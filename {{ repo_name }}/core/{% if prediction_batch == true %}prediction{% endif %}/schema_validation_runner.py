"""
# -------------------------------------------------------------
# PYTHON File
# NOTE: 
#   - DO NOT EDIT sections marked as [DO NOT EDIT]
#   - Sections without this mark can be modified as needed.
# -------------------------------------------------------------
"""

# [DO NOT EDIT]

import os
import json
from uuid import uuid4

from gcp_tools_lite.data_tools.beam_tools import BeamPipelineRunner
from gcp_tools_lite.utils import project
from gcp_tools_lite.utils.config_tools import TemplateConfigs
from gcp_tools_lite.logging_tools import logger
from gcp_tools_lite.utils.sql import update_query_limit

from model_lineage.utils.ci import get_run_id_from_commit
from model_lineage.clients.lineage_client import LineageClient

runner_type = "TemplateRunner"

# Get Schema Validation Params
configs = TemplateConfigs()
configs.get("metadata_config").gcp_service = "dataflow_pipeline"
job_labels_list = [
    f"{key}={value}" for key, value in configs.get("metadata_config").items()
]

project_number = project.get_project_number(configs.get("project_config").project_id)

query = update_query_limit(query=configs.get("prediction_config").bq.query)
exclude_columns = configs.get("training_config").bq.exclude_columns
exclude_columns.append(configs.get("training_config").bq.target_col)
comma_separated_columns = ",".join(
    column for column in exclude_columns if column is not None
)

run_id = get_run_id_from_commit() #Use existing method in model lineage 
run_id = run_id or configs.get("prediction_config").target_run_id

if not run_id:
    latest_model_dict = LineageClient.fetch_latest_model_id_static(
        querier_project=configs.get("project_config").project_id,
        job_labels=configs.get("metadata_config"),
        use_case=configs.get("project_config").repo_name,
        experiment_name=configs.get("project_config").experiment_name,
        model_version=os.getenv(
            "CI_COMMIT_TAG", configs.get("project_config").model_development_version
        ),
        lineage_project=configs.get("project_config").lineage_project,
        lineage_dataset=configs.get("project_config").lineage_dataset,
    )
    run_id = latest_model_dict["run_id"]

job_name = (
    f"{configs.get('project_config').experiment_name}-schema-validation-{uuid4()}"
)

schema_validation_params = {
    "query": query,
    "use_case": configs.get("project_config").repo_name,
    "experiment_name": configs.get("project_config").experiment_name,
    "model_name": configs.get("project_config").experiment_name,
    "model_version": os.getenv(
        "CI_COMMIT_TAG", configs.get("project_config").model_development_version
    ),
    "run_id": run_id,
    "exclude_columns": comma_separated_columns,
    "entity_columns": json.dumps(configs.get("training_config").bq.entity_columns),
    "job_labels": json.dumps(configs.get("metadata_config").toDict()),
    "lineage_project": configs.get("project_config").lineage_project,
    "lineage_dataset": configs.get("project_config").lineage_dataset,
}

# Run beam pipeline
runner = BeamPipelineRunner(
    runner_type=runner_type,
    template_location=configs.get(
        "orchestration_config"
    ).schema_validation.schema_validation_template_url,
    service_account_email=configs.get("project_config").dataflow_service_account,
    project_id=configs.get("project_config").project_id,
    region=configs.get("project_config").region,
)
job_id = runner.run(
    run_id=job_name,
    job_params=schema_validation_params,
)
logger.info(f"job id: {job_id}")
