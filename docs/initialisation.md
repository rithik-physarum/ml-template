# Project Initialisation

### Table of Contents

- [Home](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/README.md)
- [Prerequisites](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/prerequisites.md)
- [GCP Dataset and IAM access prerequisites](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/dataset-access.md)
- **[Initialisation](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/initialisation.md)**
- ML Template Guide
    - [Model Training](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/model-training.md)
    - [Model Prediction](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/model-prediction.md)
    - [Model Monitoring](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/model-monitoring.md)
    - [Model Orchestrator](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/model-orchestrator.md)
- [Deployment](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/deployment.md)
- [Formatting Code](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/formatting-code.md)
- [Copier Update](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/copier-update.md)
- [Release Notes](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/CHANGELOG.md)


### 1.1 Create a project repository in on-prem gitlab

To create a repository, please go to the **[git-utils](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/git-utils)** repository and follow the ReadMe instructions.
 
### 1.2 Git clone your repository

In your GCP notebook instance clone your repository. Your username is your UIN and your password is your BT password.

```
git clone https://gitlab.agile.nat.bt.com/CDATASCI/gcp/models/<model-type>/<your-repo-name>/
cd <your-repo-name>
git switch exp
cd ..
```

### 1.3 Git clone the ML Template

```
git clone https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template.git
```

Make sure you have the latest version of the ml-template:

```
cd ml-template
git switch main
git pull
cd ..
```

### 1.4 Generate the template using copier
You can answer the copier questions one at a time or you can edit this file [copier.sh](shell_files/copier.sh) to answer them all at once. To understand how to fill in the copier answers, please see the help information in **Section 1.5**.

#### 1.4.1 Run using copier.sh (recommended)

```
cd <your-repo-name>
bash ../copier.sh
```

#### 1.4.2 Run a line at a time 

```
copier copy --vcs-ref=HEAD ml-template/ <your-repo-name>/ --trust
```

### 1.5 Answering the copier questions

Take this slowly as it will configure your entire project repository, and small mistakes can cause headaches later on. 

See below for example copier answers:

```
Step 1/19 - "User's full name"
   Michael Roche
   
Step 2/19 - "User's email address"
   michael.2.roche@ee.co.uk
   
Step 3/19 - "User's BT UIN"
   613890586
   
Step 4/19 - "User's team, for chapter data scientists this will be your alliance
   i.e. bb-alliance, mobile-alliance, vfm-alliance, etc"
   bb-alliance
   
Step 5/19 - "Parent Gitlab (remote) project location, this is where your project
    is located in GitLab e.g. CDATASCI/gcp/models/recommender"
   CDATASCI/gcp/models/recommender
   
Step 6/19 - "Local repo location, i.e. where your new repository is located in your
    notebook instance. Unless you have your repository inside another directory in your
    instance home directory this will be /home/jupyter"
   /home/jupyter
   
Step 7/19 - "GitLab repository or high level folder, e.g. bt-bb-dynamic-pricing"
   bt-bb-recommender
   
Step 8/19 - "Experiment name, for chapter data scientists this will be
    'ex-' followed by the name of your repository, e.g. ex-dynamic-pricing"
   ex-bb-recommender
   
Step 9/19 - "Repository-specific package name in snake_case, e.g. dynamic_pricing"
   bb_recommender
   
Step 10/19 - "Google Cloud project, for chapter data scientists this will be bt-bvp-ml-plat-ai-pipe-exp"
   bt-bvp-ml-plat-ai-pipe-exp
   
Step 11/19 - "Service account, for chapter data scientists this will be
    ml-pipelines-sa@bt-bvp-ml-plat-ai-pipe-exp.iam.gserviceaccount.com"
   ml-pipelines-sa@bt-bvp-ml-plat-ai-pipe-exp.iam.gserviceaccount.com
   
Step 12/19 - "Project location, for chapter data scientists this will be europe-west2"
   europe-west2
   
Step 13/19 - "Docker registry, for chapter data scientists this will be ds-capability-docker-registry,
    for nba developers this will be nba-docker-registry"
   ds-capability-docker-registry

Step 14/19 - "The pip artifactory"
   dsc-pyartifactory
   
Step 15/19 - "Google Cloud Storage exp environment, for chapter data scientists this will be ds-capability,
    for nba developers this will be c16-nba"
   ds-capability
   
Step 16/19 - "Google Cloud Storage prod environment, for chapter data scientists this will be ds-capability-prod,
    for nba developers this will be c16-nba"
   ds-capability-prod
   
Step 17/19 - "Select true if you want a training pipeline in your repository, for chapter data scientists select true"
   True
   
Step 18/19 - "Select true if you want a prediction pipeline in your repository, for chapter data scientists select true"
   True
   
Step 18[A]/19 - "Select true if you want to use Dataflow for prediction, for chapter data scientists select true"
   True
   
Step 18[B]/19 - "Select true if you want to use Vertex for prediction, for chapter data scientists select false"
   False
   
Step 18[C]/19 - "Select true if you want to use Cloud Run for prediction, for chapter data scientists select false"
   False
   
Step 18[D]/19 - "Select true if you want to use AWS for prediction, for chapter data scientists select false"
   False
   
Step 19/19 - "Select true if you want to model performance and drift monitoring, for chapter data scientists select true"
   True
```

### 1.6 Push everything to git
```
cd <your-repo-name>
git add .
git commit -m "Initial Commit"
git push
```

Congratulations! You should now have the latest ml-template changes pushed to your GitLab project. If done successfully, a CI/CD pipeline should have triggered from your repository (see the **[dynamic pricing pipelines](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/squads/bb-alliance/bt-bb-dynamic-pricing/-/pipelines)** to illustrate GitLab pipelines). Your pipeline will contain a number of stages, categorised into training, prediction and monitoring stages. Currently, only the training and prediction stages will run. These are the first seven stages of your pipeline, with the third and seventh stages being run_training_pipeline and run_prediction_pipeline respectively. These are example pipelines performing basic tasks to be used for demonstration purposes only. 

Happy developing!

### 1.7 Copier mistakes

It's very common to have made a mistake or two when using the copier template. The simplest thing to do is to start again by running copier to generate your repository from scratch. This is because the copier answers you provide are far reaching in your repository and it can be difficult to find every change to reverse the mistake. If you notice you have made a mistake after significant changes have been made to your repository, it might be easier to try an automated approach to reverse the change first.

#### 1.7.1 How to start from scratch

**Note:** You are going to delete your exp branch to start again, so check you are absolutely sure it can be deleted before continuing

Below demonstrates how you would delete and recreate your exp branch from your notebook instance terminal.

```
cd bt-bb-dynamic-pricing      # enter your repository

git switch prod             # change branch to prod
git branch -d exp             # delete branch locally
git push origin --delete exp  # delete branch on GitLab

git switch -b exp           # create new exp branch locally
git push -u origin exp        # create branch on GitLab

cd ..                         # exit your repository to run copier
```

Now you can go back to **Section 1.4** with a clean exp branch to generate your project repository.

#### 1.7.2 Automated approach

Before you attempt the automated approach, it's advised to have any local changes pushed to GitLab. This allows you to check which files were changed during this automatic process by running `git status`. 

Below is an example of the Linux command to fix a copier mistake in the dynamic-pricing repository.

```
find bt-bb-dynamic-pricing -type f -name "*.py" -exec sed -i 's/dynamic-pricing/dynamic-pricing-change/g' {} +
```

This will find all regular files, `-type f`, with filename ending ".py", `"*.py"`, within the `bt-bb-dynamic-pricing` directory and executes, `-exec`, the `sed` command on them. The sed command performs an inplace, `-i`, text transformation, replacing all counts of `dynamic-pricing` with `dynamic-pricing-change` in all files found by the `find` command. In other words, this will automatically change `dynamic-pricing` to `dynamic-pricing-change` within all python files of the bt-bb-dynamic-pricing repository. 

If done correctly, you can use this command to fix errors across your entire repository in one line. After running this, you can run `git status` to be shown a complete list of all files changed. To inspect files further you can run `git diff <file-path>` to see the exact changes made to a file. This automated approach is very useful but be cautious when using it, as without care you can make your problem worse.

## 2.1 Understanding `core/` folder structure

The `core/` directory is where all of your project functionality begins. It contains all of the modularised components such as training, prediction and monitoring, and also houses your repository-specific package and configurations. 

**Note:** core directories are essential for the DS Chapter workflow, whereas non-core directories provide additional functionality that users may want for specific use cases

| Folder                | Description | Core (Y/N)    | 
| :---                  | :---        |:---           |
| `config`              | Directory that contains all of your project configurations. Using `config` encourages a clear and strict separation between project code and configuration. | Y |
| `package_name`        | Repository-specific package containing all functionality that is used throughout your repository. Will be installed from your other repository pipelines and modules. | Y |
| `training`            | Module for Vertex AI training pipeline code. | Y |
| `prediction_batch`    | Module that contains prediction workflow logic using apache beam and dataflow. | Y |
| `prediction_aws`      | Module used to deploy a model to an endpoint. | N |
| `prediction_cloudrun` | Module to support model deployment on a endpoint created on cloud run. | N |
| `prediction_vertex`   | Module that contains prediction workflow logic using Vertex AI. | N |
| `monitoring`          | Module that contains monitoring related codebase. | Y |

## 2.2 Purpose of the folder structure

The folder structure serves the following purposes:

- code organization: the folder structure provides a systematic organisation of files, enhancing readability, maintainability, and collaboration among developers.

- configuration management: by segregating configuration files into dedicated directories, the folder structure simplifies the management and tracking of changes to application settings. This promotes consistency across different environments and reduces bugs caused by inconsistent configurations.

- 12-factor app compliance: the folder structure ensures adherence to the 12-factor app principles, with all configuration parameters stored as environment variables. This approach guarantees code consistency across developer laptops, dev clusters, and prod clusters, minimizing issues stemming from configuration discrepancies.

- optimal architectural quanta: the folder structure supports the concept of optimal architectural quanta, where each folder, such as training, prediction and monitoring, represents an independent and deployable component. This modularity allows for the independent deployment and replacement of various ML components, enhancing flexibility, scalability, and maintainability.

- auto-generated CI/CD pipelines for model deployment: the folder structure facilitates the automatic generation of CI/CD pipelines specifically designed for model deployment. These pipelines include an integrated man-in-the-loop approval workflow, ensuring a controlled and seamless process for deploying ML models. This automation streamlines the deployment workflow, improves efficiency, and promotes collaboration among data scientists, developers, and other stakeholders involved in the model deployment process.
