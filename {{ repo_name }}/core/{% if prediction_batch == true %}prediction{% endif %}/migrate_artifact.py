"""
# -------------------------------------------------------------
# PYTHON File
# NOTE: 
#   - DO NOT EDIT sections marked as [DO NOT EDIT]
#   - Sections without this mark can be modified as needed.
# -------------------------------------------------------------

Migrate experimental artifacts to production environment.
"""

# [CAN EDIT] - ALL TO MIGRATE ARTIFACTS

import os

from gcp_tools_lite.data_tools.storage_tools import StorageHelper
from gcp_tools_lite.utils.config_tools import TemplateConfigs
from gcp_tools_lite.api import logger

from model_lineage.clients.lineage_client import LineageClient

gcs_helper = StorageHelper()
exp_configs = TemplateConfigs(target_env="exp")
prod_configs = TemplateConfigs(target_env="prod")

exp_bucket = exp_configs.get("project_config").bucket.replace("gs://", "")
prod_bucket = prod_configs.get("project_config").bucket.replace("gs://", "")

exp_configs.get("metadata_config").gcp_service = "dataflow_pipeline"
job_labels = exp_configs.get("metadata_config")

lineage_client = LineageClient.initialise_lineage_client(
    querier_project=exp_configs.get("project_config").project_id,
    lineage_project=exp_configs.get("project_config").lineage_project,
    lineage_dataset=exp_configs.get("project_config").lineage_dataset,
    use_case=exp_configs.get("project_config").repo_name,
    experiment_name=exp_configs.get("project_config").experiment_name,
    model_version=exp_configs.get("project_config").model_development_version,
    job_labels=job_labels,
    target_run_id=exp_configs.get("prediction_config").target_run_id,
)

model_artifacts = lineage_client.fetch_all_model_artifacts()

updated_artifacts = []
model_artifact_uris = []
for artifact in model_artifacts:
    if artifact["artifact_name"] in updated_artifacts:
        continue
    if prod_configs.get("project_config").bucket + "/" in artifact["artifact_uri"]:
        logger.info(f"already in prod bucket: {artifact['artifact_uri']}")
    elif exp_configs.get("project_config").bucket + "/" in artifact["artifact_uri"]:
        logger.info(f"pending to move to prod bucket: {artifact['artifact_uri']}")
        model_artifact_uris.append(
            artifact["artifact_uri"].replace(
                exp_configs.get("project_config").bucket + "/", ""
            )
        )
    updated_artifacts.append(artifact["artifact_name"])

for model_artifact_uri in model_artifact_uris:
    gcs_helper.copy_blob(
        bucket_name=exp_bucket,
        blob_name=model_artifact_uri,
        destination_bucket_name=prod_bucket,
        destination_blob_name=model_artifact_uri,
    )
    logger.info(f"Copying artifact: {model_artifact_uri}")
logger.info(f"Finished copying")
