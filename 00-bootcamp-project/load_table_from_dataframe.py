# Ref: https://cloud.google.com/bigquery/docs/samples/bigquery-load-table-dataframe

import json
import os
from datetime import datetime

import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account


keyfile = os.environ.get("KEYFILE_PATH")
service_account_info = json.load(open(keyfile))
credentials = service_account.Credentials.from_service_account_info(service_account_info)
project_id = "instant-bonfire-384606"
client = bigquery.Client(
    project=project_id,
    credentials=credentials,
)

job_config = bigquery.LoadJobConfig(
    skip_leading_rows=0,
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    source_format=bigquery.SourceFormat.CSV,
    autodetect=True,
    # time_partitioning=bigquery.TimePartitioning(
    #     type_=bigquery.TimePartitioningType.DAY,
    #     field="created_at",
    # ),
    # clustering_fields=["first_name", "last_name"],
)

file_path = "data/addresses.csv"
# df = pd.read_csv(file_path, parse_dates=["created_at", "updated_at"])
# df = pd.read_csv(file_path, parse_dates=["created_at"])
df = pd.read_csv(file_path)
df.info()

## project_id.<DATA_SET>.<TABLE>
table_id = f"{project_id}.deb_bootcamp.addresses"
job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
job.result()

table = client.get_table(table_id)
print(f"Loaded {table.num_rows} rows and {len(table.schema)} columns to {table_id}")