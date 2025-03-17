# Copier Update

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
- [Formatting Code](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/formatting-code.md)
- **[Copier Update](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/copier-update.md)**
- [Release Notes](https://gitlab.agile.nat.bt.com/CDATASCI/gcp/templates/ml-template/-/blob/main/docs/CHANGELOG.md)

---

## Introduction

`copier update` helps you synchronize your project with the latest version of the ml-template. This guide provides a detailed step-by-step process to update your project, handle conflicts, and incorporate new changes effectively.

## 1. Package Installation

Install the required packages:

```bash
pip install copier==9.1.0
pip install pyyaml-include==1.4.1
```

Ensure you use the specified versions to avoid compatibility issues.

## 2. Update the ml-template Repository

Ensure your local copy of the `ml-template` is up to date before running the update:

```bash
cd ml-template
git pull
cd ..
```

This step guarantees that you are updating your project using the latest template version.

## 3. Review `.mlops-answers.yml`

Navigate to your project’s root directory and open the `.mlops-answers.yml` file:

```bash
cd <your-repo-name>
cat .mlops-answers.yml
```

This file contains your project configuration. Review the answers and update any fields if necessary.

### Check `_src_path`

If you are using an older version of the template, ensure `_src_path` is set correctly:

```yaml
_src_path: ../ml-template/
```

An incorrect `_src_path` can cause the update process to fail.

## 4. Steps to Run Copier Update

### Step 1: Backup Your Current Work

Create a backup commit to save your current state:

```bash
git add .
git commit -m "Backup before Copier update"
```

This provides a restore point in case the update introduces issues.

### Step 2: Preview Changes with `git diff`

Before starting the update, run:

```bash
git diff
```

This command helps you understand the changes in your code that may be impacted by the update.

### Step 3: Run the Copier Update Command

Start the update process using:

```bash
copier update --trust -a .mlops-answers.yml
```

- **`--trust`**: Allows the update to proceed without additional prompts.
- **`-a .mlops-answers.yml`**: Specifies your configuration file.

To update to a specific template version (e.g., `v2.0.0`):

```bash
copier update --vcs-ref v2.0.0 --trust -a .mlops-answers.yml
```

### Step 4: Review Prompts and Diffs

Copier might prompt you with new questions if the template has changed. Review these questions carefully. To see a preview of changes without applying them:

```bash
copier update --diff
```

This helps you inspect the modifications before they are made.

### Step 5: Resolve Merge Conflicts

After the update, check for conflicts:

```bash
git status
```

Conflicted files will have markers like this:

```text
<<<<<< before updating
your_existing_code()
======
new_template_code()
>>>>>> after updating
```

Manually resolve these conflicts, then mark the files as resolved:

```bash
git add <conflicted_file>
git commit -m "Resolved conflicts during Copier update"
```

### Step 6: Review and Finalize Changes

Use `git diff` to review all changes made during the update:

```bash
git diff
```

Decide if any adjustments are needed before proceeding.

### Step 7: Commit the Update

After reviewing all changes and resolving conflicts, commit the update:

```bash
git add .
git commit -m "Copier update to v<ml-template-version>"
git push origin main
```

This final commit should include all resolved changes from the update process.

---
## 5 Aborting an update¶
When you're not happy with the result of a copier update run or unsure about adding the introduced changes to your code base, specifically when you have unpleasant conflicts, it's not 100% obvious how to get back to the previously clean copy of your branch. 

**The following strategies won't work**:

```bash
git checkout <branch> # error: you need to resolve your current index first
git checkout . # error: path '<filename>' is unmerged
git merge --abort # fatal: There is no merge to abort (MERGE_HEAD missing)
```

Here is what you can do using Git in the terminal to throw away all changes:
```bash
git reset           # throw away merge conflict information
git checkout .      # restore modified files
git clean -d -i     # remove untracked files and folders
```
If you want fine-grained control to restore files selectively, read the output of the git status command attentively. It shows all the commands you may need as hints!

## 6. Post-Update Checklist

### 6.1 Unmerged Paths

These files have conflicts that require manual resolution. Use Git markers to guide your decisions, then commit the resolved files.

### 6.2 Changes Not Staged for Commit

These changes do not conflict with your code but should be reviewed. Use:

```bash
git diff
```

Decide whether to accept or discard these updates.

### 6.3 Untracked Files

These are new files added by the template. To include them:

```bash
git add .
```

### 6.4 Final Commit

After resolving all issues and reviewing changes, make a final commit:

```bash
git commit -m "Applied Copier update for ml-template v<ml-template-version>"
```

---


## 7. Additional Tips

- **Dry-Run Mode**: Preview changes without applying them:

  ```bash
  copier update --pretend
  ```

- **Verbose Logging**: Get detailed logs for debugging:

  ```bash
  copier update --verbose
  ```

- **Interactive Mode**: Re-answer all prompts during the update:

  ```bash
  copier update --replay
  ```

- **Read the Changelog**: Review the template’s release notes to understand major changes.

---
## 8. Troubleshooting 

When updating a project using **Copier**, there are two main categories of issues: **Breakable Changes** and **Non-Breakable Changes**. The following guide will help you troubleshoot common problems that arise during updates, and provide commands for resolving issues using Git, Copier, and other tools.

For troubleshooting these kind of issues, Kindly follow the [Troubleshooting Guide](./troubleshoting.md)