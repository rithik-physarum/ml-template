# Model Monitoring

### Table of Contents
- [Home](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/README.md)
- [Prerequisites](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/prerequisites.md)
- [GCP Dataset and IAM access prerequisites](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/dataset-access.md)
- [Initialisation](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/initialisation.md)
- ML Template Guide
    - [Model Training](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/model-training.md)
    - [Model Prediction](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/model-prediction.md)
    - **[Model Monitoring](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/model-monitoring.md)**
    - [Model Orchestrator](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/model-orchestrator.md)
- [Deployment](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/deployment.md)
- [Formatting Code](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/formatting-code.md)
- [Copier Update](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/copier-update.md)
- [Release Notes](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/CHANGELOG.md)

## 1 Introduction

The monitoring components are low code approach, these are control by the config yaml files. the schema validation dataflow and the monitoring dataproc are controlled by `monitoring_config.yaml` and `monitoring_jobs_config.yaml`.

## 2 Config files

### 2.1 monitoring_config.yaml

`monitoring_config.yaml` controls the infrastructure of dataflow and dataproc.

| Variables | Desc |
| :---:   |  :---: |
| gs | Structure config of the schema validation component |
| infra_config | Structure config of the monitoring component |
| pyspark_job | The monitoring job's config, assigns the job runner and spark packages (jars) |
| workflow_name | The template name of the orchestration workflow |
| app_config.source.train.BigQuerySource | The training data input into the dataproc from BigQuery<br>`project`: gcp project id<br>`dataset`: dataset id in BigQuery<br>`table`: table name of the training table<br>`filters`: the sql where condition for the training dataset<br>`query`: custom pyspark query, it can transform the temp view (train_temp_view) above. |
| app_config.source.pred.BigQuerySource | The prediction data input into the dataproc from BigQuery<br>`project`: gcp project id<br>`dataset`: dataset id in BigQuery<br>`table`: table name of the prediction table<br>`filters`: the sql where condition for the prediction dataset<br>`query`: custom pyspark query, it can transform the temp view (pred_temp_view) above. |
| app_config.sinks | the output sinks for the dataproc (spark) |
| app_config.sinks.GCSSink | Output sink with Cloud Storage<br>`path`: gs path of the sink<br>`file_format`: format of output files |
| app_config.sinks.BigQuerySink | Output sink with BigQuery<br>`project`: gcp project id<br>`dataset`: dataset id in BigQuery<br>`table`: table name of the table<br>`temp_gcs_bucket`: Folder for cache<br>`mode`: mode of sink, append or overwrite |

`monitoring_jobs_config.yaml` control the jobs of dataproc

| Variables | Desc |
| :---:   |  :---: |
| data_drift | `data_drift` is the name of the dataproc job from monitoring-core |
| data_drift.date_col | date column in train and pred tables from `app_config.source` |
| data_drift.calculate_train | If true, the job will return wsd of training data |
| data_drif.run_type | If delta, the job will return the new records only; If full, the job will return all records |
| data_drif.transformation | If True, it will transform the pred table with the nba transformation function with agg5 and agg7 tables. If False, it will skip the transformation |
| data_drif.x_cols | If nba model, please clone the x_cols in `nba/data_config.yaml`; If non-nba model, it is the list of input features |

## 3 Debug

### 3.1 Schema Validation

The workflow will create a schema validation job in dataflow. We can get the error messages from the dataflow job.<br>
https://console.cloud.google.com/dataflow/jobs?project=bt-bvp-ml-plat-ai-pipe-exp

```
cd core/
python prediction/schema_validation_runner.py
```

### 3.2 Monitoring

The workflow will create a monitoring job in dataproc. we can get the error messages from the dataproc job.<br>
https://console.cloud.google.com/dataproc/jobs?project=bt-bvp-ml-plat-ai-pipe-exp

### 3.3 How to run monitoring locally
Install the monitoring-core, the version is matched, example:
```terminal
pip install monitoring-lib==0.0.4
```
Local direct runner
```terminal
cd <repo_name>/<repo_name>/core/
python -m monitoring.runner --local
```
Local docker runner<br>
Details: https://www.collab.bt.com/confluence/display/DI/Local+Docker+Runner+guide
```terminal
cd <repo_name>/<repo_name>/core/
python -m monitoring.runner --docker
```
Dataproc runner (on gitlab runner)
```terminal
cd <repo_name>/<repo_name>/core/
python -m monitoring.runner
```