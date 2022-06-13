import json

import google.api_core.exceptions
from google.cloud import bigquery

from creditentials import storage_client, bq_client


def create_dataset(dataset_uri: str):
    """
    Creates empty dataset.

    :param dataset_uri: URI of dataset to be created
    :return: created dataset
    """
    dataset = bigquery.Dataset(dataset_uri)
    dataset.location = "US"
    dataset = bq_client.create_dataset(dataset)
    print('   ---> dataset created successfully: ' + dataset_uri)
    return dataset


def create_schema_from_json(path: str):
    """
    Creates a list of SchemaField objects from JSON files for the external table configuration.

    :param path: path of folder containing JSON schema files
    :return: list of SchemaField objects
    """
    schema_bq = list()
    with open(path) as file:
        columns = json.load(file)
        for col in columns:
            schema_bq.append(bigquery.SchemaField(col['name'], col['type'], col['mode']))
    return schema_bq


def create_table(src_uri: str, table_uri: str, schema: list):
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
    external_config.schema = schema
    table.external_data_configuration = external_config
    try:
        table = bq_client.create_table(table)
        print('   ---> table created successfully: ' + table_uri)
    except google.api_core.exceptions.Conflict:
        print('   ---> table already exists: ' + table_uri)
    return table


def create_cap_tables(bucket: str, project: str, dataset: str, schemas: str):
    """
    Creates tables from files in storage bucket.
    If the dataset is missing, it creates one as well.

    :param schemas: folder containing schema information
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
        table_uri = '{}.{}.{}'.format(project, dataset, blob.name.split('.')[0])
        schema = create_schema_from_json(schemas + '/' + blob.name.split('.')[0] + '.json')
        tables.append(create_table(src_uri, table_uri, schema))
    print('   All tables are up to date!')
    return tables
