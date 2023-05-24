from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils import timezone

import csv
import json
import requests

# Import modules regarding GCP service account, BigQuery, and GCS
# Your code here
from google.cloud import bigquery, storage
from google.oauth2 import service_account

FILENAME_LIST = ["addresses", "products", "order-items", "promos"]
API_URL2 = f"http://34.87.139.82:8000"


# FILENAME = "addresses"
# API_URL = f"http://34.87.139.82:8000/{FILENAME}/"

DATA_FOLDER = "data"
DAG_PATH = f"/opt/airflow/dags"

BUSINESS_DOMAIN = "greenery"
LOCATION = "asia-southeast1"
PROJECT_ID = "instant-bonfire-384606"
BUCKET_NAME = "deb-bootcamp-100021"


def _extract_data():
    # Your code below
    for file in FILENAME_LIST:
        response = requests.get(f"{API_URL2}/{file}/")
        data = response.json()
        with open(f"{DAG_PATH}/{DATA_FOLDER}/{file}.csv", "w") as f:
            writer = csv.writer(f)
            header = data[0].keys()
            writer.writerow(header)

            for each in data:
                writer.writerow(each.values())


def _load_data_to_gcs():
    # Your code below

    # keyfile = os.environ.get("KEYFILE_PATH")
    keyfile = "instant-bonfire-384606-91d9ef3a9cc4-gcs.json"
    service_account_info = json.load(open(f"{DAG_PATH}/{keyfile}"))
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info)

    storage_client = storage.Client(
        project=PROJECT_ID,
        credentials=credentials,
    )
    for file in FILENAME_LIST:
        bucket = storage_client.bucket(BUCKET_NAME)
        file_path = f"{DAG_PATH}/{DATA_FOLDER}/{file}.csv"
        destination_blob_name = f"{BUSINESS_DOMAIN}/{file}/{file}.csv"
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(file_path)


def _load_data_from_gcs_to_bigquery():
    # Your code below
    keyfile_bigquery = "instant-bonfire-384606-2324e1481ccb-gcs-bigquery.json"
    service_account_info_bigquery = json.load(
        open(f"{DAG_PATH}/{keyfile_bigquery}"))
    credentials_bigquery = service_account.Credentials.from_service_account_info(
        service_account_info_bigquery
    )

    bigquery_client = bigquery.Client(
        project=PROJECT_ID,
        credentials=credentials_bigquery,
        location=LOCATION,
    )
    for file in FILENAME_LIST:
        table_id = f"{PROJECT_ID}.deb_bootcamp.{file}"
        job_config = bigquery.LoadJobConfig(
            skip_leading_rows=1,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            source_format=bigquery.SourceFormat.CSV,
            autodetect=True,
        )

        destination_blob_name = f"{BUSINESS_DOMAIN}/{file}/{file}.csv"
        job = bigquery_client.load_table_from_uri(
            f"gs://{BUCKET_NAME}/{destination_blob_name}",
            table_id,
            job_config=job_config,
            location=LOCATION,
        )
        job.result()

        table = bigquery_client.get_table(table_id)
        print(
            f"Loaded {table.num_rows} rows and {len(table.schema)} columns to {table_id}")


default_args = {
    "owner": "airflow",
    # Set an appropriate start date here
    "start_date": timezone.datetime(2023, 5, 1),
}
with DAG(
    dag_id="greenery_no_partition_data_pipeline",  # Replace xxx with the data name
    default_args=default_args,
    schedule=None,  # Set your schedule here
    catchup=False,
    tags=["DEB", "2023", "greenery"],
):

    # Extract data from Postgres, API, or SFTP
    extract_data = PythonOperator(
        task_id="extract_data",
        python_callable=_extract_data,
    )

    # Load data to GCS
    load_data_to_gcs = PythonOperator(
        task_id="load_data_to_gcs",
        python_callable=_load_data_to_gcs,
    )

    # Load data from GCS to BigQuery
    load_data_from_gcs_to_bigquery = PythonOperator(
        task_id="load_data_from_gcs_to_bigquery",
        python_callable=_load_data_from_gcs_to_bigquery,
    )

    # Task dependencies
    extract_data >> load_data_to_gcs >> load_data_from_gcs_to_bigquery
