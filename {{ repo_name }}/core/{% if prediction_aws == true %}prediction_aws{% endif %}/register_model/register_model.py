from decimal import Decimal
from io import BytesIO
import json
import logging
import os
from pprint import pprint
import requests
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class ModelRegistry:
    def __init__(self):
        """
        Initialize the ModelRegistry.

        Attributes
        ----------
        dyn_resource : boto3.resources.factory.dynamodb.ServiceResource
            The DynamoDB resource.
        table : boto3.resources.factory.dynamodb.Table
            The DynamoDB table.
        """
        self.dyn_resource = boto3.resource("dynamodb", region_name="eu-west-2")
        self.table = None

    def exists(self, table_name):
        """
        Determines whether a table exists. As a side effect, stores the table in
        a member variable.

        Parameters
        ----------
        table_name : str
            The name of the table to check.

        Returns
        -------
        bool
            True when the table exists; otherwise, False.
        """
        try:
            table = self.dyn_resource.Table(table_name)
            table.load()
            exists = True
        except ClientError as err:
            if err.response["Error"]["Code"] == "ResourceNotFoundException":
                exists = False
            else:
                logger.error(
                    "Couldn't check for existence of %s. Here's why: %s: %s",
                    table_name,
                    err.response["Error"]["Code"],
                    err.response["Error"]["Message"],
                )
                raise
        else:
            self.table = table
        return exists

    def register(self, model_name, model_uri, model_cluster):
        """
        Adds a model to the table.

        Parameters
        ----------
        model_name : str
            The unique id of the model.
        model_uri : str
            The cloud function uri of the model.
        model_cluster : str
            The cluster where the model is deployed.

        """
        try:
            self.table.put_item(
                Item={
                    "model_name": model_name,
                    "model_uri": model_uri,
                    "model_cluster": model_cluster,
                }
            )
        except ClientError as err:
            logger.error(
                "Couldn't register model %s to table %s. Here's why: %s: %s",
                model_name,
                self.table.name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise

    def get_model(self, model_name):
        """
        Gets model from the table.

        Parameters
        ----------
        model_name : str
            The unique name of the model.

        Returns
        -------
        dict
            The data of the requested model.
        """
        try:
            response = self.table.get_item(Key={"model_name": model_name})
        except ClientError as err:
            logger.error(
                "Couldn't get model %s from table %s. Here's why: %s: %s",
                model_name,
                self.table.name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
        else:
            return response["Item"]


table_name = os.getenv("MODEL_TABLE", "nba-model-registration-testing")

registry = ModelRegistry()
registry.exists(table_name)
model_service_dicovery = json.loads(os.getenv("MODEL_ENDPOINTS", "'{}'")[1:-1])
model_namespace = json.loads(os.getenv("MODEL_NAMESPACES", "'{}'")[1:-1])
model_service = json.loads(os.getenv("MODEL_SERVICES", "'{}'")[1:-1])
model_cluster = os.getenv("MODEL_DEPL_CLUSTER")[1:-1]

model_url = (
    f"http://{model_service_dicovery['name']}.{model_namespace['name']}:8080/predict"
)
print("model_url set in the env are :- ", model_url)

registry.register(model_service["name"], model_url, model_cluster)
