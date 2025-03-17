"""
# -------------------------------------------------------------
# PYTHON File
# NOTE: 
#   - DO NOT EDIT sections marked as [DO NOT EDIT]
#   - Sections without this mark can be modified as needed.
# -------------------------------------------------------------

Build the Dataflow Beam pipeline.

EXAMPLE WRITE TO UNICA EXTERNAL TABLE - please follow this example

https://cloud.google.com/bigquery/docs/external-data-cloud-storage

CREATE OR REPLACE EXTERNAL TABLE `your_project.your_dataset.your_table`
(
  MODEL_ID STRING,
  BRAND STRING,
  KEY_TYPE STRING,
  KEY_VALUE INT64,
  MODEL_OUTPUT INT64,
  MODEL_OUTPUT_TYPE STRING,
  CREATE_DATE DATE,
  STALE_DATE DATE
)
OPTIONS (
  format = 'CSV',
  uris = ['gs://ds-capability/unica-model-scores/landing/your_model_name/*.csv']
);
"""

# [CAN EDIT] - ALL

import os
from datetime import date
from typing import Dict

import numpy as np
import apache_beam as beam
from apache_beam.io.parquetio import WriteToParquet
from apache_beam.io.gcp.internal.clients import bigquery
from apache_beam.options.pipeline_options import PipelineOptions

from gcp_tools_lite.utils.io import get_pyarrow_schema
from gcp_tools_lite.utils.time import timestamp

from model_lineage.utils.ci import get_artifact_uri
from gcp_tools_lite.utils.io import get_artifact

from .transformers import predict_transformers, transformers

def build_beam_pipeline(
    project_config: Dict,
    prediction_config: Dict,
    training_config: Dict,
    model_artifacts: list[dict],
    artifact_location: str,
    pipeline_options: PipelineOptions = None,
):
    """
    Build the beam pipeline with both UNICA and Pega outputs.

    Parameters
    ----------
    project_config : Dict
        Project configurations
    prediction_config : Dict
        Prediction pipeline configs
    model_artifacts : list[dict]
        List of model artifact dictionaries
    artifact_location : str
        GCS artifact location for prediction
    pipeline_options : PipelineOptions
        Options for beam pipeline
    """
    gcs_config = prediction_config["gcs"]
    unica_config = gcs_config["unica"]
    pega_config = gcs_config["pega"]
    bq_config = prediction_config["bq"]

    # Prepare artifact URI and feature list
    artifact_uri = get_artifact_uri(
        model_artifacts=model_artifacts, 
        artifact_name="model_object"
    )
    _model = get_artifact(artifact_uri)
    feature_list = _model.feature_names_in_.tolist()
    num_feature_list = _model["preprocessor"].transformers[1][2]
    entity_list = training_config["bq"]["entity_columns"]
    reference_list = entity_list + feature_list

    # UNICA GCS output settings
    unica_gcs_file_path = os.path.join(
        project_config["bucket"],
        unica_config["landing_dir"],
        project_config['repo_name'],
        unica_config["gcp_edw_unica_str"]+project_config["repo_name"].upper()
    )
    unica_gcs_sink = beam.io.WriteToText(
        file_path_prefix=unica_gcs_file_path,
        file_name_suffix=f"_{str(date.today()).replace('-','')}.csv",
        header=','.join(bq_config['output_table_header']),
        max_bytes_per_shard=gcs_config["max_bytes_per_shard"],
        append_trailing_newlines=True,
        shard_name_template=gcs_config["shard_name_template"],
    )

    # Pega GCS output settings
    # Get the dynamic timestamp for prediction datetime
    score_datetime = timestamp(format="timestamp")
    expiry_timestamp = timestamp(
        add_days=180,
        format="timestamp"
    )

    pega_schema = get_pyarrow_schema(
        schema_str=pega_config["output_table_schema"]
    )
    pega_gcs_file_path = os.path.join(
        project_config["bucket"],
        pega_config["pega_model_scores_landing"],
        f"{pega_config['partition_col_model_name']}={project_config['repo_name'].upper()}",
        f"{pega_config['partition_col_score_dtm']}={score_datetime}",
        pega_config["predictions_prefix"]
    )
    pega_gcs_sink = WriteToParquet(
        file_path_prefix=pega_gcs_file_path,
        file_name_suffix=".parquet",
        schema=pega_schema
    )

    # Define the Predict and Pega Conversion transformers
    predict_transformer = beam.ParDo(
        predict_transformers.PredictTransformer(
            repo_name=project_config['repo_name'],
            artifact_uri=artifact_uri,
            entity_list=entity_list,
            num_feature_list=num_feature_list,
            reference_list=reference_list,
            brand=unica_config['brand'],
            key_type=unica_config['key_type'],
            output_type=unica_config['output_type'],
        )
    )

    # Data source - reading data from BQ
    source = beam.io.gcp.bigquery.ReadFromBigQuery(
        query=bq_config["query"],
        use_standard_sql=True,
        temp_dataset=bigquery.DatasetReference(
            projectId=project_config["project_id"],
            datasetId=bq_config["temp_dataset"],
        ),
    )
    
    # BQ data sink, create or append table to save to
    bq_sink = beam.io.gcp.bigquery.WriteToBigQuery(
        table=bq_config["output_table"],
        schema=bq_config["output_table_schema"],
        create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
        write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
        additional_bq_parameters={'timePartitioning': {'type': 'DAY', 'field': f"{bq_config['output_table_partition_col']}"}}
    )

    with beam.Pipeline(options=pipeline_options) as p:

        # Get data from bigquery
        data = p | "Read data from source" >> source

        # Transformations
        transformed_data = data | "Convert dict to list" >> beam.Map(
            transformers.convert_dict_to_list, reference=reference_list
        )
        batched_data = transformed_data | "Batching" >> beam.transforms.util.BatchElements(
            min_batch_size=prediction_config.get("batch_size", 1),
            max_batch_size=prediction_config.get("batch_size", 1)
        )
        batched_numpy = batched_data | "Convert to NumPy" >> beam.Map(np.array)

        # Apply prediction
        predictions = batched_numpy | "Get prediction" >> predict_transformer

        # UNICA Output
        csv_predictions = predictions | "Format as CSV for UNICA" >> beam.FlatMap(
            transformers.array_to_string,
            entity_size=len(entity_list)
        )
        csv_predictions | "Write to UNICA GCS" >> unica_gcs_sink

        # Pega Output
        pega_predictions = predictions | "Convert to PEGA schema" >> beam.FlatMap(
            transformers.array_to_dicts,
            timestamp=expiry_timestamp,
            output_type=pega_config['output_type'],
            output_desc=pega_config['output_desc'],
        )
        pega_predictions | "Write to Pega GCS" >> pega_gcs_sink
        
        # BQ Output
        bq_predictions = predictions | "Convert to bq schema" >> beam.FlatMap(
            transformers.convert_to_bq_dicts,
            timestamp=score_datetime,
        )
        bq_predictions | "Write to Bq" >> bq_sink
