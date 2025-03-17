####### TEST SCRIPT ######

"""
Usage guide - 

Run this script from prediction aws as - 
    python prediction_aws/app/test/test_local_feature_store.py

This script shows use of a dummy feature store which could be used to test in local to
check everything in the app is working fine.

data/test_data.json: Use can define their sample request in data/test_data.json.
data/test_json.json: This file provides the sample data for feature store. Use can add 
        request entities and feature map in this which would be used as source of local
        data fetch.

Model - To run this script users would have to save their model in 
        /home/artifacts/model_object/model.pkl
        or assign the artifact directory by `os.environ['ARTIFACT_LOCATION'] = ''`
        <artifact_directory>/<artifact_name>/<local_filename>
"""
from fastapi import Response
import os
import logging
import time
import sys
from gcp_tools_lite.utils.config_tools import TemplateConfigs
from gcp_tools_lite.utils import io
from dotmap import DotMap

current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_folder = os.path.join(parent_directory)

print("SRC FOLDER \n  :- ", src_folder)
sys.path.append(src_folder)

from src.handler import RequestHandler

configs = TemplateConfigs()

predict_config = DotMap(io.load_yaml(f"{current_directory}/data/test_config.yaml"))

model_config = predict_config.model_config
feature_store_config = predict_config.toDict().get("feature_store")
requests = io.load_json(f"{current_directory}/data/test_data.json")

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def initalize():
    logging.info("Initializing global resources...")
    from mlops_decorators.core.feature_api import Client
    from src.model import Model

    RequestHandler.logging = logging

    if feature_store_config is not None:
        RequestHandler.feature_store_client = Client.initialize(
            store_api = feature_store_config["store_api"], 
            config = feature_store_config["config"]
        )

    RequestHandler.model = Model(
        name=configs.get("project_config").experiment_name,
        artifacts=model_config.artifacts.toDict(),
        feature_store_client=RequestHandler.feature_store_client,
        **model_config.toDict().get("extra_init_params", {}),
    )
    RequestHandler.model.load_model()
    logging.info("Global resources initialized successfully.")

async def predict(request: dict):
    """Predict route that uses preprocess, predict, and postprocess methods."""
    process_start = time.time()

    output = await RequestHandler.predict(request)

    tt = time.time() - process_start
    logging.info(f"Total processing time: {tt:0.4f} {request}")

    if not isinstance(output, dict):
        return Response(content=output, headers={})
    
    return output

async def main():
    outputs = []
    initalize()
    for request in requests:
        result = await predict(request)
        outputs.append(result)
        print("Prediction Result: ", result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
