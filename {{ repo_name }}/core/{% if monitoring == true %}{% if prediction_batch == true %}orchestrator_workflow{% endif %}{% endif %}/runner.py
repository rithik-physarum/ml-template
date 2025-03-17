"""
# -------------------------------------------------------------
# PYTHON SCRIPT
# NOTE: 
#   - DO NOT EDIT sections marked as [DO NOT EDIT]
#   - Sections without this mark can be modified as needed.
# -------------------------------------------------------------
"""

# [DO NOT EDIT]

import os
import re
import json
import argparse
from gcp_tools_lite.utils.config_tools import TemplateConfigs
from gcp_tools_lite.data_tools.pubsub_tools import PubsubHelper
from gcp_tools_lite.data_tools.workflow_tools import WorkflowHelper
from gcp_tools_lite.utils.project import get_project_number

from gcp_tools_lite.utils.sql import update_query_limit

from model_lineage.clients.lineage_client import LineageClient
from model_lineage.utils.ci import get_run_id_from_commit


def generate_workflow(
    configs,
    workflow_template_path: str,
    workflow_save_path: str,
) -> str:
    """
    Generates and saves the workflow script by updating the template with configurations.

    Parameters
    ----------
    configs : TemplateConfigs
        Configuration data for the workflow.
    workflow_template_path : str
        Path to the workflow template file.
    workflow_save_path : str
        Path to save the generated workflow.

    Returns
    -------
    str
        Path to the saved workflow file.

    """
    with open(workflow_template_path, "r") as file:
        workflow_script = file.read()

    # Update Workflow Parameters
    _metadata_config = configs.get("metadata_config").toDict()
    _metadata_config["gcp_service"] = "dataflow_pipeline"

    query = update_query_limit(query=configs.get("prediction_config").bq.query)
    exclude_columns = configs.get("training_config").bq.exclude_columns
    exclude_columns.append(configs.get("training_config").bq.target_col)
    comma_separated_columns = ",".join(
        column for column in exclude_columns if column is not None
    )
    if not configs.get("training_config").bq.entity_columns:
        raise RuntimeError(
            "training_config, entity_columns is empty, duplicate checking will be failed."
        )

    run_id = get_run_id_from_commit()
    run_id = run_id or configs.get("prediction_config").target_run_id

    if not run_id:
        latest_model_dict = LineageClient.fetch_latest_model_id_static(
            querier_project=configs.get("project_config").project_id,
            job_labels=_metadata_config,
            use_case=configs.get("project_config").repo_name,
            experiment_name=configs.get("project_config").experiment_name,
            model_version=os.getenv(
                "CI_COMMIT_TAG", configs.get("project_config").model_development_version
            ),
            lineage_project=configs.get("project_config").lineage_project,
            lineage_dataset=configs.get("project_config").lineage_dataset,
        )
        run_id = latest_model_dict["run_id"]

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
        "job_labels": json.dumps(_metadata_config),
        "lineage_project": configs.get("project_config").lineage_project,
        "lineage_dataset": configs.get("project_config").lineage_dataset,
    }

    _project_number = get_project_number(configs.get("project_config").project_id)
    _prediction_pipeline_url = os.path.join(
        configs.get("project_config").bucket,
        configs.get("project_config").repo_name,
        str(_project_number),
        configs.get("project_config").experiment_name,
        configs.get("prediction_config").gcs.dataflow_dir,
        "template",
        f"{configs.get('project_config').experiment_name}-prediction",
    )
    print(
        "Schema Validation URL",
        configs.get(
            "orchestration_config"
        ).schema_validation.schema_validation_template_url,
    )
    print("Prediction URL", _prediction_pipeline_url)

    _model_config = {
        "project_id": configs.get("project_config").project_id,
        "model_version": configs.get("project_config").model_development_version,
        "job_labels": _metadata_config,
        "use_case": configs.get("metadata_config").use_case,
        "lineage_project": configs.get("project_config").lineage_project,
        "lineage_dataset": configs.get("project_config").lineage_dataset,
    }

    monitoring_config = configs.get("monitoring_config").toDict()
    _workflow_name = monitoring_config.get("dataproc_workflow_name")
    _cluster = monitoring_config.get("cluster_name")
    _loader_class_args = monitoring_config.get("loader_class_args")
    _loader_class_args_sep = monitoring_config.get("loader_class_args_sep")

    # Replace placeholders in the workflow script
    replacements = {
        "@static_params.region": json.dumps(configs.get("project_config").region),
        "@static_params.schema_validation_params": json.dumps(schema_validation_params),
        "@static_params.monitoring_workflow_params": json.dumps(
            configs.get("orchestration_config").monitoring_workflow_params
        ),
        "@static_params.repo_name": configs.get("project_config").repo_name,
        "@static_params.experiment_name": configs.get("project_config").experiment_name,
        "@static_params.prediction_pipeline_params": json.dumps(
            configs.get("orchestration_config").prediction_pipeline_params
        ),
        "@static_params.drift_threshold_params": json.dumps(
            configs.get("orchestration_config").alert_threshold
        ),
        "@static_params.monitoring_drift_table": configs.get(
            "orchestration_config"
        ).monitoring_drift_table,
        "@static_params.date_column": configs.get(
            "training_config"
        ).bq.date_timestamp_column,
        "@static_params.schema_validation_template_url": configs.get(
            "orchestration_config"
        ).schema_validation.schema_validation_template_url,
        "@static_params.prediction_pipeline_url": _prediction_pipeline_url,
        "@static_params.monitoring_workflow_name": _workflow_name,
        "@static_params.cluster_name": _cluster,
        "@static_params.loader_class_args": _loader_class_args,
        "@static_params.loader_class_arg_sep": _loader_class_args_sep,
    }
    for placeholder, value in replacements.items():
        workflow_script = workflow_script.replace(placeholder, value)

    # Save the updated workflow script
    with open(workflow_save_path, "w") as file:
        file.write(workflow_script)

    print(f"Workflow saved to {workflow_save_path}")


def deploy_workflow(
    configs,
    workflow_helper,
    workflow_save_path: str,
):
    """
    Deploys the workflow by generating the workflow script and deploying it.

    Parameters
    ----------
    configs : TemplateConfigs
        Configuration data for the workflow.
    workflow_helper : WorkflowHelper
        Helper to deploy the workflow.
    workflow_save_path : str
        Path to the workflow YAML file to be deployed.

    """
    if os.getenv("CI_COMMIT_REF_NAME"):
        print("Starting workflow deployment...")
        workflow_helper.deploy_workflow(
            workflow_name=configs.get("orchestration_config").workflow_name,
            workflow_yaml_path=workflow_save_path,
        )
        print("Workflow deployed successfully.")

        # Create the Pub/Sub subscription
        create_pubsub_subscription(configs)
    else:
        print(
            "Warning: Deployment from a local environment is not allowed. Deployment is restricted to CI/CD environments."
        )


def execute_workflow(
    configs,
    workflow_helper,
    execution_params: dict = {},
):
    """
    Executes the workflow.

    Parameters
    ----------
    configs : TemplateConfigs
        Configuration data for the workflow.
    workflow_helper : WorkflowHelper
        Helper to execute the workflow.
    execution_params : dict, optional
        Parameters to pass to the execution. Defaults to {}.

    """
    execution_data = json.dumps(
        {
            "project_id": configs.get("project_config").project_id,
            "poll_wait_time_seconds": "10",
            "location": configs.get("project_config").region,
            "execution_params": execution_params,
        }
    )
    print("Executing the workflow...")
    execution_response = workflow_helper.execute_workflow(
        workflow_name=configs.get("orchestration_config").workflow_name,
        data=execution_data,
        is_orch_wait=False,
    )
    print(f"Workflow executed successfully: {execution_response.name}")


def create_pubsub_subscription(configs):
    """
    Creates a Pub/Sub subscription using the PubsubHelper.

    Parameters
    ----------
    configs : dict
        Configuration dictionary containing the following keys:
        - orchestration_config (dict): Configuration related to orchestration.
        - project_config (dict): General project configuration.

    """
    helper = PubsubHelper(
        project_id=configs.get("project_config").project_id,
        location=configs.get("project_config").region,
    )

    push_endpoint = (
        "https://workflowexecutions.googleapis.com/v1/projects/"
        f"{configs.get('project_config').project_id}/locations/"
        f"{configs.get('project_config').region}/workflows/"
        f"{configs.get('orchestration_config').workflow_name}:triggerPubsubExecution"
        "?__GCP_CloudEventsMode=CUSTOM_PUBSUB_projects%2F"
        f"{configs.get('project_config').project_id}%2Ftopics%2F"
        f"{configs.get('orchestration_config').topic}"
    )
    labels = {"use_case": configs.get("project_config").experiment_name}

    # Create the subscription with the necessary parameters
    helper.create_subscription(
        topic_name=configs.get("orchestration_config").topic,
        subscription_name=f"trigger-{configs.get('project_config').experiment_name}-orchestrator",
        override=True,
        push_endpoint=push_endpoint,
        service_account_email=configs.get("project_config").terraform_service_account,
        labels=labels,
        filter_expression=f"attributes.data_product=\"{configs.get('orchestration_config').source_data_product_name}\"",
        expiration_duration_secs=configs.get(
            "orchestration_config"
        ).expiration_duration_secs,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--template", action="store_true", help="Flag to generate the workflow template"
    )
    parser.add_argument(
        "--deploy", action="store_true", help="Flag to deploy the workflow"
    )
    parser.add_argument(
        "--execute", action="store_true", help="Flag to execute the deployed workflow"
    )
    args = parser.parse_args()

    if not args.template and not args.deploy and not args.execute:
        raise ValueError("Please select the process [--template, --deploy, --execute]")

    # Initialize global configurations
    configs = TemplateConfigs()
    # configs.get('metadata_config').gcp_service = 'dataproc_pipeline'

    # Check the workflow name length
    workflow_name = configs.get("orchestration_config").workflow_name

    if len(workflow_name) > 64:
        raise ValueError(
            f"Workflow name '{workflow_name}' exceeds the maximum length of 64 characters."
        )

    # Define paths
    WORKFLOW_DIR = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "workflow",
    )
    WORKFLOW_TEMPLATE_PATH = os.path.join(WORKFLOW_DIR, "workflow_orchestration.yaml")
    WORKFLOW_SAVE_PATH = os.path.join(WORKFLOW_DIR, "workflow_deploy.yaml")

    if args.template or args.deploy:
        print("Generating the workflow template...")
        generate_workflow(
            configs=configs,
            workflow_template_path=WORKFLOW_TEMPLATE_PATH,
            workflow_save_path=WORKFLOW_SAVE_PATH,
        )
        print("Workflow generated successfully.")

    if args.deploy or args.execute:
        workflow_helper = WorkflowHelper(
            project_id=configs.get("project_config").project_id,
            region=configs.get("project_config").region,
            experiment_name=configs.get("project_config").experiment_name,
            workflow_service_account=configs.get(
                "project_config"
            ).workflow_service_account,
            description=f"Workflow for {configs.get('project_config').experiment_name}",
        )

    if args.deploy:
        deploy_workflow(
            configs=configs,
            workflow_helper=workflow_helper,
            workflow_save_path=WORKFLOW_SAVE_PATH,
        )

    if args.execute:
        execute_workflow(
            configs=configs,
            workflow_helper=workflow_helper,
            execution_params={},
        )
