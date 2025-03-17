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
def train_dummy_model(
    data_artifact: Input[Dataset],
    target_col: str,
    exclude_columns: list,
    training_seed: int,
    lineage_dict: dict,
    user_dict: dict,
    git_dict: dict,
    kfp_vars: dict,
    model_artifact: Output[Model],
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
    from sklearn.preprocessing import OneHotEncoder
    from sklearn.compose import ColumnTransformer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    from sklearn.impute import SimpleImputer

    from gcp_tools_lite.data_tools.storage_tools_v2 import StorageHelperV2
    from model_lineage.clients.lineage_client import LineageClient

    io = StorageHelperV2()

    # Prepare training data
    data = io.load(data_artifact.path.replace("_artifact", "_train.parquet"))
    y_train = data[target_col]
    X_train = data.drop(
        columns=exclude_columns+[target_col],
    )
    
    # Create preprocessor for data cleaning
    categorical_columns = X_train.select_dtypes(
        include=['object', 'category']
    ).columns.tolist()
    numerical_columns = list(set(X_train.columns)-set(categorical_columns))
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_columns),
            ('num', SimpleImputer(strategy='constant', fill_value=0), numerical_columns)
        ],
        remainder='passthrough'  # Keep the rest of the columns as they are
    )

    # Train model with preprocessor
    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', LogisticRegression())
    ])
    model.fit(X_train, y_train)

    # Save model
    io.save(
        data=model,
        path=model_artifact.path.replace("_artifact", ".pkl"),
    )

    # Push result to model-lineage
    if not local_run:
        lineage_client = LineageClient(
            **lineage_dict,
        )
        lineage_client.register_model(
            algorithm_name="xgboost",
            package_name="XGBoost",
            **user_dict,
            **git_dict,
        )
        lineage_client.register_parameter(
            parameter_name="training_seed",
            parameter_value=training_seed,
        )
        lineage_client.register_model_artifact(
            artifact_name="model_object",
            artifact_uri=model_artifact.uri.replace("_artifact", ".pkl"),
        )