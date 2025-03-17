"""
# -------------------------------------------------------------
# PYTHON FILE
# NOTE: 
#   - DO NOT EDIT sections marked as [DO NOT EDIT]
#   - Sections without this mark can be modified as needed.
# -------------------------------------------------------------

Build the training Vertex pipeline.
"""

# [CAN EDIT] - All pipeline functions

from typing import Dict

from google_cloud_pipeline_components.v1 import vertex_notification_email
from kfp import dsl

from components.load_dummy_data import load_dummy_data
from components.train_dummy_model import train_dummy_model
from components.test_dummy_model import test_dummy_model


def pipeline(
    project_config: Dict,
    training_config: Dict,
    experiment_name: str,
    job_labels: Dict,
    lineage_dict: Dict,
    git_dict: Dict,
    user_dict: Dict,
    local_path: str,
    kfp_vars: Dict = {},
):
    """
    Build pipeline using kfp components defined in core/training/components.

    Parameters
    ----------
    project_config : dict
        Config containing project specific configurations
    training_config : dict
        Config containing pipeline configurations
    experiment_name : str
        Vertex pipeline training experiment name
    job_labels : dict
        Dictionary containing user metadata for finops tracking
    lineage_dict : dict
        Dictionary containing variables required to initialise model
        lineage client. See core/training/runner.py for more information
    git_dict : dict
        Dictionary containing git related variables for model lineage.
        Currently git_repo_url, git_branch and git_commit_sha
    user_dict : dict
        Dictionary containing user related variables for model lineage.
        Currently user_email and user_uin
    local_path : str
        Local path to vertex artifacts, used to change paths and connect
        artifacts
    kfp_vars : Optional[dict], default = {}
        Optional dictionary containing kubeflow pipeline variables. Includes
        environment, credential and local run variables for running vertex
        pipelines locally

    Returns
    -------
    pipeline : object
        Vertex pipeline, built below in build_and_compile
        and triggered in core/training/runner.py

    """
    @dsl.pipeline(
        name=experiment_name,
    )
    def _pipeline():
        """
        Construct the Vertex pipeline.

        """
        notify_email_task = vertex_notification_email.VertexNotificationEmailOp(
            recipients=[project_config["owner_email"]]
        ).set_display_name("email-notification")

        with dsl.ExitHandler(
            notify_email_task,
            name="pipeline-monitor",
        ):
            exclude_columns = [
                feature
                for feature in training_config["bq"]["exclude_columns"] 
                if feature is not None
            ]
            entity_columns = [
                feature
                for feature in training_config["bq"]["entity_columns"] 
                if feature is not None
            ]

            # Create pipelile from the defined components
            load_dummy_data_component = load_dummy_data(
                project=project_config["project_id"],
                dataset_id=training_config["bq"]["dataset_id"],
                table_name=training_config["bq"]["table_name"],
                target_col=training_config["bq"]["target_col"],
                query=training_config["bq"]["query"],
                exclude_columns=exclude_columns,
                entity_columns=entity_columns,
                timestamp_column=training_config["bq"]["date_timestamp_column"],
                training_seed=training_config["training_seed"],
                job_labels=job_labels,
                lineage_dict=lineage_dict,
                kfp_vars=kfp_vars,
            )
            train_dummy_model_component = train_dummy_model(
                data_artifact=load_dummy_data_component.outputs["data_artifact"],
                target_col=training_config["bq"]["target_col"],
                exclude_columns=exclude_columns,
                training_seed=training_config["training_seed"],
                lineage_dict=lineage_dict,
                git_dict=git_dict,
                user_dict=user_dict,
                kfp_vars=kfp_vars,
            )
            test_dummy_model_component = test_dummy_model(
                data_artifact=load_dummy_data_component.outputs["data_artifact"],
                model_artifact=train_dummy_model_component.outputs["model_artifact"],
                target_col=training_config["bq"]["target_col"],
                exclude_columns=exclude_columns,
                lineage_dict=lineage_dict,
                kfp_vars=kfp_vars,
            )

    return _pipeline
