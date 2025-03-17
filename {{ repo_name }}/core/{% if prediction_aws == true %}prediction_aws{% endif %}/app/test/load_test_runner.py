import os
import json
import yaml
import time
from datetime import datetime

import boto3

from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from gcp_tools_lite.logging_tools import configure_logger
from gcp_tools_lite.utils.config_tools import TemplateConfigs, get_config_dirs, get_env


class LoadTestRunner:
    def __init__(self):
        # Load configurations and initialize logger
        self.configs = TemplateConfigs()
        self.configs.get("metadata_config").gcp_service = "infrastructure"
        self.logger = configure_logger()
        self.run_env, self.domain_env = get_env()
        self.sleep_time = float(os.getenv('SLEEP_TIME', 5))
        self.num_of_retries = os.getenv('NUM_OF_RETRIES', 5)
        
        self.logger.info(f"Environment: {self.run_env}, {self.domain_env}")

        # Load AWS configuration
        self.region = self.configs.get('prediction_aws_config').get("aws_infra_config").get("region")
        self.account_id = self.configs.get('prediction_aws_config').get("aws_infra_config").get("project_id")
        self.endpoint_test_config = self.configs.get('prediction_aws_config').get("endpoint_test_config")
        self.model_test_bucket = self.endpoint_test_config.model_test_bucket
        
        # AWS clients
        self.s3_client = boto3.client('s3')
        self.step_functions_client = boto3.client('stepfunctions')
        self.step_function_arn = os.getenv(
            "STEP_FUNCTION_ARN", 
            f"arn:aws:states:{self.region}:{self.account_id}:stateMachine:load-test-{domain_env}"
        )
        lambda_config = Config(connect_timeout=900, read_timeout=900, retries={'max_attempts': 2})
        self.lambda_client = boto3.client('lambda', config=lambda_config)
        self.load_test_function_name = f'arn:aws:lambda:{self.region}:{self.account_id}:function:aws-health-check-{domain_env}'
        
        # Derived configurations
        self.run_id = datetime.now().strftime("%Y%d%m%HH%MM%SS")
        self.execution_id = f"{self.configs.get('project_config').experiment_name}-execution-{self.run_id}"

        self.run_bucket = f"s3://{self.model_test_bucket}/model_endpoint/{self.configs.get('project_config').experiment_name}/{self.run_id}"
        self.result_path = f"{self.run_bucket}/reports"
        self.namespace = f"nba-ml-model.private-{domain_env}"
        if domain_env == "prod":
            self.namespace = f"{self.configs.get('project_config').experiment_name}-ns.private-{self.domain_env}"


    def upload_yaml_to_s3(self):
        try:
            yaml_key = f"model_endpoint/{self.configs.get('project_config').experiment_name}/{self.run_id}/payload.yaml"

            self.s3_client.put_object(
                Bucket=self.model_test_bucket, 
                Key=yaml_key, 
                Body=yaml.dump(self.configs.get("aws_endpoint_payload").toDict())
            )
            yaml_s3_uri = f"s3://{self.model_test_bucket}/{yaml_key}"
            self.logger.info(f"Uploaded YAML to S3: {yaml_s3_uri}")
            return yaml_s3_uri
        except (BotoCoreError, ClientError, FileNotFoundError) as e:
            self.logger.error(f"Failed to upload YAML to S3: {e}")
            raise RuntimeError("YAML upload failed") from e

    def prepare_step_function_input(self, yaml_s3_uri):
        return {
            "TargetEndpoint": f"http://{self.configs.get('project_config').experiment_name}-svc-dis-{self.domain_env}.{self.namespace}:8080/predict",
            "Payload": yaml_s3_uri,
            "S3ResultPath": self.result_path,
            "StartDuration": self.endpoint_test_config.start_duration,
            "RampUpDuration": self.endpoint_test_config.ramp_up_duration,
            "RampDownDuration": self.endpoint_test_config.ramp_down_duration,
            "InitialUsers": self.endpoint_test_config.initial_users,
            "RampUpUsers": self.endpoint_test_config.ramp_up_users,
            "RampDownUsers": self.endpoint_test_config.ramp_down_users
        }

    def execute_step_function(self, step_function_input):
        try:            
            response = self.step_functions_client.start_execution(
                stateMachineArn=self.step_function_arn,
                input=json.dumps(step_function_input),
                name=self.execution_id
            )
            self.logger.info(f"Step Function started successfully. Execution ARN: {response['executionArn']}")
            
            return response['executionArn']
        except (BotoCoreError, ClientError) as e:
            self.logger.error(f"Step Function execution failed: {e}")
            raise RuntimeError("Step Function execution failed") from e
    
    def wait_for_execution(self, execution_arn, poll_interval=10):
        """Waits for the Step Function execution to complete."""
        self.logger.info(f"Waiting for Step Function execution to complete: {execution_arn}")
        while True:
            try:
                response = self.step_functions_client.describe_execution(executionArn=execution_arn)
                status = response["status"]
                self.logger.info(f"Execution status: {status}")
                
                if status in ["SUCCEEDED", "FAILED", "TIMED_OUT", "ABORTED"]:
                    return status
                time.sleep(poll_interval)
            except Exception as e:
                self.logger.error(f"Failed to describe execution: {e}")
                raise RuntimeError("Error while waiting for Step Function execution") from e
    
    def download_results(self, s3_path, local_dir):
        """Downloads results from the given S3 path to a local directory."""
        try:
            bucket_name, prefix = s3_path.replace("s3://", "").split("/", 1)
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)

            os.makedirs(local_dir, exist_ok=True)
            for page in pages:
                for obj in page.get('Contents', []):
                    key = obj['Key']
                    local_file = os.path.join(local_dir, os.path.basename(key))
                    self.s3_client.download_file(bucket_name, key, local_file)
                    self.logger.info(f"Downloaded: {key} -> {local_file}")
        except (BotoCoreError, ClientError) as e:
            self.logger.error(f"Failed to download results from S3: {e}")
            raise RuntimeError("Failed to download results") from e

    def invoke_health_check(self):
        test_result = False
        function_request = {
            "operation": "model_health_check",
            'endpoint': f"http://{self.configs.get('project_config').experiment_name}-svc-dis-{self.domain_env}.{self.namespace}:8080/live",
        }

        for _ in range(self.num_of_retries):
            try:
                self.logger.info(f"Sleeping for {self.sleep_time} seconds before Invoking health check...")
                time.sleep(self.sleep_time)
                
                response = self.lambda_client.invoke(
                    FunctionName=self.load_test_function_name,
                    InvocationType='RequestResponse',
                    Payload=json.dumps(function_request).encode('utf-8')
                )
                    
                response['Payload'] = json.loads(response['Payload'].read())
                self.logger.info(f'model_health_check response: {response}')

                if not response['Payload']['endpoint_up']:
                    raise ValueError(f'model_health_check failed, response:', response)

                test_result = True
                break
            except Exception as e:
                self.logger.info(
                    '############### Failed #################\n'
                    f'{e}\n'
                    '########################################\n'
                )
        
        return test_result

    def run(self, local_results_dir):
        try:
            health_check_success = self.invoke_health_check()

            if health_check_success is True:
                # Upload YAML to S3 and get its URI
                yaml_s3_uri = self.upload_yaml_to_s3()
                
                # Prepare input for Step Function
                step_function_input = self.prepare_step_function_input(yaml_s3_uri)
                self.logger.info(f"Step Function Input: {step_function_input}")
                
                # Execute Step Function
                execution_arn = self.execute_step_function(step_function_input)

                status = self.wait_for_execution(execution_arn)
                if status != "SUCCEEDED":
                    raise RuntimeError(f"Step Function execution failed with status: {status}")

                self.download_results(self.result_path, local_results_dir)           
            else:
                raise RuntimeError("Health check failure - Can't run load test until endpoint is healthy.")
        except RuntimeError as e:
            self.logger.error(f"Execution failed: {e}")
            raise 


if __name__ == "__main__":
    run_env, domain_env = get_env()
    local_results_dir = os.getenv("LOCAL_RESULTS_DIR")

    runner = LoadTestRunner()
    runner.run(local_results_dir)
