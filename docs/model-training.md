# Vertex AI Model Training

### Table of Contents
- [Home](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/README.md)
- [Prerequisites](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/prerequisites.md)
- [GCP Dataset and IAM access prerequisites](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/dataset-access.md)
- [Initialisation](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/initialisation.md)
- ML Template Guide
    - **[Model Training](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/model-training.md)**
    - [Model Prediction](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/model-prediction.md)
    - [Model Monitoring](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/model-monitoring.md)
    - [Model Orchestrator](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/model-orchestrator.md)
- [Deployment](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/deployment.md)
- [Formatting Code](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/formatting-code.md)
- [Copier Update](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/copier-update.md)
- [Release Notes](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/CHANGELOG.md)

## 1 Introduction

This section outlines how to set up a Vertex AI model training pipeline. Besides training configurations found in `core/config/`, everything related to training is found within `core/training/`.

Vertex Pipelines are the most complete way to implement AI and machine learning pipelines on GCP. Please see the dynamic pricing **[training directory](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/squads/bb-alliance/bt-bb-dynamic-pricing/-/tree/exp/bt-bb-dynamic-pricing/core/training)** for an example of a completed Vertex training container.

## 2 Build a model in a notebook

The recommended first step to model training in Vertex is to build a model in a notebook. Regardless of your experience with Vertex, notebooks provide instant code feedback and allow you to build a model faster. Once you have a notebook that ingests data from a source, processes the data, builds a model, tests the performance, and you are happy with the performance, you are ready to begin. As always, it's advised to break your code up into functions, and these should be contained in your repository-specific package. See the dynamic-pricing **[package](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/squads/bb-alliance/bt-bb-dynamic-pricing/-/blob/exp/bt-bb-dynamic-pricing/core/dynamic-pricing/dynamic_pricing/utils.py)** in the bt-bb-dynamic-pricing repository for demonstration. The next section will tell you how to transfer your notebook code to Vertex AI.

## 3 Pipeline components

A Vertex pipeline is created by connecting together functions, named pipeline components, that each contribute a section of the model training process. How model training is sectioned into components is completely down to the user, and will most likely be dependent on the use-case. For beginners familiarising themselves with Vertex, it's common to either a) create one large component or b) create four smaller components with purposes similar to ingesting data, processing data, model building, and model testing. See the dynamic-pricing **[components directory](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/squads/bb-alliance/bt-bb-dynamic-pricing/-/tree/exp/bt-bb-dynamic-pricing/core/training/components)** for an example of using four components.

With your model build notebook and your plan to section it into components, you can begin copying your code into `core/training/components`. It is recommended that each component has it's own file, with the file and component sharing the same name. Components can have three types of function parameters:

- local variables, variables to be used directly in that component
- input variables, variables to be received from another component
- output variables, variables to be passed to another component

The latter two, input and output variables, are transferred between components and are often called artifacts. To define input or output artifact variables you add type hints to the variable that look like `data_artifact: Input[Dataset]` and `model_object_artifact: Output[Model]`. These artifacts are not the objects themselves, they are defined as component parameters to signify the use of the objects in the component. For the objects represented by these variables to be transferred across components, they need to be saved to, or loaded from, Google Cloud Storage. See a dynamic-pricing **[component](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/squads/bb-alliance/bt-bb-dynamic-pricing/-/blob/exp/bt-bb-dynamic-pricing/core/training/components/train_model_pipeline.py)** for an example of using input and output type hints along with saving and loading from Google Cloud Storage.

## 4 Vertex pipeline

Once you have created your pipeline components you can create your pipeline. Locate your `pipeline.py` file inside `core/training/vertex`, the function `build_vertex_pipeline` is used to create the vertex pipeline, calling the pipeline component functions created in **Section 3**. This provides Vertex the instructions on how to join the components by transfering the component artifacts across the pipeline. See the dynamic-pricing **[pipeline.py](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/models/recommender/bt-bb-dynamic-pricing/-/blob/exp/bt-bb-dynamic-pricing/core/training/vertex/bt_bb_dynamic_pricing/pipeline.py)** file to demonstrate how this is done. For a simplified example suppose you have two components shown below:

```
@component(base_image=base_image)
def component_example1(
    local_variable1: str,
    input_variable1: Input[Dataset],
    output_variable1: Output[Model],
)

@component(base_image=base_image)
def component_example2(
    local_variable2: str,
    input_variable2: Input[Model],
    output_variable2: Output[Dataset],
)
```
## 5 Model Lineage Integration

The model-lineage library integrates with this pipeline to track all essential data and metadata in **BigQuery tables**, supporting robust model tracking. 

Model lineage offers:
- A detailed record of **model progression**, including model name, version, training artifacts, baselines, and more.
- Monitoring of model performance trends.
- Seamless **integration** within pipeline components for automatic and efficient model tracking.

1. **Initialize LineageClient:**
    - Create the LineageClient using a lineage_dict containing necessary credentials and configuration.
```
lineage_dict = {
    "querier_project": querier_project,
    "lineage_project": lineage_project,
    "lineage_dataset": lineage_dataset,
    "use_case": repo_name,
    "experiment_name": experiment_name,
    "model_name": experiment_name,
    "model_version": model_development_version,
    "run_id": run_id,
    "job_labels": job_labels
}

lineage_client = LineageClient(**lineage_dict)

```

2. **Register Training Dataset:**
    - Register a new row in the **datasets table**.
    - It registers a training table **schema**, **baselines**, and details about the **features** used to train the model.
```
lineage_client.register_training_dataset(
    training_project=project,
    training_dataset_id=dataset_id,
    training_table_name=table_name,
    target_col=target_col,
    training_query=query,
    timestamp_column=timestamp_column,
    exclude_columns=exclude_columns
)
```
3. **Register Model:**
    -  Register a new row in the **model master table** for model tracking..
    - Records key model-specific details, such as the algorithm name, relevant Git repository information etc.
```
lineage_client.register_model(
    algorithm_name="xgboost",
    package_name="XGBoost",
    **user_dict,
    **git_dict
)
```
4. **Register Model Parameters:**
    - Adds a new entry to the **parameters table** for model tracking.
    - Registers important parameters used in training, such as **random seed** etc.
```
lineage_client.register_parameter(
    parameter_name="training_seed",
    parameter_value=training_seed
)
```
5. **Register Model Artifact:**
    - Adds a new entry to the **artifact table** for model tracking.
    - Key details registered include the artifact name, GCS URI of the saved model, and artifact data.
```
lineage_client.register_model_artifact(
    artifact_name="model_object",
    artifact_uri=model_artifact.uri.replace("_artifact", ".pkl")
)
```
**You will join these components in your `pipeline.py` file using the following code:**

```
from components.component_examples import component_example1, component_example2

def pipeline(project: str, region: str):
    
    component_example_op1 = component_example1(
        local_variable1=local_variable1,
        input_variable1=input_variable1,
    )
    
    component_example_op2 = component_example2(
        local_variable2=local_variable2,
        input_variable2=component_example_op1.outputs["output_variable1"],
    )
```

**Note:** you only pass local variables and input variables to component function calls. Output variables are not defined, and input variables are passed using previous components `.outputs` attribute to reference previous input variables.

## 5 `core/training/` top level folder structure

All files and folders can be edited to suit your purposes; if a file below is defined as does not require editing, this simply means you do not need to edit it to get your first training pipelines started. As you develop, you will want to edit most, if not all, of the files below.


| File/Folder              | Description    | Requires editing (Y/N) |
| :---                     | :---           | :---                   | 
| `tests/`                 | Directory that contains user defined unit tests. | Y |
| `vertex/`                | Directory that contains Vertex AI pipeline experiments. The experiment folder specific to the model build is your repo name. Inside these folders you'll fine a pipeline file, `pipeline.py`. This details how the code in `core/training/components/` folder is connected together to create the pipeline.| Y |
| `components/`            | Directory that contains KubeFlow components used to build Vertex AI pipelines. All the supporting functions are written outside the components folder and will be part of the training docker image.| Y |
| `Dockerfile`             | File pointing to pre-built vertex ai base image that contains packages required for your Vertex AI training pipeline. Also, installs any extra packages required for your pipeline from `requirements.txt`. | N |
| `requirements.txt`       | File containing packages to be installed in the training docker used in your training pipeline. | Y |
| `runner.py`              | File that triggers the Vertex AI pipeline defined within `vertex/`. Can be ran locally or from within GitLab CI. | N |
| `tox.ini`                | File that defines the setup for testing. | N |
| `training.gitlab-ci.yml` | File that defines the training GitLab CI pipeline. | N |

## 6 Training configs 

**Note:** any values within double brackets `{{ }}` will be populated when you use the ml-template

### 6.1 `core/config/exp/training_config.yaml`

This file will hold all the configuration settings, constants, parameters, etc., necessary for your pipeline run. It is consumed by the pipeline runner, `runner.py`, and provided to the `build_vertex_pipeline` function to be used within your pipeline components. See the dynamic-pricing **[training_config.json](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/models/recommender/bt-bb-dynamic-pricing/-/blob/exp/bt-bb-dynamic-pricing/core/config/exp/training_config.json)** for ideas on populating this file. See below for the unedited template version:

```
training_seed: 16
gcs:
  vertex_config_dir: "vertex_configs"
bq: 
  dataset_id: "ml_template"
  table_name: "ml_template_training_table"
  query: |
    SELECT 
      * 
    FROM 
      bt-bvp-ml-plat-ai-pipe-exp.ml_template.ml_template_training_table
    LIMIT 10
  target_col: "target"
  date_timestamp_column: "2024-08-11"
  exclude_columns: []
  entity_columns:
    - a
    - b

```
Update the training configuration parameters as per your use case to ensure the model trains effectively.

`training_seed`: Change this value to set a different random seed for reproducibility.

`vertex_config_dir`: Update the directory name where your Vertex AI configuration files are stored.

`dataset_id`: Specify the BigQuery dataset ID that will be used for training data.

`table_name`: Enter the name of the BigQuery table containing your training data.

`query`: Adjust the SQL query to select the appropriate training data, ensuring it fits your model's requirements.

`target_col`: Set the target column that your model will learn to predict.

`date_timestamp_column`: Specify the date timestamp for your training data to track temporal aspects.

`exclude_columns`: List any columns to exclude from the training data that are not relevant.

`entity_columns`: Define the entity columns that represent the features used in training.

### 6.2 `core/config/exp/training_experiments.json`

This file allows you to control which training pipeline experiments to run when you trigger the pipeline runner. Simply specify the pipeline experiment name and set `run` to either `true` or `false` for your purposes. 

```
{
    "{{ experiment_name|lower|replace('_', '-')|replace(' ', '-') }}": {
        "run": true
    }
}
```

## 7 Triggering the training pipeline

### 7.1 GitLab CI/CD pipeline trigger

There are a number of jobs within the training CI/CD pipeline, namely:
- `run_training_tests`, executes training unit tests defined in `core/training/tests/`
- `build_training_docker`, builds training docker image necessary to run training components
- `run_training_pipeline`, triggers `core/training/runner.py` to build and trigger the training pipeline
- `migrate_artifact_exp_to_prod`, migrates experimental prod artifacts to production buckets.

Your CI/CD pipeline will trigger when certain files or directories have changes made to them and pushed to GitLab. `run_training_tests` and `run_training_pipeline` will be triggered with every Git push containing changes to `core/training/`. `build_training_docker` will be triggered only when there is a change to the `Dockerfile`, `requirements.txt` and your repository package. `run_training_pipeline` will create a folder in Google Cloud Storage, based on the pipeline experiment name, in the bucket specified in `training_config.json` where your pipeline artifacts will be stored.

### 7.2 Local trigger

Before you can run a pipeline locally you need to update your Kubeflow Pipeline package as shown below:

```
pip install -r requirements.txt
```

You can run your pipeline locally by heading into the training directory of your repository and running `runner.py`

```
cd core/
python training/runner.py
```

As your pipeline requires your repository specific package you must first add your package to your python path. Below shows how you would do this for the dynamic-pricing repository:

```
export PYTHONPATH="/home/jupyter/bt-bb-dynamic-pricing/bt-bb-dynamic-pricing/core/dynamic-pricing/"
```

Put kfp_vars to all components for the local docker runner.
```
from gcp_tools_lite.data_tools.kfp.utils.vars import init_kfp_variables
local_run = init_kfp_variables(kfp_vars=kfp_vars)
```

**Note:** you should only trigger the pipeline locally if you do not need to rebuild your docker image. If you have made changes to your `Dockerfile`, `requirements.txt` or your repository specific package, please trigger you pipeline via CI/CD shown in **Section 7.1**.

### 7.2 Sample Vertex Pipeline Success Image
![vertex_pipeline_success_image.PNG](docs/images/vertex_pipeline_success_image.png)

### 7.3 Vertex Runners
Vertex Local Runner 
Location : {{ repo_name }}/core/{% if training == true %}training{% endif %}/runner.py
Details: https://www.collab.bt.com/confluence/display/DI/Local+Docker+Runner+guide

Command: use --local_run flag
```
python training/runner.py --local
```
Vertex (Cloud) Runner
Location: {{ repo_name }}/core/{% if training == true %}training{% endif %}/runner.py
```
python training/runner.py
```
Docker Runner
Location:{{ repo_name }}/core/{% if training == true %}training{% endif %}/runner.py

Run the vertex pipeline with the docker container (locally built image)
```
python training/runner.py --docker
```