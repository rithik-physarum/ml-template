# GCP Dataset and IAM-Access Management - Prerequisites

### Table of Contents
- [Home](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/README.md)
- [Prerequisites](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/prerequisites.md)
- **[GCP Dataset and IAM access prerequisites](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/dataset-access.md)**
- [Initialisation](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/initialisation.md)
- ML Template Guide
    - [Model Training](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/model-training.md)
    - [Model Prediction](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/model-prediction.md)
    - [Model Monitoring](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/model-monitoring.md)
    - [Model Orchestrator](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/model-orchestrator.md)
- [Deployment](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/deployment.md)
- [Formatting Code](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/formatting-code.md)
- [Copier Update](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/copier-update.md)
- [Release Notes](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/CHANGELOG.md)

When creating a dataset on GCP for your repository, please ensure that you have completed the following

## **1 Workflow of Creating a new dataset for a repository**

Firstly a Dataset must be created in the appropriate project `(exp/prod)`
When this has been completed and changes successfully applied in the production environment, dataset access must be raised on 
the newly created dataset

Dataset Creation happens in bigquery-datasets - https://gitlab.agile.nat.bt.com/CDATASCI/gcp/common-infrastructure/bigquery-datasets
Access to a Dataset, bucket or table happens in iam-control - https://gitlab.agile.nat.bt.com/CDATASCI/gcp/common-infrastructure/iam-control

In order for you to have full access, a full process from repo-branch to exp to prod must succeed in bigquery-datasets to create a dataset in the appropriate project area `(exp/prod)`. It must succeed in both plan and apply stages in both exp and prod

Access must then be created in iam-control on the newly created dataset, again a full process from repo-branch to exp to prod must succeed in iam-control to provide access for that dataset in the appropriate project area `(exp/prod)`

The process should now be complete once the apply stage has succeeded in prod

### Note : Why do stages have to suceed in exp and prod, if I am only creating a dataset or access in exp?

The platform team have designed the creation and provisioning process to ensure guardrails are setup in the prod environment.
Changes must first go through the 'staging' environment (exp) to ensure the plan and apply changes succeed without incorrect changes
being merged into prod. Once the merge to prod has completed successfully, the process is complete

`terraform plan` - Simulates changes without making them. It previews the impact of your code changes on existing resources.
`terraform apply` - Actually applies the changes defined in the Terraform files to the infrastructure. It makes the modifications to the cloud resource - either creating a dataset or applying role access to a SA or user email provided in the vars

### 1.1 General guidelines on where to apply access or create a dataset

Changes in `exp.tfvars` on the branch reflect in bt-bvp-ml-plat-ai-pipe-exp.
Changes in `prod.tfvars` on the branch reflect in bt-bvp-ml-plat-ai-pipe-prod.
Always branch off `prod` to create changes in iam-control or bigquery-datasets, and merge into `exp` NOT `prod`

### 1.2 Dataset Creation 

Dataset provisioning Process for https://gitlab.agile.nat.bt.com/CDATASCI/gcp/common-infrastructure/bigquery-datasets

Option 1: Platform Request - Submit a post in the platform request channel with the following details:

- the project you wish to create the dataset for `(exp/prod)`,
- the ID of the repo i.e. `ee-payg-xsell`
- the description of why the dataset needs to be created
- the email of the dataset owner i.e. who is requesting it
- the dataset labels
    - environment  `(exp/prod)`
    - creators first name 
    - team name i.e. dsc/nba

Option 2 : Direct Request - https://gitlab.agile.nat.bt.com/CDATASCI/gcp/common-infrastructure/bigquery-datasets

### 1.3 Access IAM Provisioning

Access provisioning process for : https://gitlab.agile.nat.bt.com/CDATASCI/gcp/common-infrastructure/iam-control

Option 1: Platform Request - Submit a post in the platform request channel with the following details:


- the project you wish to grant access to  `(exp/prod)`,
- the dataset, bucket or table name that requires access
- The user's email 
- The role level of access i.e. dataset/table/bucket reader
- For prod access, if the line manager is aware

Option 2 : Direct Request - https://gitlab.agile.nat.bt.com/CDATASCI/gcp/common-infrastructure/iam-control


### 1.4 Merge request guidelines - Dataset and access provisioning

All dataset creation requests and access provsioning must be made into the exp branch

A general guide to do this is :

- Create a branch according to the merge request guidelines from prod
- Create changes on the newly created branch
- Raise changes from newly created branch into exp
- Gain approval from the platform team, this will merge the new branch with your changes into exp, and delete the staging branch
- Raise the merge request once succeeded from exp into prod


