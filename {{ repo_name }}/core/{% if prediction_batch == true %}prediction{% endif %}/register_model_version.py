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
from gcp_tools_lite.utils.config_tools import TemplateConfigs
from model_lineage.clients.lineage_client import LineageClient

from model_lineage.utils.ci import get_run_id_from_commit

from gcp_tools_lite.logging_tools import configure_logger
logger = configure_logger()

exp_configs = TemplateConfigs(target_env="exp")
exp_configs.get("metadata_config").gcp_service = "infrastructure"
configs = TemplateConfigs(target_env=os.getenv("ENV","exp"))
configs.get("metadata_config").gcp_service = "infrastructure"

exp_bucket = exp_configs.get("project_config").bucket.replace("gs://", "")
target_bucket = configs.get("project_config").bucket.replace("gs://", "")


def register_model_version():
    """
    Registers a model version using the provided tag name.

    Returns:
        None

    CASE 1
    run_ids in model-lineage [run1, run2, run3]
    config.target_run_id = run1

    clone record in dev (run1) > ci-commit-tag
    """
    run_id = get_run_id_from_commit()
    run_id = run_id or configs.get("prediction_config").target_run_id

    if not run_id:
        latest_model_dict = LineageClient.fetch_latest_model_id_static(
            querier_project=configs.get("project_config").project_id,
            lineage_project=exp_configs.get("project_config").lineage_project,
            lineage_dataset=exp_configs.get("project_config").lineage_dataset,
            use_case=exp_configs.get("project_config").repo_name,
            experiment_name=exp_configs.get("project_config").experiment_name,
            model_name=exp_configs.get("project_config").experiment_name,
            model_version=exp_configs.get("project_config").model_development_version,
            job_labels=exp_configs.get("metadata_config"),
        )
        run_id = latest_model_dict["run_id"]

    dev_lineage_client = LineageClient(
        querier_project=configs.get("project_config").project_id,
        lineage_project=exp_configs.get("project_config").lineage_project,
        lineage_dataset=exp_configs.get("project_config").lineage_dataset,
        use_case=exp_configs.get("project_config").repo_name,
        experiment_name=exp_configs.get("project_config").experiment_name,
        model_name=exp_configs.get("project_config").experiment_name,
        model_version=exp_configs.get("project_config").model_development_version,
        job_labels=exp_configs.get("metadata_config"),
        run_id=run_id,
    )
    model_artifacts = dev_lineage_client.fetch_all_model_artifacts()

    lineage_client = LineageClient(
        querier_project=configs.get("project_config").project_id,
        lineage_project=configs.get("project_config").lineage_project,
        lineage_dataset=configs.get("project_config").lineage_dataset,
        use_case=configs.get("project_config").repo_name,
        experiment_name=configs.get("project_config").experiment_name,
        model_name=configs.get("project_config").experiment_name,
        model_version=os.getenv(
            "CI_COMMIT_TAG",
            configs.get("project_config").model_development_version
        ),
        job_labels=configs.get("metadata_config"),
        run_id=run_id,
    )
    lineage_client.update_model(deployment_status="deployed")

    updated_artifacts = []
    for artifact in model_artifacts:
        if artifact["artifact_name"] in updated_artifacts:
            continue
        if target_bucket not in artifact["artifact_uri"]:
            artifact_uri = artifact["artifact_uri"].replace(exp_bucket, target_bucket)
        else:
            artifact_uri = artifact["artifact_uri"]

        lineage_client.register_model_artifact(
            artifact_name=artifact["artifact_name"],
            artifact_uri=artifact_uri,
        )
        logger.info(f"Register: {artifact['artifact_name']}, {artifact_uri}")
        updated_artifacts.append(artifact["artifact_name"])

    # Temp update dataset
    query = f"""
    INSERT INTO `{lineage_client.lineage_project}.{lineage_client.lineage_dataset}.datasets` 
    SELECT 
        "{lineage_client.use_case}" AS use_case
        , "{lineage_client.experiment_name}" AS experiment_name
        , "{lineage_client.model_name}" AS model_name
        , "{lineage_client.model_version}" AS model_version
        , run_id
        , full_training_table
        , gcs_uri
        , features
        , target
        , schema
        , baseline
        , timestamp_column
        , query_date
        , min_date
        , max_date
        , is_hh360
        , exclude_columns
    FROM `{dev_lineage_client.lineage_project}.{dev_lineage_client.lineage_dataset}.datasets` 
    WHERE use_case = "{dev_lineage_client.use_case}"
      AND run_id = "{dev_lineage_client.run_id}"
      AND model_version = "{dev_lineage_client.model_version}"
    ORDER BY query_date DESC
    LIMIT 1
    """
    lineage_client.bq_client.execute_query(
        query=query,
        job_labels=lineage_client.job_labels,
        return_type=None,
    )

if __name__ == "__main__":
    register_model_version()
