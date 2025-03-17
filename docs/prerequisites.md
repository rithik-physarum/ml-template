# Prerequisites

### Table of Contents
- [Home](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/README.md)
- **[Prerequisites](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/prerequisites.md)**
- [GCP Dataset and IAM access prerequisites](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/dataset-access.md)
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

In order to use this template you must have a GCP account and Vertex AI Workbench notebook instance.

**Note:** please beaware that notebook instances in the bvp-ml-platform space are routinely shutdown daily at 7pm, any work done after 7pm that is not saved will be lost.
 
### **1 Authenticate yourself**

You need to do this whenever you start a new terminal, including at the start of every day. There are two gcloud commands below and you need to do both every time.

```
gcloud auth application-default login --no-launch-browser
gcloud auth login --no-launch-browser
```

 - When prompted do you want to continue, enter y to continue
 - Copy and paste the https link into your browser
 - Sign in using your BT google account
 - Scroll down and click Allow
 - Copy and paste the Authorization code into the terminal

```
git config --global user.name "<user-name>"
git config --global user.email <user-email>
```

Click [here](shell_files/initialise.sh) to download an `initialise.sh` script containing the above commands that you should run first thing every day to initialise your instance. Simply copy this into your home directory, update the git configs appropriately and run:

```
bash initialise.sh
```

### 2 Installs
It is recommended you use a virtual environment for your packages. Any packages installed outside of a virtual environment will be lost when your instance is shut down and you will need to reinstall the package again if you need it. 

A virtual environment guide will be added to this page soon, for now please see **[this](https://www.collab.bt.com/confluence/display/DI/Virtual+Environment+Guide)** documentation.

#### 2.1 Installing copier to run the ml-template

```
pip install copier>=9.3.1
# You may need the extensions
pip install copier-templates-extensions>=0.3.0
pip install pyyaml-include>=1.4.1

```

#### **2.2 Installing `gcp-tools-lite`**

`gcp-tools-lite` is a package for simplifying and standarising the data science workflow on GCP. 
This includes big query tools, using Vertex AI for Model builds and storage tools for saving and loading model objects.

Repo can be found here:
https://gitlab.agile.nat.bt.com/CDATASCI/gcp/shared-libraries/gcp-tools-lite.git

To install run the following command:

```
pip install git+https://gitlab.agile.nat.bt.com/CDATASCI/gcp/shared-libraries/gcp-tools-lite.git@v0.0.36
```

