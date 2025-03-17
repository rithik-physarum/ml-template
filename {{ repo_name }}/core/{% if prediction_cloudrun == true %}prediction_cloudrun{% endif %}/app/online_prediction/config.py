import os


class Config:

    """
    Use this class to read all the environment variables and
    access env variables using this class throughout.

    Attributes
    ----------
    model_path : str
        The path to the model.
    model_name : str
        The name of the model.
    experiment_name : str
        The name of the experiment.
    run_id : str
        The ID of the run.
    """

    def __init__(self):
        """
        Initialize the Config class and read environment variables.
        """
        self.model_path = os.environ.get("MODEL_PATH", "")
        self.model_name = os.environ.get("MODEL_NAME", "")
        self.experiment_name = os.environ.get("EXPERIMENT_NAME")
        self.run_id = os.environ.get("RUN_ID")
