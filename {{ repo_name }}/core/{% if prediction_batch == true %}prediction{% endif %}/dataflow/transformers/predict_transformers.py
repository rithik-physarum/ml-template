"""
# -------------------------------------------------------------
# PYTHON File
# NOTE: 
#   - DO NOT EDIT sections marked as [DO NOT EDIT]
#   - Sections without this mark can be modified as needed.
# -------------------------------------------------------------
Prediction Beam transformer.
"""

# [CAN EDIT] - All

import pytz

import apache_beam as beam
from datetime import datetime
import numpy as np
import pandas as pd
from typing import List

from gcp_tools_lite.data_tools.storage_tools import StorageHelper
from gcp_tools_lite.utils.io import get_artifact

time_zone = pytz.timezone("Europe/London")


class PredictTransformer(beam.DoFn):
    """
    Beam Transformer class to score a single transformed row of data.

    Methods
    -------
    setup()
        Downloads model to be used in every scoring iteration.
        Runs once at the start of scoring pipeline

    process()
        Scores model and creates results dictionary that will
        be saved in desired sink location, i.e. BQ or Google Cloud Storage

    """

    def __init__(
        self,
        repo_name: str,
        artifact_uri: str,
        entity_list: List[str],
        num_feature_list: List[str],
        reference_list: List[str],
        brand: str,
        key_type: str,
        output_type: str,
    ):
        self.repo_name = repo_name
        self.artifact_uri = artifact_uri
        self.entity_size = len(entity_list)
        self.feature_list = reference_list[self.entity_size:]
        self.num_feature_list = num_feature_list
        self.brand = brand
        self.key_type = key_type
        self.key_index = entity_list.index(self.key_type)
        self.output_type = output_type

    def setup(self):
        """
        Set up a predict transformer.

        Instantiate once at the start of the scoring pipeline, preventing
        loading the model with every row that needs to be scored.

        """
        self.model = get_artifact(self.artifact_uri)
        # Set create_date once during setup to avoid repeats
        self.create_date = datetime.now(time_zone).strftime("%Y-%m-%d")

    def process(
        self,
        inputs: list,
    ):
        """
        Process method.

        This function takes an inputted preprocessed row of data,
        represented as a dictionary, and creates a model prediction for
        that row.

        Parameters
        ----------
        inputs : List
            List of inputs to be scored.

        Returns
        -------
        results : dict
            Model output results

        """
        # Get the model prediction from inputs
        # Because the model included one-hot-encoding, 
        # sadly we need to get pandas dataframe.
        _inputs = pd.DataFrame(inputs[:, self.entity_size:], columns=self.feature_list)
        # Handling the data type, because the batch could get 
        # all 0 in some numeric columns.
        _inputs.loc[:, self.num_feature_list] = _inputs.loc[:, self.num_feature_list]\
                                                       .fillna(0).astype(float)

        preds = self.model.predict(_inputs)
        results = np.column_stack(
            (
                inputs[:, :self.entity_size],
                np.full((inputs.shape[0], 1), self.repo_name.upper()),
                np.full((inputs.shape[0], 1), self.brand.upper()),
                np.full((inputs.shape[0], 1), self.key_type.upper()),
                inputs[:, self.key_index],
                preds,
                np.full((inputs.shape[0], 1), self.output_type.upper()),
                np.full((inputs.shape[0], 1), self.create_date),
                np.full((inputs.shape[0], 1), self.create_date)
            )
        )
        yield results
