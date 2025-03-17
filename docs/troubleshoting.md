# Troubleshooting Issues During Copier Update

When updating a project using **Copier**, there are two main categories of issues: **Breakable Changes** and **Non-Breakable Changes**. The following guide will help you troubleshoot common problems that arise during updates, and provide commands for resolving issues using Git, Copier, and other tools.

## Table of Contents

1. [Breakable Changes](#1-breakable-changes)  
    1.1. [Overwritten Critical Configuration Files](#a-overwritten-critical-configuration-files)  
    1.2. [Breaking Changes in Project Dependencies](#b-breaking-changes-in-project-dependencies)  
    1.3. [Breaking Changes in Project Structure](#c-breaking-changes-in-project-structure)  
    1.4. [Failed Copier Update Due to Conflicting Custom Files](#d-failed-copier-update-due-to-conflicting-custom-files)  
    1.5. [Issues with Missing or Invalid Git Repository State](#e-issues-with-missing-or-invalid-git-repository-state)  

2. [Non-Breakable Changes](#2-non-breakable-changes)  
    2.1. [New or Updated Documentation Files](#a-new-or-updated-documentation-files)  
    2.2. [Minor Refactoring or Code Style Changes](#b-minor-refactoring-or-code-style-changes)  
    2.3. [Template-Specific Defaults or Options](#c-template-specific-defaults-or-options)  
    2.4. [New Non-Critical Features](#d-new-non-critical-features)  

3. [Handling Unexpected Prompts for New Questions](#3-handling-unexpected-prompts-for-new-questions)  
    3.1. [Solution 1: Review and Answer New Questions](#solution-1-review-and-answer-new-questions)  
    3.2. [Solution 2: Skip New Prompts and Use Default Values](#solution-2-skip-new-prompts-and-use-default-values)  
    3.3. [Solution 3: Apply Updates Without Interaction](#solution-3-apply-updates-without-interaction)  
    3.4. [Answering Only Specific Questions](#answering-only-specific-questions)  
    3.5. [Reusing Previous Answers](#reusing-previous-answers)  

4. [General Troubleshooting Tips](#4-general-troubleshooting-tips)  
5. [Summary of Commands](#5-summary-of-commands)

---

## **1. Breakable Changes**

### a) **Overwritten Critical Configuration Files**

**Issue**:  
You might be prompted to overwrite important configuration files like `Dockerfile`, `settings.py`, or `config.yml`, which could break your custom settings.

**Solution**:  
- Review the changes carefully when prompted to overwrite.
- If you need to preserve your settings, choose to **keep your changes** instead of overwriting.
- Manually merge any necessary changes from the template into your configuration files.

**Commands**:  
```bash
# To review changes before overwriting, use the diff option
copier update --diff

# Use git to compare changes before committing
git diff
```

**Prevention**:  
- **Version Control**: Always use Git to track configuration files. This allows easy rollback in case of issues.

---

### b) **Breaking Changes in Project Dependencies**

**Issue**:  
Updates to project dependencies (e.g., `requirements.txt`, `pyproject.toml`, `package.json`) could introduce breaking changes or incompatibilities with your code.

**Solution**:  
- After the update, inspect the changes to dependencies and compare the versions with your current setup.
- Test the project thoroughly, especially areas interacting with these dependencies.
- If needed, pin dependencies to earlier versions in your configuration files.

**Commands**:  
```bash
# To inspect the diff of dependencies
copier update --diff

# Use git to check which dependencies have changed
git diff requirements.txt pyproject.toml

# If dependencies are broken, revert to the previous version using Git
git checkout HEAD^ requirements.txt
git checkout HEAD^ pyproject.toml
```

**Prevention**:  
- Test dependency updates in a separate branch before merging into your main project to ensure compatibility.

---

### c) **Breaking Changes in Project Structure**

**Issue**:  
If the template alters the project structure (e.g., renaming directories, changing module imports), your project may break due to incorrect paths.

**Solution**:  
- Review the template changes for any structural modifications.
- Adjust your project’s references to match the new structure (e.g., file paths, import paths).

**Commands**:  
```bash
# Use Git to check changes in project structure
git diff --name-status

# Manually update import paths in your code
# Example: change import from `from old_module import x` to `from new_module import x`
```

**Prevention**:  
- Document and maintain your custom project structure to easily integrate template changes.

---

### d) **Failed Copier Update Due to Conflicting Custom Files**

**Issue**:  
If you have modified template files (e.g., adding custom files) and the update introduces new versions of these files, Copier may fail or prompt you to resolve conflicts.

**Solution**:  
- Review the diff and choose to merge changes manually.
- If a file conflict arises, decide whether to keep your custom file or adopt the new template version.

**Commands**:  
```bash
# To check for file conflicts during update
copier update --diff

# If there is a conflict, use git to resolve the merge
git mergetool
```

**Prevention**:  
- Regularly commit your custom changes and resolve conflicts when updating.

---

### e) **Issues with Missing or Invalid Git Repository State**

**Issue**:  
If your Git repository has an inconsistent state (e.g., uncommitted changes or conflicts), the update might fail.

**Solution**:  
- Ensure all changes are committed or stashed before running the update.
- Resolve any conflicts or merge issues in your Git repository.

**Commands**:  
```bash
# Check the status of your Git repository
git status

# Commit all changes before updating
git add .
git commit -m "Pre-update commit"

# If there are uncommitted changes, stash them temporarily
git stash

# After update, you can apply stashed changes back
git stash pop
```

---

## **2. Non-Breakable Changes**

### a) **New or Updated Documentation Files**

**Issue**:  
New or updated documentation files (e.g., `README.md`, `CONTRIBUTING.md`) may conflict with existing documentation but won’t break functionality.

**Solution**:  
- Review new documentation files and decide whether to merge or discard them.
- If you’ve customized your documentation, manually merge the changes.

**Commands**:  
```bash
# Check the diff of documentation files
copier update --diff

# Use git to merge documentation changes
git merge
```

**Prevention**:  
- Keep documentation up-to-date and track changes in version control.

---

### b) **Minor Refactoring or Code Style Changes**

**Issue**:  
The template may introduce minor refactoring or code style changes (e.g., indentation, variable names) that don’t affect functionality but alter the formatting.

**Solution**:  
- Review changes with the diff output from Copier and selectively apply them.
- Ensure these changes don’t introduce unnecessary complexity to your code.

**Commands**:  
```bash
# Review minor code changes with Copier diff
copier update --diff

# Use Git to inspect specific files
git diff
```

**Prevention**:  
- Use a consistent code style guide (e.g., `black`, `flake8`) to apply before updating, preventing conflicts.

---

### c) **Template-Specific Defaults or Options**

**Issue**:  
New template defaults or configuration options may be added that aren’t necessary for your project.

**Solution**:  
- Review and remove any irrelevant new options or files.
- Choose to ignore these changes during the update if they are not required.

**Commands**:  
```bash
# Run the update and skip irrelevant questions using defaults
copier update --defaults
```

**Prevention**:  
- Ensure your project’s needs align with the template options to minimize unnecessary updates.

---

### d) **New Non-Critical Features**

**Issue**:  
The template might add new features that don’t affect core functionality but could expand your project’s codebase.

**Solution**:  
- Review and test new features to decide whether to integrate them.
- If they are not useful, you can choose to ignore them.

**Commands**:  
```bash
# Use the copier diff to inspect non-critical features
copier update --diff

# To skip new features and use defaults, use the --defaults flag
copier update --defaults
```

**Prevention**:  
- Review the change log or inspect new features before updating to decide whether to adopt them.

---

## **3. Handling Unexpected Prompts for New Questions**

When updating a project with a template, you may encounter new questions or options that weren't previously part of the original configuration. Below are some ways to manage these updates efficiently.

### **Solution 1: Review and Answer New Questions**
During an update, review and answer any new questions to ensure the project aligns with your current needs.

### **Solution 2: Skip New Prompts and Use Default Values**
To automatically apply default values to new questions, use the `--defaults` flag:

```bash
copier update --defaults
```

### **Solution 3: Apply Updates Without Interaction**
If you want to apply all updates without being prompted for input, use the `--force` flag. However, use this with caution, as it skips the review of individual changes:

```bash
copier update --force
```

### **Answering Only Specific Questions**

In some cases, you might want to answer only specific questions while reusing previous answers for the rest. This can be done by using appropriate flags and options to streamline the process.

- **Reuse All Previous Answers**:  
   To skip new questions and reuse all previous answers, use the `--defaults` flag:

   ```bash
   copier update --defaults
   ```

- **Update a Specific Question**:  
   If you need to change only one specific question and leave the others as-is, you can use the `--defaults` flag with the `--data` option to specify the new answer. For example, to update the `updated_question`:

   ```bash
   copier update --defaults --data updated_question="my new answer"
   ```

   Alternatively, you can use a data file to specify the changes:

   ```bash
   echo "updated_question: my new answer" > /tmp/data-file.yaml
   copier update --defaults --data-file /tmp/data-file.yaml
   ```

**Note**: Due to issue [#1474](https://github.com/copier-org/copier/issues/1474), updating multiselect choices via the `--data` flag is not supported. In such cases, the `--data-file` method must be used instead.
---  

## 4 **General Troubleshooting Tips**

- **Check the Diff**:  
  Always review the diff output when running `copier update`. It will show you what changes the template wants to apply, and you can decide which ones to accept.

- **Use Git for Version Control**:  
  Commit your changes before updating with Copier. This allows you to easily roll back to a previous state if something goes wrong.

- **Test in a Separate Branch**:  
  Run the `copier update` in a separate branch first. This lets you test the update in isolation before merging it into your main branch.

- **Manual Merging**:  
  If there are conflicts that Copier cannot automatically resolve, you may need to manually merge the changes. Using a Git merge tool or manually inspecting the conflicting files will help in resolving the issues.

- **Backup Your Project**:  
  Always create a backup of your project or ensure you have a proper version control system before updating, especially if your project involves complex configurations or critical code.

---

## 5 **Summary of Commands**

| **Action**                               | **Command**                                 |
|------------------------------------------|---------------------------------------------|
| Answer prompts interactively             | `copier update`                             |
| Skip prompts and use defaults            | `copier update --defaults`                  |
| Force an update without prompts          | `copier update --force`                     |
| Check changes before overwriting         | `copier update --diff`                      |
| Use git to check file changes            | `git diff`                                  |
| Backup database                          | `pg_dump mydatabase > backup.sql`           |
| Test migrations locally                  | `alembic upgrade head`                      |
| Resolve merge conflicts                  | `git mergetool`                             |

