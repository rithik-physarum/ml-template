"""
# -------------------------------------------------------------
# PYTHON File
# NOTE: 
#   - DO NOT EDIT sections marked as [DO NOT EDIT]
#   - Sections without this mark can be modified as needed.
# -------------------------------------------------------------

Load dummy data.

Loading dummy data from a BigQuery table and saving it
as a parquet in Google Cloud Storage.
"""

# [CAN EDIT] - ALL

import os

from kfp.v2.dsl import component, Dataset, Output
from runner import configs


@component(
    base_image=configs.get("vertex_config").base_image,
    install_kfp_package=False,
)
def load_dummy_data(
    project: str,
    dataset_id: str,
    table_name: str,
    target_col: str,
    query: str,
    exclude_columns: list,
    entity_columns: list,
    timestamp_column: str,
    training_seed: int,
    job_labels: dict,
    lineage_dict: dict,
    kfp_vars: dict,
    data_artifact: Output[Dataset],
):
    """
    Read model table from BigQuery and save the data off as parquets
    to Google Cloud Storage to be loaded into future pipeline components.

    Parameters
    ----------
    project : str
        The GCP project name
    dataset_id : str
        BQ dataset name
    table_name : str
        BQ table name
    target_col : str
        Target column name
    query : str
        The SQL query to load the model table
    exclude_columns : list
        List of columns to exclude from model lineage schema validation
    timestamp_columns : str
        Name of training dataset timestamp column
    job_labels : dict
        Dictionary containing user metadata for finops tracking
    lineage_dict : dict
        Dictionary for initialising model-lineage LineageClient
    kfp_vars : dict
        Dictionary containing kubeflow pipeline variables. Includes
        environment, credential and local run variables for running
        vertex pipelines locally

    Outputs
    -------
    data_artifact : vertex object
        Object containing attribute path, the local
        gcs path to save/load data

    """
    from gcp_tools_lite.data_tools.kfp.utils.vars import init_kfp_variables
    local_run = init_kfp_variables(kfp_vars=kfp_vars)
    from gcp_tools_lite.data_tools.bigquery_tools import Querier
    from gcp_tools_lite.data_tools.storage_tools_v2 import StorageHelperV2
    from gcp_tools_lite import logging_tools
    from model_lineage.clients.lineage_client import LineageClient

    io = StorageHelperV2()
    bq = Querier(querier_project=project)

    logger = logging_tools.configure_logger()
    logger.info(lineage_dict)

    data = bq.execute_query(
        query=query,
        job_labels=job_labels,
        return_type="df",
    )
    train = data.sample(frac=0.8, random_state=training_seed)
    test = data.drop(train.index)

    io.save(
        data=train,
        path=data_artifact.path.replace("_artifact", "_train.parquet"),
    )
    io.save(
        data=test,
        path=data_artifact.path.replace("_artifact", "_test.parquet"),
    )

    if not local_run:
        lineage_client = LineageClient(
            **lineage_dict,
        )
        exclude_columns.append(target_col)
        if entity_columns:
            exclude_columns += entity_columns
        # We must push dataset baseline to model-lineage for monitoring

        lineage_client.register_training_dataset(
            training_project=project,
            training_dataset_id=dataset_id,
            training_table_name=table_name,
            target_col=target_col,
            training_query=query,
            timestamp_column=timestamp_column,
            exclude_columns=list(set(exclude_columns)),
        )
        lineage_client.register_model_artifact(
            artifact_name="train_data",
            artifact_uri=data_artifact.path.replace("_artifact", "_train.parquet"),
        )
        lineage_client.register_model_artifact(
            artifact_name="test_data",
            artifact_uri=data_artifact.path.replace("_artifact", "_test.parquet"),
        )