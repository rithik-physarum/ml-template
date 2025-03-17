import os

from gcp_tools.data_tools.storage_tools import StorageHelper
from gcp_tools.data_tools.bigquery_tools import Querier

gcs_helper = StorageHelper()
bq = Querier(querier_project=os.getenv("PROJECT"))
