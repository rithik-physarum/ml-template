"""Module for registering the monitoring configuration to the model lineage library."""

import os
from gcp_tools_lite.logging_tools import logger
from gcp_tools_lite.utils.config_tools import TemplateConfigs
from model_lineage.clients.lineage_client import LineageClient


configs = TemplateConfigs()

lineage_client = LineageClient.initialise_lineage_client(
    querier_project=configs.get("project_config").project_id,
    lineage_project=configs.get("project_config").lineage_project,
    lineage_dataset=configs.get("project_config").lineage_dataset,
    use_case=configs.get("project_config").repo_name,
    experiment_name=configs.get("project_config").experiment_name,
    model_version=os.getenv(
        "CI_COMMIT_TAG", configs.get("project_config").model_development_version
    ),
    job_labels=configs.get("metadata_config").toDict(),
    target_run_id=configs.get("prediction_config").target_run_id,
)

monitoring_config = configs.get("monitoring_config").toDict()
logger.debug(f"Monitoring_config:{monitoring_config}")

lineage_client.register_parameter(
    parameter_name="monitoring_config",
    parameter_value=monitoring_config,
)
logger.info("Monitoring configuration registered in the model lineage library")
