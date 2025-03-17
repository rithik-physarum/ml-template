import os
import yaml  # Import PyYAML
from gcp_tools_lite.api import StorageHelperV2
from gcp_tools_lite.logging_tools import configure_logger
from gcp_tools_lite.utils.config_tools import TemplateConfigs
from model_lineage.clients.lineage_client import LineageClient

# Configure logger
_logger = configure_logger()

# Load configurations
configs = TemplateConfigs()
configs.get("metadata_config").gcp_service = "notebook"

# Initialize Lineage client
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
    target_run_id=configs.get("prediction_aws_config").model_config["target_run_id"],
)

# Fetch all model artifacts
model_artifacts = lineage_client.fetch_all_model_artifacts()

# Initialize GCS StorageHelperV2
storage_helper = StorageHelperV2(
    location=configs.get("project_config").region,
    project=configs.get("project_config").project_id,
)

# Local destination path for models
local_destination_root = os.getenv('ARTIFACT_LOCATION', '/home/artifacts')
os.makedirs(local_destination_root, exist_ok=True)

# Dictionary to store artifact names and their local paths
artifacts_info = {}

# Download each artifact
for artifact in model_artifacts:
    artifact_name = artifact.get("artifact_name")
    artifact_uri = artifact.get("artifact_uri")
    if not artifact_name or not artifact_uri:
        _logger.warning(f"Skipping artifact with incomplete information: {artifact}")
        continue

    # Create subdirectory for the artifact and define local path
    artifact_directory = os.path.join(local_destination_root, artifact_name)
    if not os.path.exists(artifact_directory):
        os.makedirs(artifact_directory)
    local_file_path = os.path.join(artifact_directory, os.path.basename(artifact_uri))

    try:
        storage_helper.copy(artifact_uri, local_file_path)
        _logger.info(f"Downloaded {artifact_name} to {local_file_path}")
        artifacts_info[artifact_name] = local_file_path
    except Exception as e:
        _logger.error(f"Failed to download artifact {artifact_name}: {e}")

# Generate YAML file with artifact details
output_yaml_path = os.path.join(local_destination_root, "artifacts_info.yaml")
try:
    with open(output_yaml_path, "w") as yaml_file:
        yaml.dump(artifacts_info, yaml_file, default_flow_style=False)
    _logger.info(f"Artifacts information saved to {output_yaml_path}")
    print(f"artifacts_info:{artifacts_info}")
except Exception as e:
    _logger.error(f"Failed to write artifacts information to YAML: {e}")
    