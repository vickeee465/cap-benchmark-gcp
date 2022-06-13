from google.cloud import bigquery
from google.cloud import storage
from google.oauth2 import service_account


credentials = service_account.Credentials.from_service_account_file('../gcp_key.json')
bq_client = bigquery.Client(credentials=credentials)
storage_client = storage.Client(credentials=credentials)
