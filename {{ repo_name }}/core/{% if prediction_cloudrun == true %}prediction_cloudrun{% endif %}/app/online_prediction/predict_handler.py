import random
import os
import re
import os.path as op
import glob
import json
import logging

from .io import gcs_helper, bq


class PredictHandler:
    def __init__(self, model_path: str, model_name: str):
        """
        Initialize the PredictHandler.

        Parameters
        ----------
        model_path : str
            The path to the model.
        model_name : str
            The name of the model.
        """
        self.model = None
        self.model_path = model_path
        self.model_name = model_name

    def load_model(self):
        """
        function to load the model and assign it to self.model
        """
        pass

    def predict(self, instance: dict):
        """
        Make a prediction for each instance.

        Parameters
        ----------
        instance : dict
            The input data for prediction.

        Returns
        -------
        The prediction result.
        """
        pass
