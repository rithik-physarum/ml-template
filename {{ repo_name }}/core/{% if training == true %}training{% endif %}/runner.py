"""
# -------------------------------------------------------------
# PYTHON File
# NOTE: 
#   - DO NOT EDIT sections marked as [DO NOT EDIT]
#   - Sections without this mark can be modified as needed.
# -------------------------------------------------------------

Run the training Vertex pipeline.

This script sets up and runs a Vertex AI pipeline using configurations loaded from
environment variables and project-specific settings. The pipeline is built with
parameters such as user and Git details, lineage, and experiment configurations.

Modules Used
------------
- gcp_tools_lite.utils.config_tools.TemplateConfigs: For getting the config data.
- gcp_tools_lite.utils.time.timestamp: To get the current timestamp.
- gcp_tools_lite.data_tools.kfp.utils.args.get_parsed_args: For parsing pipeline run arguments.
- gcp_tools_lite.data_tools.kfp_tools.KFPPipelineRunner: To run the Vertex pipeline.
- gcp_tools_lite.data_tools.kfp.utils.pipeline.get_pipeline: To retrieve the Vertex pipeline instance.
- gcp_tools_lite.data_tools.kfp.utils.vars: For getting Git, user, and KFP variables.

Example
-------
To run the pipeline from the command line:
    python runner.py
"""

# [DO NOT EDIT]

import os

from gcp_tools_lite.utils.config_tools import TemplateConfigs
from gcp_tools_lite.utils.time import timestamp
from gcp_tools_lite.data_tools.kfp.utils.args import get_parsed_args
from gcp_tools_lite.data_tools.kfp_tools import KFPPipelineRunner
from gcp_tools_lite.data_tools.kfp.utils.pipeline import get_pipeline
from gcp_tools_lite.data_tools.kfp.utils.vars import (
    get_git_variables,
    get_user_variables,
    get_kfp_variables,
)

# Loading the environment variables
configs = TemplateConfigs()
configs.get("metadata_config").gcp_service = "vertex_pipeline"

if __name__ == "__main__":
    args = get_parsed_args()
    git_dict = get_git_variables(default="local_run")
    user_dict = get_user_variables(
        default_email=configs.get("project_config").owner_email,
        default_uin=configs.get("metadata_config").user_uin,
    )
    kfp_vars = get_kfp_variables(local_run=args.local, docker_run=args.docker)

    for experiment_name, run_choice in configs.get("training_experiments").items():
        run_id = f"{experiment_name}-{timestamp()}"
        lineage_dict = {
            "querier_project": configs.get("project_config").project_id,
            "lineage_project": configs.get("project_config").lineage_project,
            "lineage_dataset": configs.get("project_config").lineage_dataset,
            "use_case": configs.get("project_config").repo_name,
            "experiment_name": experiment_name,
            "model_name": experiment_name,
            "model_version": configs.get("project_config").model_development_version,
            "run_id": run_id,
            "job_labels": configs.get("metadata_config").toDict(),
        }

        pipeline = get_pipeline(
            project_config=configs.get("project_config").toDict(),
            training_config=configs.get("training_config").toDict(),
            experiment_name=experiment_name,
            job_labels=configs.get("metadata_config").toDict(),
            lineage_dict=lineage_dict,
            git_dict=git_dict,
            user_dict=user_dict,
            kfp_vars=kfp_vars,
            local_path=os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 
                "local_outputs"
            ),
        )

        KFPPipelineRunner(
            local=kfp_vars["local_run"],
            pipeline=pipeline,
            project_config=configs.get("project_config").toDict(),
            training_config=configs.get("training_config").toDict(),
            vertex_config=configs.get("vertex_config").toDict(),
            job_labels=configs.get("metadata_config").toDict(),
            experiment_name=experiment_name,
            local_runner_type=kfp_vars["runner_type"],
            output_location=os.path.dirname(os.path.abspath(__file__)),
        ).run(run_id=run_id)
