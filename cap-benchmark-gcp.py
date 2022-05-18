import pandas as pd
import os
import sys
import openpyxl
import google
from google.cloud import bigquery
from google.cloud import storage
import tqdm
import configparser


def search_for_key(filename):
    files = os.listdir()
    if filename not in files:
        raise Exception('Private key for Service Account not found. Is it in the same directory as the script?')
    return filename


def load_config(filename):
    config = configparser.ConfigParser()
    config.read(filename)

    path = config['arguments']['path'].strip('\n')
    project = config['arguments']['project'].strip('\n')
    bucket = config['arguments']['bucket'].strip('\n')
    dataset = config['arguments']['dataset'].strip('\n')

    return path, project, bucket, dataset


def xlsx2jsonl(path):
    """
    Converts CAP data from .xlsx to .jsonl.

    :param path: folder containing .xlsx files
    :return: None
    """
    path += "\\"
    files = os.listdir(path)
    files = [file for file in files if file.endswith(".xlsx") and not file.startswith("~$")]
    for file in tqdm.tqdm(files, desc='1. Converting files in ' + os.path.abspath(path)):
        sheet = int(file.startswith("party_name_full"))
        df = pd.read_excel(path + file, sheet_name=sheet)
        df = df.assign(**df.select_dtypes(['datetime']).astype(str).to_dict('list'))
        df = df.replace('"', '\"', regex=True)
        df.columns = df.columns.str.replace(' ', '')
        df.columns = df.columns.str.replace('Unnamed:', 'unnamed_')
        df.to_json(path + file.split('.')[0] + '_bq.jsonl', orient="records", lines=True, force_ascii=False)


def create_bucket(bucket_name):
    """
    Creates empty bucket.

    :param bucket_name: Storage bucket name
    :return: created bucket
    """
    bucket = storage_client.bucket(bucket_name)
    bucket.storage_class = "STANDARD"
    bucket = storage_client.create_bucket(bucket, location="us")
    print('   ---> bucket created successfully: ' + bucket_name)
    return bucket


def upload_to_bucket(bucket_name, blob_name, file_path):
    """
    Uploads file to Storage bucket.

    :param bucket_name: Storage bucket name
    :param blob_name: filename in bucket
    :param file_path: file to be uploaded
    :return: blob
    """
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)

    # for slow upload speed
    blob._DEFAULT_CHUNKSIZE = 2097152  # 1024 * 1024 B * 2 = 2 MB
    blob._MAX_MULTIPART_SIZE = 2097152  # 2 MB
    # very large file and/or slow upload speed might still cause exception

    blob.upload_from_filename(file_path)
    return blob


def upload_cap_data(folder_path, bucket_name):
    """
    Uploads all .jsonl files.
    If the bucket is missing it creates one as well.

    :param folder_path: folder containing .jsonl files
    :param bucket_name: storage bucket name
    :return: None
    """
    try:
        storage_client.get_bucket(bucket_name)
    except google.api_core.exceptions.NotFound:
        create_bucket(bucket_name)

    folder_path += "/"
    files = os.listdir(folder_path)
    files = [file for file in files if file.endswith(".jsonl") and not file.startswith("~$")]
    for file in tqdm.tqdm(files, desc='2. Uploading files to ' + bucket_name):
        upload_to_bucket(bucket_name, file[:-9], folder_path + file)


def create_dataset(dataset_uri):
    """
    Creates empty dataset.

    :param dataset_uri: URI of dataset to be created
    :return: created dataset
    """
    dataset = bigquery.Dataset(dataset_uri)
    dataset.location = "US"
    dataset = bq_client.create_dataset(dataset, timeout=30)
    print('   ---> dataset created successfully: ' + dataset_uri)
    return dataset


def create_table(src_uri, table_uri):
    """
    Creates external table in a BigQuery dataset from Cloud Storage data.
    Only accepts newline-delimited JSON, and the table schema is autodetected.

    :param src_uri: URI of file to be uploaded (format: gs://bucket/blob)
    :param table_uri: URI of table to be created (format: project.dataset.table)
    :return: created table
    """
    table = bigquery.Table(table_uri)
    external_config = bigquery.ExternalConfig('NEWLINE_DELIMITED_JSON')
    external_config.source_uris = src_uri
    external_config.autodetect = True
    table.external_data_configuration = external_config
    try:
        table = bq_client.create_table(table)
        print('   ---> table created successfully: ' + table_uri)
    except google.api_core.exceptions.Conflict:
        print('   ---> table already exists: ' + table_uri)
    return table


def create_cap_tables(bucket, project, dataset):
    """
    Creates tables from files in storage bucket.
    If the dataset is missing, it creates one as well.

    :param bucket: Storage bucket name
    :param project: BigQuery project name
    :param dataset: BigQuery dataset name
    :return: list of created tables
    """
    print('3. Creating tables:')
    dataset_uri = '{}.{}'.format(project, dataset)
    try:
        bq_client.get_dataset(dataset_uri)
    except google.api_core.exceptions.NotFound:
        create_dataset(dataset_uri)
    blobs = storage_client.list_blobs(bucket)
    tables = list()
    for blob in blobs:
        src_uri = 'gs://{}/{}'.format(bucket, blob.name)
        table_uri = '{}.{}.{}'.format(project, dataset, blob.name)
        tables.append(create_table(src_uri, table_uri))
    print('   All tables are up to date!')
    return tables


if __name__ == '__main__':
    # private key for Google Cloud service account
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = search_for_key('gcp_key.json')

    # storage + bigquery client init
    storage_client = storage.Client()
    bq_client = bigquery.Client()

    # parameters as command-line arguments
    if len(sys.argv) == 5:
        path, project, bucket, dataset = sys.argv[1:]
    else:
        path, project, bucket, dataset = load_config('config.ini')

    xlsx2jsonl(path)
    upload_cap_data(path, bucket)
    create_cap_tables(bucket, project, dataset)
