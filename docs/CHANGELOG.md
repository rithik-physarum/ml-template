# Release Notes 

### Table of Contents
- [Home](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/README.md)
- [Prerequisites](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/prerequisites.md)
- [Initialisation](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/initialisation.md)
- ML Template Guide
    - [Model Training](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/model-training.md)
    - [Model Prediction](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/model-prediction.md)
- [Formatting Code](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/formatting-code.md)
- [Copier Update](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/copier-update.md)
- **[Release Notes](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/CHANGELOG.md)**

All notable changes to this project will be documented in this file.
 
The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).


## [0.4.3] - 2025-01-08
### Changed
- Removed common functions in custom package
- Get ci functions from gcp-tools-lite and model-lineage
- Updated prediction aws and local tester
- Updated training, prediction, prediction_aws, monitoring example
- Upgraded monitoring module
- gcp-tools-lite==0.0.36
- model-lineage==0.2.11
- monitoring-lib==0.0.4

### Added
- k6 for aws ecs test
- load balancer for prediction aws

### Removed
- common functions in the custom package

## [0.4.2.1] - 2024-11-20
### Added
- Labeled configs and scripts with [DO NOT]
- Added the unique monitoring core
- Added ds-tools in comments
- Added monitoring image to gitlab config
- Added external table as example
- Added pega example to beam
- Added batch processing as example
### Changed
- Updated readme and docstring
- Default exp model-lineage
- execute orch. workflow in gitlab ci
- update gcp-tools-lite to 0.0.32
- supported gs path and local path in beam
- Added bigquery parition as example
- apache-beam[gcp]==2.59.0
- DotMap toDict in runner.py
- vertex component can get variables and base_image from config module.
- Update docs for IAM and dataset
- Updated registry model lineage for prod
- Updated migrate artifacts
### Debug
- add logger into register_model_version.py

## [0.4.1] - 2024-09-30
### Added
- model deployment with version tag
- Add GIT_TOKEN to dockerfile
### Changed
- Update dataflow based image to v0.0.3
- Udpate gcp-tools-lite to v0.0.28
- Update kfp local runner --local --docker
- Update CI shortcut
- Config refactor
- Update Docs and Docstring
- Update WIF

## [0.4.0] - 2024-08-23
### Added 
- CI variables for shortcut
- Vertex local runner
- Add new variable - experiment_name
- prediction dataflow local runner and docker runner
- schema-validation dataflow runner
- apply monitoring vm
### Removed
- monitoring-core, will be added after local dataproc runner

### Changed
- model-lineage with training, prediction and schema validation
- docker images from new harbor
- Get configs from TemplateConfigs

## [0.3.19] - 2024-07-02
### Added 
- `model-lineage v0.2.3` library 
    - registering model, dataset, parameter and model artifact to training stage
    - passing `lineage_dict` and other dictionaries necessary for lineage to training components
    - loading model artifact in prediction stage to run prediction pipeline
    - lineage model configs, for initialising lineage client and registration
- `get_artifacts_uri_stub` fn, for extracting part of training artifact path to be used in prediction
- `initialise_lineage_client` fn, for initialising `model-lineage` LineageClient
- `get_artifact_location` fn, for extracting artifact_location for `model_lineage_v2.model_artifacts` bq table
- `get_model_objects` fn, for extracting artifact_uri and loading the model_object using gtl `StorageHelper`

### Removed
- some lineage model configs, as lineage information is captured in model-lineage

## [0.3.18] - 2024-05-14
### Added
- terraform variables to config files

### Changed
- schema validation configs moved into orchestration config
- all terraform variables pulled from config files instead of `exp.tfvars`/`prod.tfvars`
- duplicated CI/CD `changes` as necessary with latest GitLab version

### Removed
- terraform `exp.tfvars` and `prod.tfvars`

## [0.3.17] - 2024-05-08
### Changed
- Rename the workflow template name for the gcp length limit < 48

## [0.3.16] - 2024-04-25
### Added
- extra CI/CD yml `if` conditionals to prevent stages running when not intended
- `schema_artifact` for `get_schema` component

### Removed
- pip configs from `orchestrator.gitlab-ci.yml` as hotfix for Nexus issue

## [0.3.15] - 2024-04-20
### Added
- `--orch_wait` command line argument for `test_run_workflow.py` so that CI/CD stage completes without waiting for orchestration workflow
- `table_schema.py` containing `table_schema` component to generate schema of BQ training table
- `get_table_schema` function for `utils.py` for generating table schema

### Removed
- duplicated conditional `changes` in CI/CD files

## [0.3.14] - 2024-04-18
### Changed
- monitoring example with data drift tool

## [0.3.13] - 2024-04-04
### Added
- deployment documentation to support data scientists
- deployment specific code to make deployment easier, in
    - `prediction_config.yaml`
    - `core/prediction/dataflow/transformers/predict_transformer.py`
    - `core/prediction/dataflow/beam_pipeline.py`

### Removed
- training ci/cd stages from production environment
- migrate artifact stage from production environment


## [0.3.12] - 2024-03-25
### Added
- `orchestration_workflow` for prediction and monitoring
- dataproc deployment to run monitoring
- configs to support monitoring orchestration

### Removed
- `monitoring/src` and put it in monitoring library
- `plan_prediction_tf` and `apply_prediction_tf` prediction CI/CD stages

## [0.3.11] - 2024-03-18
### Added
- WIF authentication in CI/CD scripts
- deployment changes in `prediction.gitlab-ci.yml`, allowing easy deployment to production
- parameterised GitLab ci files, no more duplicated configurations
- common scripts to root GitLab file
    - `.authentication` to run `gcloud auth` and set common google variables
    - `.pip-authentication` to provide access to our pip artifactory for ci/cd stages

### Removed
- JSON key authentication in CI/CD scripts

## [0.3.10] - 2024-03-11
### Added
- Add auto deployment to aws prediction

### Changed
- Hotfix changed new-docs

## [0.3.9] - 2024-02-22
### Added
- README approach to docs following news of losing GitLab Pages functionality

### Removed
- No longer updating ml-template GitLab Pages documentation, please see README for repository information

## [0.3.8] - 2024-02-19
### Added
- AWS speed load test for deployment

### Debug
- AWS terraform deployment problem, all environments go to exp env previously

## [0.3.7] - 2024-02-05
### Added
- model monitoring schema validation
    - `schema-validation==0.0.1` package connection 
    - `monitoring_config.yaml` to define monitoring configs
    - `get_table_schema` fn in `utils.py` to generate schema from a BQ table
    - `run_monitoring_pipeline` ci/cd stage to run the schema validation pipeline
    - `core/monitoring/Dockerfile` new Dockerfile
    - `core/monitoring/monitoring_config.py` file to define monitoring, generating monitoring config file
    - `core/monitoring/schema_validate.py` file to define schema validation, using `schema-validation` package
    - `core/monitoring/table_schema.py` file to generate table schema config, used during schema validation

### Changed
- `core/monitoring/monitoring.gitlab-ci.yml` updated to reflect newer training and prediction ci/cd scripts
- `gcp-tools-lite==0.0.12`, containing new StorageHelper changes
- configs
    - `repo_name` moved to `project_config.yaml` to avoid config duplication
    - renamed a lot of variables suffixed with `_path` to `_dir`


### Removed
- `core/monitoring/datapipeline` to be replaced with `schema-validation` package
- functionality from `io.py` and moved into gcp-tools-lite

## [0.3.6] - 2024-01-16
### Added
- Formatted and linted the following directories with Black & Flake8
    - `core/training`
    - `core/prediction`
    - `core/<package-name>`
    - `notebooks`
- Formatted the entirety of the package with Black
- Documentation update
    - Copier update - how to run copier update
    - Formatting - how to use Black & Flake8

## [0.3.5] - 2023-12-19
### Added
- Connection to new `dsc-pyartifactory` as a registry used to store our repositories
- Added artifactory installation using secret in all Dockerfiles
- Added artifactory authentication using keyring in ci steps
- New copier variable `pip_artifactory` with default value `dsc-pyartifactory`

### Changed
- Updated `gcp-tools-lite` version to `v0.0.11`

## [0.3.4] - 2023-12-06
### Added
- `copy_blob` function for migrating artifacts to `io.py`

### Changed
- `migrate_artifact.py` to work with new yaml configs
    
### Deleted
- `exp_to_prod.yaml`

## [0.3.3] - 2023-12-04
### Added
- passing `job_labels` to vertex and dataflow pipelines for finops tracking
- configs
    - `project_config` to remove project configuration duplications in other configs
    - `vertex_config` to mirror `dataflow_config`

### Changed
- configs
    - made all configs `yaml`
    - renamed `beam_options` to `dataflow_config` to reflect `nba-training-template`
    - removed `source_service` from `metadata_config` so it can be added in the relevant pipeline
    
### Deleted
- removed all reference to `DotMap` in the template

## [0.3.2] - 2023-11-20
### Added
- training
    - passing `job_labels` through the pipeline for latest finops monitoring in `gcp-tools-lite:v0.0.9`
- scoring
    - writing model output to gcs as csv
    - `core/prediction/terraform` for automatic prediction pipeline triggered from data product
        - `build_prediction_template` stage for building dataflow template used for data product pipeline trigger
        - `--generate_template` command line argument for `build_prediction_template` stage
        - `plan_prediction_tf` terraform plan stage to deploy pubsub subscription that receive events from data product and triggers the prediction pipeline
        - `apply_prediction_tf` apply stage of the above
- `RUN_TESTS` ci yaml variable set to false, to avoid running tests stages when they're not needed

### Changed
- training 
    - removed `DotMap` from chapter feedback
- moved `migrate_artifact.py` to scoring pipeline from training pipeline
- moved `migrate_artifact_exp_to_prod` stage to scoring pipeline from training pipeline
- latest version of `gcp-tools-lite:v0.0.9`

## [0.3.1] - 2023-11-07
### Added
- `docs/shell_files/copier.sh` for easier use of copier
- new `sql` directory to host SQL code
- introduced `git switch` to the documentation as a safer way to change branches

### Changed
- updated `docs/Initialisation.md` descriptions to be more understandable after user feedback
- updated `docs/Prerequisites.md` to describe copier process better and access `copier.sh` file
- updated copier help strings to provide more information to users

## [0.3.0] - 2023-11-06
### Added
- training pipeline
    - created `load_dummy_data` and `train_dummy_model` components
    - introduced new approach to io, using local gcs `.path` and `gcp-tools-lite` `utils`
- scoring pipeline
    - reading data from BQ table instead of generating dummy data
    - writing scoring results to BQ table
    - generating predictions using a dummy model
- `utils.py` for functionality shared across different pipelines and repository components

### Changed
- training pipeline
    - deleted `create_dummy_data` component
    - gcs path to save artifacts
    - introduced prefix 'ex-' for experiment names to differentiate from repository names
- scoring pipeline
    - replaced `Model` class with beam `setup` method to load scoring model in `PredictTransformer`
    - renamed `start_run` to `build_beam_pipeline`
    - deleted pipeline stage `build_prediction_template`
    - removed many command line args: `action`, `run_info_json`, `beam_option_json`, `parameters`
    - introduced `gcp-tools-lite`'s `DataflowHelper`
- configs
    - repository images now using `repo_name` instead of `experiment_name`
    - introduced `gcs` key for more intuitive model path configurations
- documentation
    - updated prerequisites page
    - updated Dataflow scoring page
    - added downloadable initialise.sh file
    - hidden out WIP pages
- copier questions
    - new `local_repo_location` variable, to add local path to envs
    - new `ci_commit_branch` variable, to speed up testing repo pipelines
 
### Deleted
- input/output, deleted `io.py` file
- `model.py`

## [0.2.0] - 2023-07-10
   
### Added
- New Folders
    - `core/<package-folder>/` - package to share common code across entire repository
    - `docs/` - directory to maintain the repository documentation
        - new ci/cd steps to deploy documentation from main
    - `env/` - directory to maintain environment variable files
        - `exp.env` - environment variable file to keep all the experimental prod environment variable
        - `prod.env` - environment variable file to keep all the production environment variable
    - `core/prediction_aws/`
        - `model_seving/` - deployment decorator to deploy a model class to ECS
        - config related to ECS deployment and environment variables
    
### Changed
- `core/training/`
    - `src/components/` - now named `components/`
    - `vertex_pipeline/` - now named `vertex/`
    - Supports py39
    - Training docker rebuild frequency reduced by loosening file change requirements to trigger it
- `core/prediction/` - moved `prediction_aws/`, `prediction_batch/`, `prediction_cloudrun/`, `prediction_vertex/` to `core/`
- `core/prediction/prediction_batch` - now `core/prediction/`
- `core/prediction/`
    - Default beam pipeline runs from first commit
    - `transformers/` module to maintain all beam transformers
    - Introduced [mlops_decorators](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/squads/ds-capability/mlops-decorators/-/tree/dev/) package to support conversion of python functions into beam transformers
    - Supports python 3.9
    - Supports Apache Beam v2.45.0
    - Prediction docker rebuild frequency reduced by loosening file change requirements to trigger it
 - CI/CD 
    - Training stages
        - `run_training_tests`
        - `build_training_docker`
        - `run_training_pipeline`
        - `migrate_artifact_exp_to_prod`
    - Prediction stages
        - `run_prediction_tests`
        - `build_prediction_docker`
        - `build_prediction_template`
        - `run_prediction_pipeline`
- `core/prediction_aws/`
    - `register_model/` module moved inside prediction_aws
    - `model_seving/` deployment decorator to deploy a model class to ECS
    - Config related to ECS deployment and environment variables
- `core/config/` - moved all repository configs to this locations
- Deleted folders
    - `core/features/` - removed and moved code to shared library [mlops_decorators](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/squads/ds-capability/mlops-decorators/-/tree/dev/)
    - `core/datasets/` - removed
 
## [0.1.9] - 2023-06-20
   
### Added
- Prediction Batch Dataflow
    - Support for apache beam version 2.45
    - Added beam_plugins and labels to support version 2.45

### Changed
- Folder structure for storing the kfp components in core/training
    - Created a new folder `pipeline_components/` in training to store the kubeflow pipeline
    - Kubeflow components are no more copied inside the docker image
    - Docker build step triggered only on changes in src folder and not on changes in kfp components

- Prediction Batch Dataflow  
    - Changed the config to scoring_config instead of cfg
    - Changed the way to read the model using the runid and experiment path
 
## [0.1.8] - 2023-05-29

### Fixed
 
- Fixed the automatic version upgrade cicd pipeline

## [0.1.7] - 2023-05-29
 
### Added

- Support for auto version upgrade using bump2version.
- Added pyproject.toml to main the requirements and project info.
- Added ci to update the version automatically

### Fixed
 
- Add a dummy vertex pipeline component to corrected the first to run successfully.
