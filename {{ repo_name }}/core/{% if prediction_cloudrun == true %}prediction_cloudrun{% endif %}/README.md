# Cloud run model deployment

This project contains terraform code to create and deploy cloud run in GCP project : **bt-bvp-ml-plat-ai-pipe-exp** with CI/CD pipeline using gitlab runner.The cloud run contains a online deloyed model and the load and predict code for model deployment.

## Changes

In prediction/prediction_cloudrun/app/online_prediction folder:-

In **config.py**:-

Load all the required environment variables in the __init__ method in the Config class.

In **predict_hanlder.py**:-

In load_model write the code to download the model from gcs and load the model and assign the model to self.model, the model path is in the self.model_path variable and in self.model_name is the name for the model.

In predict method write the code to do the prediction and reture the response for one instance in the request.
ex:- 

    def predict(self, instance):

        prediction = self.model.predict(instance)
    
        return prediction

In **model.py**:-

Use this class to store the MODEL CLASS used to load a model.

In **requirements.txt**:-

Add the additional requirements below user defined requirements in this file.

In prediction/prediction_cloudrun/terraform folder:-

In **exp.tfvars**:-

Add additional environment variables in the **env_vars** list. Each value in the env_vars list is the combination of name and value pair.
Name is the env variable name and value is the value for the environment variable.

Example:-

{"name": "SAMPLE_VARIABLE", "value": "SAMPLE_VALUE"}

SAMPLE_VARIABLE is the variable to be user in the code to get the value and SAMPLE_VALUE is the value for the SAMPLE_VARIABLE.

## CICD

Gitlab CI/CD runner is used to deploy the cloud run using terraform modules.
To change the deployment config one can change the **{environment name}.tfvars.json**.


## To trigger the deployed cloud run

curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" https://{CLOUD_RUN_URL}/ -X POST -d '{}'
