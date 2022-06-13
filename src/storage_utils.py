import os

import google.api_core.exceptions
from tqdm import tqdm

from creditentials import storage_client


def create_bucket(bucket_name: str):
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


def upload_to_bucket(bucket_name: str, blob_name: str, file_path: str):
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


def upload_cap_data(folder_path: str, bucket_name: str):
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
    for file in tqdm(files, desc='2. Uploading files to ' + bucket_name):
        upload_to_bucket(bucket_name, file, folder_path + file)
