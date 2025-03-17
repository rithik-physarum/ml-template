# Black & Flake8 Formatting

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
- [Deployment](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/deployment.md)
- **[Formatting Code](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/formatting-code.md)**
- [Copier Update](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/copier-update.md)
- [Release Notes](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/CHANGELOG.md)

Black is a formatting package and Flake8 is a linter package. Once you have set up your repository with these tools, every commit you make will need to conform to their standards. Any commits that are attempted to files that are incorrectly formatted will be rejected and you will need to make the necessary adjustments.

## 1 Formatting Prerequisites 
### 1.1 Install packages

In your preferred virtual environment install the following packages:

```
pip install pre-commit 'black[jupyter]' flake8 flake8-docstrings
```

### 1.2 Pre-commit setup

In your repositories root directory create a `.pre-commit-config.yaml` file and add the following code:

```
repos:
  - repo: local
    hooks:
    - id: black-jupyter
      name: black-jupyter
      description: "Black: The uncompromising Python code formatter (with Jupyter Notebook support)"
      entry: black
      language: python
      minimum_pre_commit_version: 2.9.2
      require_serial: true
      types_or: [python, pyi, jupyter]
      additional_dependencies: [".[jupyter]"]
    - id: flake8
      name: flake8
      additional_dependencies: [flake8-docstrings]
      entry: flake8
      language: python
      types: [python]
```

To activate your pre-commit config, run the following:

```
pre-commit install
```

### 1.3 Flake8 setup

In your repositories root directory create another file `.flake8` and add the following code:

```
[flake8]
extend-ignore = E203
max-line-length = 88
docstring-convention = numpy
```

## 2 Formatting Usage

To format your individual files, simply run:

```
black <path/to/file/file-name>
flake8 <path/to/file/file-name>
```

Alternatively, you can format entire directories by running:

```
black <path/to/directory>
flake8 <path/to/directory>
```

Black will rigorously format your code to conform to it's strict standards and flake8 will lint your file reviewing it and printing issues it has with your code. 