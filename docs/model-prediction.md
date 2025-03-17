# Dataflow Batch Model Prediction

### Table of Contents
- [Home](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/README.md)
- [Prerequisites](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/prerequisites.md)
- [GCP Dataset and IAM access prerequisites](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/dataset-access.md)
- [Initialisation](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/initialisation.md)
- ML Template Guide
    - [Model Training](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/model-training.md)
    - **[Model Prediction](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/model-prediction.md)**
    - [Model Monitoring](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/model-monitoring.md)
    - [Model Orchestrator](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/model-orchestrator.md)
- [Deployment](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/deployment.md)
- [Formatting Code](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/formatting-code.md)
- [Copier Update](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/copier-update.md)
- [Release Notes](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/CHANGELOG.md)

## 1 Introduction

This section outlines how to set up a Dataflow beam pipeline for model prediction. Besides training configurations found in  `core/config/`, everything related to prediction is found within  `core/prediction/`.

Please see the dynamic pricing  **[prediction directory](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/squads/bb-alliance/bt-bb-dynamic-pricing/-/tree/exp/bt-bb-dynamic-pricing/core/prediction)**  for an example of a completed Dataflow prediction container. 


## 2 Scoring data in a notebook

Following on from lessons in model training, the scoring pipeline begins with a notebook. Notebooks provide instant feedback that allow you to perfect your approach before tackling the more lengthy procedure of triggering a dataflow pipeline. Dataflow executes predictions row by row, with each row passed through a series of defined beam transformations and operations. You must imitate this in a notebook by loading a single row of scoring data, processing it, and generate a prediction . Once you have done this, you are ready to start building your beam pipeline. 

Beam pipelines assume data as single key-value pair dictionaries but you can also convert these to pandas dataframes if you would find that easier to work with. To demonstrate how this is done please see the dynamic pricing model scoring notebooks using a **[dataframe](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/models/recommender/bt-bb-dynamic-pricing/-/blob/exp/bt-bb-dynamic-pricing/notebooks/06a_model_score_df.ipynb)** and **[dictionary](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/models/recommender/bt-bb-dynamic-pricing/-/blob/exp/bt-bb-dynamic-pricing/notebooks/06b_model_score_dict.ipynb)**. 

## 3 Beam Transformers

Similar to the training pipeline being constructed from vertex components, the scoring pipeline is constructed from beam transformers. Transformers can be thought of in the same way as components, with each performing a section of the scoring process. You require at least two beam transformers: one to transform your raw data into processed scoring data, and one generate a prediction on your scoring data. Your transformers can be found inside `core/prediction/dataflow/transformers`.

### 3.1 Transformers
Your data processing transformers will be created inside `/core/prediction/dataflow/transformers/transformers.py`. To begin it is recommended you use the `@beam_transformation` decorator, allowing you to create beam transformers from standard functions rather than the more complicated beam `DoFn` classes. These functions require you to pass `inputs` as the first parameter and return `inputs` at the end. Please see the dynamic-pricing **[`transformers.py`](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/models/recommender/bt-bb-dynamic-pricing/-/blob/exp/bt-bb-dynamic-pricing/core/prediction/dataflow/transformers/transformers.py)** for an example of this.

### 3.2 PredictTransformer

Your predict transformer is a class with two methods `setup` and `process`. The setup method runs only once during your scoring pipeline to load your model object. This allows you to access your model when you iteratively use your `process` method scoring every row. `setup` can be left alone provided you complete your `prediction_config` with the correct Google Cloud Storage path to your model object. `process` will be configured by you determined by your required prediction output.

## 4 `core/prediction/` top level folder structure

| File/Folder                 | Description | Requires editing (Y/N) |
| :---                        | :---        | :---                   |
| `dataflow/transformers/`    | Directory that contains all apache beam transformers used in the dataflow pipeline. | Y |
| `dataflow/beam_pipeline.py` | File that defines the beam pipeline, using transformers defined in `dataflow/transformers/`. Beam pipeline is provided with all the configs, pipeline options and run time options to run the pipeline. | Y |
| `Dockerfile`                | File pointing to pre-built dataflow base image that contains packages required for your dataflow prediction pipeline. Also, installs any extra packages required for your pipeline from `requirements.txt`. | N |
| `requirements.txt`          | File containing packages to be installed in the prediction docker used in your prediction pipeline. | Y |
| `runner.py`                 | File containing the logic to start the run for the prediction pipeline using dataflow. | N |
| `migrate_artifact.py`       | File used to upload experimental prod artifacts to production buckets.                 | N |
| `register_model_version.py` | File used to migrate data from the experimental to production model lineage each time a new model tag is created.  | N |
| `runtime_options.py`        | File containing class RunTimeOptions used to provide run time arguments for the pipeline. These parameters can be later passed to the pipeline using --parameters options. | N |
| `tests/`                    | Directory that contains user defined unit tests. | Y |
| `setup.py`                  | File used so that the prediction container to be installed as a package. | N |
| `tox.ini.py`                | File that defines the setup for testing. | N |
| `prediction.gitlab-ci.yml`  | File that defines the prediction GitLab CI pipeline. | N |

## 5 Prediction configs

### 5.1 `core/config/exp/prediction_config.json`

This JSON file should contains the configuration settings, constants, fixed & shared parameters, etc. necessary for the prediction pipeline. 

```
target_run_id: null
gcs:
  dataflow_dir: "dataflow"
  unica_landing_dir: "unica-model-scores/landing"
  gcp_edw_unica_str: "GCP_EDW_UNICA_EE_"
  max_bytes_per_shard: 736432000
  shard_name_template: "_SSSSSS_NNNNNN"
  brand: "EE"
  key_type: "a"
  output_type: "INT"
bq:
  query: |
    SELECT
      A as a,
      B as b,
      C as c,
      D as d,
      E as e,
      F as f
    FROM 
      bt-bvp-ml-plat-ai-pipe-exp.ml_template.ml_template_scoring_table 
    LIMIT 
      5;
  output_table: "bt-bvp-ml-plat-ai-pipe-exp:ml_template.ml_template_predictions"
  output_table_schema: "MODEL_ID:STRING, KEY_VALUE:STRING, MODEL_OUTPUT:FLOAT64, CREATE_DATE:DATE"
  output_table_header: 
    - "MODEL_ID" 
    - "BRAND"
    - "KEY_TYPE"
    - "KEY_VALUE" 
    - "MODEL_OUTPUT"
    - "MODEL_OUTPUT_TYPE"
    - "CREATE_DATE"
    - "STALE_DATE"
  temp_dataset: "beam_temp"
columns:
  drop_cols:
    - "f"

```
To customize the prediction configuration for your use case, update the above parameters:

## 6 Migrating Artifacts

### 6.1 Artifact Migration on deployment to prod

The migrate_artifact.py script automates the process of transferring essential model artifacts from the **exp** to **prod** bucket. Here’s a breakdown of the workflow:

  - It retrieves bucket names and project details from the configuration for both environments. The exp bucket contains the model artifacts, while the prod bucket is the destination.

  - The script fetches all model artifacts from the **model lineage**,For each artifact, the script constructs its URI and uses the GCS helper to copy the artifact from the experimental bucket to the production bucket, maintaining the same structure.

After processing all relevant artifacts, the migration is complete, ensuring that only the necessary files for prediction are transferred to the production environment.

### 6.2 model version and related artifacts migration on deployment to prod

The model_version_registration.py script automates the registration of model versions and model artifacts in the lineage tracking system.

  - fetches the run id based on this priority - run_id in commit_message > run_id in prediction_config > fetch latest from model lineage

  - Two instances of **LineageClient** are created—one for fetching model artifacts from the development environment and another for registering the model artifacts in the lineage tracking system.

  - The script iterates through all fetched model artifacts, checking if they are already registered. If an artifact's URI points to the experimental bucket, it updates the URI to point to the target bucket. Each artifact is then registered with its updated URI, and logging is performed for traceability.

This script is crucial for maintaining accurate lineage and tracking of model versions, ensuring that only the required artifacts are registered in the target bucket for production use.

## 7 Triggering the scoring pipeline

### 7.1 GitLab CI/CD pipeline trigger

There are a number of jobs within the prediction CI/CD pipeline, namely:
- `run_prediction_tests`, executes prediction unit tests defined in `core/prediction/tests/`
- `build_prediction_docker`, builds prediction docker image necessary to run prediction components
- `run_prediction_pipeline`, triggers `core/prediction/runner.py` to build and trigger the prediction pipeline

Your CI/CD pipeline will trigger when certain files or directories have changes made to them and pushed to GitLab. All jobs `run_prediction_tests`, `build_prediction_docker` and `run_prediction_pipeline` will be triggered with every Git push containing changes to `core/prediction/`. `build_prediction_docker` will also be triggered when there is a change to your repository package.

The stage `run_prediction_pipeline` runs the following line to trigger a job on dataflow:

```
python runner.py --job_name "{{ repo_name }}-prediction"
```

You can run this locally too, but the code will not execute locally, it will also send a job to be ran on dataflow.

### 7.2 Local trigger

You can run your pipeline locally by heading into the prediction directory of your repository and running `runner.py`

```
cd core/prediction/
python runner.py --local
```

As your pipeline requires your repository specific package you must first add your package to your python path. Below shows how you would do this for the dynamic-pricing repository:

```
export PYTHONPATH="/home/jupyter/bt-bb-dynamic-pricing/bt-bb-dynamic-pricing/core/dynamic-pricing/"
```

**Note:** you should only trigger the pipeline locally if you do not need to rebuild your docker image. If you have made changes to your `Dockerfile`, `requirements.txt` or your repository specific package, please trigger you pipeline via CI/CD shown in **Section 7.1**.

### 7.3 How Runners Function in these Environments

Prediction (dataflow)<br>
Beam Local Runner (Apache Beam DirectRunner)<br>
Location: {{ repo_name }}/core/{% if prediction_batch == true %}prediction{% endif %}/runner.py.jinja

```
python prediction/runner.py --local
```
Beam Dataflow Runner<br>
Location: {{ repo_name }}/core/{% if prediction_batch == true %}prediction{% endif %}/runner.py.jinja<br>
Important to note that Beam DirectRunner is preferred (Beam local runner) as Dataflow pipelines cause unnecessary delay during development

```
python prediction/runner.py
```
Beam Docker Runner <br>
Location: {{ repo_name }}/core/{% if prediction_batch == true %}prediction{% endif %}/runner.py.jinja<br>
Details: https://www.collab.bt.com/confluence/display/DI/Local+Docker+Runner+guide
```
python prediction/runner.py --docker
```