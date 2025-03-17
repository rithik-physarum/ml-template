"""
# -------------------------------------------------------------
# PYTHON File
# NOTE: 
#   - DO NOT EDIT sections marked as [DO NOT EDIT]
#   - Sections without this mark can be modified as needed.
# -------------------------------------------------------------

Run the Dataflow Beam prediction workflow.

This script orchestrates a Beam pipeline execution on Google Cloud Dataflow, with options to
run locally, in Docker, as a Dataflow template, or directly in Dataflow. It utilizes configuration 
settings and arguments to define the job's environment, entrypoint, lineage, and runtime options.

Modules Used
------------
- argparse: To parse command-line arguments.
- os: For managing paths and environment variables.
- uuid4: To generate unique job IDs for Dataflow runs.
- gcp_tools_lite.data_tools.beam_tools.BeamPipelineRunner: Manages the execution of the Beam pipeline.
- gcp_tools_lite.utils.project: Utility for project-related metadata retrieval.
- gcp_tools_lite.utils.config_tools.TemplateConfigs: Handles configuration loading.
- gcp_tools_lite.logging_tools.logger: For logging job-related information.
- model_lineage.LineageCient: For initialisising the model lineage client

Command-line Arguments
----------------------
- `--local`: Set to True to run locally using DirectRunner.
- `--docker`: Set to True to run locally using Docker.
- `--run-template`: Set to True to run an existing Dataflow template.
- `--generate-template`: Set to True to generate a reusable Dataflow template without running it.
- `--job-name`: Optional; specifies the name of the Dataflow job. If not provided, a unique job name is generated.

Environment Variables
---------------------
The script uses environment variables for proxy settings and Google Cloud project ID:
- "http_proxy", "https_proxy": Proxy settings.
- "HTTP_PROXY", "HTTPS_PROXY": Proxy settings.
- "GOOGLE_CLOUD_PROJECT": The Google Cloud project ID.

Example
-------
To run the pipeline from the command line:
    python runner.py --local 
    python runner.py --run-template 
    python runner.py --generate-template 
    python runner.py --docker 

"""

# [DO NOT EDIT]

import argparse
import os
from uuid import uuid4

from gcp_tools_lite.data_tools.beam_tools import BeamPipelineRunner
from gcp_tools_lite.utils import project
from gcp_tools_lite.utils.config_tools import TemplateConfigs
from gcp_tools_lite.logging_tools import logger

from dataflow.beam_pipeline import build_beam_pipeline
from model_lineage.clients.lineage_client import LineageClient

parser = argparse.ArgumentParser("Dataflow beam prediction workflow")

parser.add_argument(
    "--local",
    type=bool,
    default=False,
    nargs="?",
    const=True,
    help="Set to true to run locally, do not use when running CI/CD",
)
parser.add_argument(
    "--docker",
    type=bool,
    default=False,
    nargs="?",
    const=True,
    help="Set to true to run docker locally, do not use when running CI/CD",
)
parser.add_argument(
    "--run-template",
    type=bool,
    default=False,
    nargs="?",
    const=True,
    help="Set to true to run template on dataflow, do not use when running CI/CD",
)
parser.add_argument(
    "--generate-template",
    type=bool,
    default=False,
    nargs="?",
    const=True,
    help="Set to true to generate a reusable dataflow template without run",
)

parser.add_argument(
    "--job-name",
    required=False,
    default=None,
    help="Dataflow job name",
    type=str,
)

args = parser.parse_args()


configs = TemplateConfigs()
configs.get("metadata_config").gcp_service = "dataflow_pipeline"
job_labels_list = [
    f"{key}={value}" for key, value in configs.get("metadata_config").items()
]

project_number = project.get_project_number(configs.get("project_config").project_id)

if args.docker:
    runner_type = "DockerRunner"
elif args.local:
    runner_type = "DirectRunner"
elif args.run_template:
    runner_type = "TemplateRunner"
else:
    runner_type = "DataflowRunner"
if args.job_name is None:
    args.job_name = f"{configs.get('dataflow_config').job_name}-{uuid4()}"

entrypoint = "python /home/prediction/runner.py --local"
root_path = os.path.dirname(os.path.dirname(configs.config_dir))
volumes = {
    "/root/.config/gcloud": "/root/.config/gcloud",
    os.path.join(root_path, "config"): "/home/config",
    os.path.join(root_path, "prediction"): "/home/prediction",
}

# use model lineage class method to initialise Lineage
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

model_artifacts = lineage_client.fetch_all_model_artifacts()
gcs_location = os.path.join(
    configs.get("project_config").bucket,
    configs.get("project_config").repo_name,
    project_number,
    configs.get("project_config").experiment_name,
    configs.get("prediction_config").gcs.dataflow_dir,
)
template_location = os.path.join(
    gcs_location, f"template/{configs.get('project_config').experiment_name}-prediction"
)
build_pipeline_kwargs = dict(
    project_config=configs.get("project_config").toDict(),
    prediction_config=configs.get("prediction_config").toDict(),
    training_config=configs.get("training_config").toDict(),
    model_artifacts=model_artifacts,
    artifact_location=gcs_location,
)
envs = {
    "http_proxy": "http://clientproxy.nat.bt.com:8080",
    "https_proxy": "http://clientproxy.nat.bt.com:8080",
    "HTTP_PROXY": "http://clientproxy.nat.bt.com:8080",
    "HTTPS_PROXY": "http://clientproxy.nat.bt.com:8080",
    "GOOGLE_CLOUD_PROJECT": configs.get("project_config").project_id,
}

runner = BeamPipelineRunner(
    runner_type=runner_type,
    # Direct Runner & DataflowRunner
    gcs_location=gcs_location,
    # Docker Runner & DataflowRunner
    docker_image=configs.get("dataflow_config").sdk_container_image,
    # Template Runner & DataflowRunner
    template_location=template_location,
    service_account_email=configs.get("project_config").dataflow_service_account,
    project_id=configs.get("project_config").project_id,
    region=configs.get("project_config").region,
    # DataflowRunner
    pipeline_kwargs=configs.get("dataflow_config").toDict(),
)
job_id = runner.run(
    # DataflowRunner
    template_only=args.generate_template,
    # Direct Runner & DataflowRunner
    build_pipeline_fn=build_beam_pipeline,
    build_pipeline_kwargs=build_pipeline_kwargs,
    # Template Runner & DataflowRunner
    run_id=args.job_name,
    job_params=None,
    # Docker Runner
    entrypoint=entrypoint,
    volumes=volumes,
    envs=envs,
    auto_remove=True,
)
logger.info(f"job id: {job_id}")
