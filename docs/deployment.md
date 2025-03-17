# Deployment

### Table of Contents
- [Home](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/README.md)
- [Prerequisites](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/prerequisites.md)
- [GCP Dataset and IAM access prerequisites](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/dataset-access.md)
- [Initialisation](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/initialisation.md)
- ML Template Guide
    - [Model Training](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/model-training.md)
    - [Model Prediction](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/model-prediction.md)
    - [Model Monitoring](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/model-monitoring.md)
    - [Model Orchestrator](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/model-orchestrator.md)
- **[Deployment](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/deployment.md)**
- [Formatting Code](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/formatting-code.md)
- [Copier Update](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/copier-update.md)
- [Release Notes](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/CHANGELOG.md)

This document will explain how to prepare your repository for deployment. Please refer to the **[Model Deployment Checklist](https://www.collab.bt.com/confluence/display/DI/Model+Deployment+Checklist)** to support information in this doc.

## 1 Request Review

Before a model can be deployed the code must be reviewed from software engineering and machine learning methodology stand points. As a model approaches deployment readiness, please request a code review in the BVP DS Platform team under the Code Review channel. Allow for up to two weeks for your code review to be completed; so it is recommended you request a code review before you are finished developing. 

## 2 UNICA Deployment (optional)

This section describes how to get model scores into UNICA, and is not applicable for all cases; please move onto the next section if believe this does not apply to you. Model scores that are correctly formatted in the correct location will be picked up, packaged appropriately and sent to UNICA. This transfer occurs daily for all model results that fulfil the below criteria: 

### 2.1 Scoring output format

The formatting of the model output is particular and strict, the output data must have the following columns and data types:

| Field Name   | Description   | Data Type | Example |
|--------------|---------------|---------|---------|
| MODEL_ID | Unique ID of the model, typically repository name | STRING | bt-bb-dynamic-pricing |
| BRAND | BT/EE | STRING | BT |
| KEY_TYPE | Customer identifier, BAC/MSISDN/SUB_ID/MSR_ADDR_PROS_ID | STRING | BAC |
| KEY_VALUE | The value of the chosen KEY_TYPE | STRING | GenevaGB1111111 |
| MODEL_OUTPUT | Model score/prediction | STRING | 0.76 |
| MODEL_OUTPUT_TYPE | The data type of output, STRING/DOUBLE | STRING | DOUBLE |
| CREATE_DATE | Date the predictions were generated | DATE | 2023-01-20 |
| STALE_DATE | Date the data scientist estimates the scores will be stale | DATE | 2023-07-20 |

**Note:** if your model needs to return more than one score, you can define the `MODEL_OUTPUT` string with as many outputs as necessary separated with a chosen character. E.g. you could have `"0.76*0.81*0.31"`, or similar.

### 2.2 Scoring output location

Scoring files need to be outputted to the Google Cloud Storage directory `ds-capability/unica-model-scores/landing/<repository-name>` with file names of the form `GCP_EDW_UNICA_EE_<REPOSITORY_NAME>_<FILE_NUMBER>_<TOTAL_FILES>_YYYYMMDD.csv`. Please see the GCS **[UNICA landing directory](https://console.cloud.google.com/storage/browser/ds-capability/unica-model-scores/landing?pageState=(%22StorageObjectListTable%22:(%22f%22:%22%255B%255D%22))&project=bt-bvp-ml-plat-ai-pipe-exp&prefix=&forceOnObjectsSortingFiltering=false)** for some examples of this.

To output your scoring file to this location, in `core/prediction/dataflow/beam_pipeline.py` change the `gcs_file_path` to:

```
gcs_file_path = os.path.join(
    project_config["bucket"],
    prediction_config["unica_landing_dir"],
    project_config["repo_name"],
    prediction_config["gcp_edw_unica_str"] + project_config["repo_name"].upper(),
)
```

Where your prediction config will contain:

```
unica_landing_dir: "unica-model-scores/landing"
gcp_edw_unica_str: "GCP_EDW_UNICA_EE_"
```

If you keep the `gcs_sink` in the same form shown below, the string `_<FILE_NUMBER>_<TOTAL_FILES>_YYYYMMDD.csv` will be handled for you automatically:

```
gcs_sink = beam.io.WriteToText(
    file_path_prefix=gcs_file_path,
    file_name_suffix=f"_{str(date.today()).replace('-','')}.csv",  # configures YYYYMMDD.csv
    header=f"{','.join(bq_config['output_table_header'])}\n",
    max_bytes_per_shard=gcs_config["max_bytes_per_shard"],
    append_trailing_newlines=False,
    shard_name_template=gcs_config["shard_name_template"],         # configures <FILE_NUMBER>_<TOTAL_FILES>
)
```

**Note:** scoring files are only picked up from `ds-capability-prod` so model deployment to production is required before results are sent to UNICA.

## 3 Config Files

The CI/CD files infer the environment from the branch used, exp or prod, and use that information to point to the relevant config files. Pre-deployment you will have populated the `core/config/exp` directory with the necessary variables to run your pipelines. In preparation for deployment to the production environment, you must populate the `core/config/prod` directory.

- duplicate the `core/config/exp/` prediction and monitoring code into the `core/config/prod/` directory
- open each file and replace `-exp` with `-prod`
    - e.g. bvp-ml-platform-exp-vpc-network -> bvp-ml-platform-prod-vpc-network
    - e.g. bvp-ml-plat-ai-pipe-exp -> bvp-ml-plat-ai-pipe-prod
    - be careful to not turn the string "experimental" into "proderimental", or similar
- in each file replace `gs://ds-capability` with `gs://ds-capability-prod`
    - be careful to not turn `ds-capability-docker-registry` to `ds-capability-prod-docker-registry`

## 4 Migrating Artifacts

All of the artifacts required for prediction, e.g. the model file, need to be moved across to the production bucket in Google Cloud Storage. The ml-template contains a python file, `core/prediction/migrate_artifact.py`, that helps you do this easily. Only files that are required to run the pipeline need to be migrated, files that are generated by the pipeline can be left alone. 

 - It retrieves bucket names and project details from the configuration for both environments. The exp bucket contains the model artifacts, while the prod bucket is the destination.

  - The script fetches all model artifacts from the **model lineage**,For each artifact, the script constructs its URI and uses the GCS helper to copy the artifact from the experimental bucket to the production bucket, maintaining the same structure.

After processing all relevant artifacts, the migration is complete, ensuring that only the necessary files for prediction are transferred to the production environment.

## 5 CI/CD

The artifact migration is handled via CI/CD stage `migrate_artifact_exp_to_prod`. This is a good opportunity to check a final time that your prediction pipeline runs as expected in exp. 

- inside `core/prediction/prediction.gitlab-ci.yml`, set `ALLOW_MIGRATION: "true"` 
- run a successful prediction pipeline with all of it's expected stages
    - ensure you have manually triggered the job `apply_prediction_tf` and that it has successfully ran
    - ensure `migrate_artifact_exp_to_prod` has successfully ran
- check Google Cloud Storage for your artifacts in `ds-capability-prod` bucket
