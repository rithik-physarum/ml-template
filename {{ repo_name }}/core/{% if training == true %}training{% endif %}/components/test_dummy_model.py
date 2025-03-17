"""
# -------------------------------------------------------------
# PYTHON File
# NOTE: 
#   - DO NOT EDIT sections marked as [DO NOT EDIT]
#   - Sections without this mark can be modified as needed.
# -------------------------------------------------------------

Train dummy model.

Loading dummy data from a Google Cloud Storage and training
a basic Logistic Regression model with it. Finally, saving
the model as a pickle file to Google Cloud Storage.
"""

# [CAN EDIT] - ALL

import os

from kfp.v2.dsl import component, Dataset, Input, Model, Output
from runner import configs


@component(
    base_image=configs.get("vertex_config").base_image,
    install_kfp_package=False,
)
def test_dummy_model(
    data_artifact: Input[Dataset],
    model_artifact: Input[Model],
    target_col: str,
    exclude_columns: list,
    lineage_dict: dict,
    kfp_vars: dict,
    testing_summary: Output[Dataset],
):
    """
    Trains a logistic regression model on dummy data and
    saves the model as a pkl file to Google Cloud Storage.

    Parameters
    ----------
    data_artifact : pd.Dataframe
        Training data
    training_seed : int
        Seed used for determinism
    lineage_dict : dict
        Dictionary for initialising model-lineage LineageClient
    user_dict : dict
        Dictionary for user information
    git_dict : dict
        Dictionary containing git environment variables
    kfp_vars : dict
        Dictionary containing kubeflow pipeline variables. Includes
        environment, credential and local run variables for running
        vertex pipelines locally

    Outputs
    -------
    model_artifact : vertex object
        Object containing attribute path, the local
        gcs path to save/load the model

    """
    from gcp_tools_lite.data_tools.kfp.utils.vars import init_kfp_variables
    local_run = init_kfp_variables(kfp_vars=kfp_vars)
    from sklearn.metrics import roc_curve, roc_auc_score
    import matplotlib.pyplot as plt

    from gcp_tools_lite.data_tools.storage_tools_v2 import StorageHelperV2
    from model_lineage.clients.lineage_client import LineageClient

    io = StorageHelperV2()

    # Prepare testing data
    data = io.load(data_artifact.path.replace("_artifact", "_train.parquet"))
    y_test = data[target_col]
    X_test = data.drop(
        columns=exclude_columns+[target_col],
    )

    # Load model and predict
    model = io.load(model_artifact.path.replace("_artifact", ".pkl"))
    y_prob = model.predict_proba(X_test)[:, 1]

    # Compute ROC curve
    fpr, tpr, thresholds = roc_curve(y_test, y_prob)

    # Compute AUC score
    auc = roc_auc_score(y_test, y_prob)
    
    # Plot ROC curve
    plt.plot(fpr, tpr, label=f"AUC = {auc:.2f}")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve")
    plt.legend()
    plt.savefig(testing_summary.path+".png")

    if not local_run:
        lineage_client = LineageClient(
            **lineage_dict,
        )
        lineage_client.register_model_artifact(
            artifact_name="roc_curve",
            artifact_uri=testing_summary.uri+".png",
        )
        lineage_client.register_training_metric(
            metric_name="auc",
            metric_value=auc,
        )
