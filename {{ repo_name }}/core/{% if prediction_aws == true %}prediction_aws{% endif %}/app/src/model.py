from fastapi import FastAPI, HTTPException
import os
import time

from mlops_decorators.core.model_serving import MLModel


class Model(MLModel):
    def __init__(self, name: str, artifacts: str, feature_store_client = None, **kwargs):
        """CUstom model class to load and predict on model.
        Parameters
        ----------
            name: str
                Name of the model.
        """
        import joblib
        import numpy as np
        from gcp_tools_lite.api import StorageHelperV2

        self.name = name
        self.np = np
        self.joblib = joblib
        self.model = None
        self.artifacts = artifacts
        self.feature_store_client = feature_store_client
        self.storage_helper = StorageHelperV2()
        _is_ready = False

    def load_model(self):
        """
        Function to load the model at the provided path and assign to self model
        Parameters
        ----------
        """
        
        model_local_filename = self.artifacts.get("model_object")["local_filename"]
        model_local_path = os.path.join(
            os.getenv('ARTIFACT_LOCATION', '/home/artifacts'),
            "model_object",
            model_local_filename
        )

        self.model = self.storage_helper.load(model_local_path)

        self._is_ready = True

    async def preprocess(self, input_request: dict):
        """
        Function to preprocess the input request to make it ready for the model input
        Parameters
        ----------
        input_request : dict
            Input request sent to the endpoint.

        Returns
        -------
        dict
            Returns the preprocessed data - data ready for model prediction
        """
        return input_request

    async def predict(self, data: dict):
        """
        Function to run the model prediction over the data and return the predicted results
        Parameters
        ----------
        data : dict
            Preprocessed data ready for model prediction.

        Returns
        -------
        dict
            Returns the model prediction
        """
        data = data.get("instances")
        model_input = []
                       
        for row in data:
            if "entity" in row:
                if self.feature_store_client:
                    ofs_features = self.feature_store_client.reads({"entity": row["entity"]})
                    row.update(ofs_features)
            model_input.append([row.get(feature) for feature in self.model.feature_names_in_])
        
        predictions = self.model.predict(self.np.asarray(model_input)).tolist()

        output = {
            "predictions": predictions
        }

        return output

    async def postprocess(self, output: dict):
        """
        Function to run some postprocessing on the output to make it ready as a server response
        Parameters
        ----------
        output : dict
            Model prediction results.

        Returns
        -------
        dict
            Postprocessed model predictions on the input data
        """
        return output

