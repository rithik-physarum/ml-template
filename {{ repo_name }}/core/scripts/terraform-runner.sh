#!/bin/bash

# Function to display usage
function usage() {
    echo "Usage: $0 <module_path> <plan_path> <operation>"
    echo "Operations allowed:"
    echo "  - local: terraform plan, terraform validate"
    echo "  - ci: terraform plan, terraform apply"
    exit 1
}

# Function to run Terraform init based on the environment
function terraform_init() {
    if [ -n "$CI_COMMIT_REF_NAME" ]; then
        echo "Initializing Terraform for CI environment..."
        terraform -chdir="$MODULE_PATH" init \
            -backend-config="bucket=${TF_BUCKET}" \
            -backend-config="prefix=${TF_PREFIX}"
    else
        echo "Initializing Terraform for local environment..."
        terraform -chdir="$MODULE_PATH" init -backend=false
    fi
}

# Function to run Terraform plan
function terraform_plan() {
    local vars=$1
    local var_file=$2

    terraform_init
    echo "Running Terraform plan..."
    terraform -chdir="$MODULE_PATH" plan $vars $var_file -out="$PLAN_PATH".tfplan
    terraform -chdir="$MODULE_PATH"  validate
    terraform -chdir="$MODULE_PATH"  show -no-color "$PLAN_PATH".tfplan > "$PLAN_PATH".txt
    terraform -chdir="$MODULE_PATH"  show -json -no-color "$PLAN_PATH".tfplan > "$PLAN_PATH".json
}

# Function to run Terraform validate
function terraform_validate() {

    terraform_init
    echo "Running Terraform validate..."
    terraform -chdir="$MODULE_PATH" validate
}

# Function to run Terraform apply
function terraform_apply() {
    terraform_init
    echo "Running Terraform apply..."
    terraform -chdir="$MODULE_PATH" apply -input=false "$PLAN_PATH".tfplan
}

# Function to check if the module path exists
function check_module_path() {
    if [ ! -d "$MODULE_PATH" ]; then
        echo "Error: Module path $MODULE_PATH does not exist."
        exit 1
    fi
}

# Main function
function main() {
    if [ "$#" -lt 3 ]; then
        usage
    fi

    MODULE_PATH="$1"
    PLAN_PATH="$2"
    OPERATION="$3"
    shift 3

     # Initialize VARS and VAR_FILE variables
    VARS=""
    VAR_FILE=""

    # Check for the optional -var-file argument
    if [[ $1 == -var-file=* ]]; then
        VAR_FILE="-var-file=${1#*=}"
        shift
    fi

    # Collect additional variable arguments
    for var in "$@"; do
        VARS="$VARS -var $var"
    done

    TF_BUCKET="${TF_BUCKET:-default-bucket-name}"  # Replace with your default bucket name
    TF_PREFIX="${TF_PREFIX:-default/prefix}"       # Replace with your default prefix

    check_module_path

    if [ -n "$CI_COMMIT_REF_NAME" ]; then
        # Running in GitLab CI
        case "$OPERATION" in
            plan)
                terraform_plan "$VARS" "$VAR_FILE"
                ;;
            apply)
                terraform_apply
                ;;
            *)
                echo "Error: Invalid operation for CI environment. Allowed operations are: plan, apply."
                usage
                ;;
        esac
    else
        # Running locally
        case "$OPERATION" in
            plan)
                terraform_plan "$VARS" "$VAR_FILE"
                ;;
            validate)
                terraform_validate
                ;;
            *)
                echo "Error: Invalid operation for local environment. Allowed operations are: plan, validate."
                usage
                ;;
        esac
    fi
}

# Call the main function
main "$@"
