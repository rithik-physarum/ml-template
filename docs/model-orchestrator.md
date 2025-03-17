# Orchestration Workflow

### Table of Contents
- [Home](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/README.md)
- [Prerequisites](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/prerequisites.md)
- [GCP Dataset and IAM access prerequisites](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/dataset-access.md)
- [Initialisation](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/initialisation.md)
- ML Template Guide
    - [Model Training](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/model-training.md)
    - [Model Prediction](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/model-prediction.md)
    - [Model Monitoring](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/model-monitoring.md)
    - **[Model Orchestrator](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/model-orchestrator.md)**
- [Deployment](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/deployment.md)
- [Formatting Code](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/formatting-code.md)
- [Copier Update](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/copier-update.md)
- [Release Notes](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/CHANGELOG.md)

## 1 Introduction

Orchestration Workflow controls the end-to-end processes during prediction, including kicking-off by pub-sub, schema validation by dataflow, model prediction by dataflow and monitoring by dataproc. Besides training configurations found in  `core/config/`, everything related to orchestration is found within  `core/orchestrator_workflow/`.

For detailed documentation and additional information, please refer to the [Confluence page](https://www.collab.bt.com/confluence/display/DI/ML+Template?src=contextnavpagetreemode).

## 2 Development
The orchestration is the config approach, `core/orchestrator_workflow/` is ready for deployment. `core/config/orchestration_config.yaml` is the only part to be modified in the workflow.
- **sample orchestration_config:**
```
schema_validation:
  schema_validation_template_url: "gs://ds-capability/schema-validation/schema_validation/config/0.0.7/template/schema-validation"
topic: "data-product-success-run"
prediction_pipeline_params: {}
monitoring_workflow_params: {}
source_data_product_name: ""
monitoring_drift_table: "{{ project_id }}.dataproc_monitoring.{{ experiment_name|lower|replace('-', '_')|replace(' ', '_') }}_monitoring_drift"
alert_threshold:
  jensenshannon: 0.5
  kullbackleibler: 0.5
  wasserstein: 0.5
workflow_name : "{{ experiment_name }}-orchestrator"
```

**Parameter Descriptions**

`source_data_product_name`: The name of the data product for the Pub/Sub trigger. When the data product is completed, Pub/Sub will kickstart the orchestration workflow.

`prediction_pipeline_params`: Parameters that are passed to the prediction Dataflow.

`monitoring_workflow_params`: Parameters that are passed to the monitoring Dataproc.

`schema_validation_params`: Parameters that are passed to the schema validation Dataflow.

`monitoring_workflow_name`: The name of the monitoring Dataproc job on GCP.

`monitoring_drift_table`: The table used for monitoring drift, constructed dynamically based on project and experiment names.

`alert_threshold`: Threshold values for various drift metrics (Jensen-Shannon, Kullback-Leibler, Wasserstein) to trigger alerts.

`workflow_name`: The name of the orchestration workflow, generated from the experiment name.

## 3 Workflow components
The workflow has 7 components:

### 3.1 init
- It prepares the configs for the following components.

### 3.2 triggerSchemaValidation
- Initiates the Dataflow job for schema validation.
- Validates both the training schema and the prediction schema to ensure data integrity.
- Launches a Dataflow job in GCP to check the structure and quality of incoming data against predefined schema rules.

### 3.3 waitDataflowJobDone
- It monitors the dataflow for schema validation unitl it completes.
- Ensures early detection of any errors and waits for successful validation before proceeding.

### 3.4 triggerPrediction
- Triggers the Dataflow job responsible for generating predictions after successful schema validation.
- Utilizes validated data and the appropriate model to produce predictions.
- Launches a Dataflow pipeline in GCP that makes predictions and writes the output to BigQuery or another desired location.

### 3.5 waitDataflowJobDonePred
- It monitors the dataflow for prediction unitl it completes.
- Confirms accurate generation of predictions before moving to the monitoring stage.

### 3.6 triggerMonitoringWorkflow
- Triggers the Dataproc job for monitoring model performance and predictions.
- Launches a job in Dataproc to evaluate the effectiveness of the model over time.

### 3.7 waitDataflowJobDonePred
- It monitors the dataproc for monitoring unitl it completes.
- Ensures successful execution of monitoring processes, providing insights into model performance and drift detection.

## 4 Detail of components

`Schema validation:` It is generated automatically by the schema config in `prediction_config.yaml`. It checks the schema of output is correct format to the serving layer.

**sample successful schema validation dataflow pipeline -**

![schema_validation_pipeline_success_image.PNG](docs/images/schema_validation_pipeline_success_image.png)


`Prediction:` 
The prediction process is automatically initiated upon the completion of schema validation. This involves a Beam pipeline that retrieves the model URI from the model lineage, loads the model from Google Cloud Platform (GCP), generates predictions, and writes the output to either BigQuery, CSV files, or other specified formats.
[Model Prediction](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/model-prediction.md)

**sample successful prediction dataflow pipeline -**

![prediction_pipeline_success_image.PNG](docs/images/prediction_pipeline_success_image.png)

`Monitoring`:
    - Automatically initiated after the prediction phase, it evaluates model performance, tracks key metrics, and identifies anomalies in outputs.
Calculates drift by comparing current outputs with historical data from the model lineage, writing results into BigQuery for continuous evaluation and timely adjustments.

[Model Monitoring](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/model-monitoring.md)

[You can access the Dataproc jobs for monitoring the pipeline by following this link.](uhttps://console.cloud.google.com/dataproc/jobs?authuser=1&project=bt-bvp-ml-plat-ai-pipe-exprl)

## 5 sample successful orchestration workflow image

![workflow_success_image.PNG](docs/images/workflow_success_image.png)


## 6 Debug

The Pub/Sub will trigger the orchestration via `data-product-success-run` pub/sub topic.<br>
https://console.cloud.google.com/cloudpubsub/topic/detail/data-product-success-run?project=bt-bvp-ml-plat-ai-pipe-exp


The orchestration will create a job in workflows. we can get the error messages from the workflows job.<br>
https://console.cloud.google.com/workflows?referrer=search&project=bt-bvp-ml-plat-ai-pipe-exp
