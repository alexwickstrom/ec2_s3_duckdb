import os
import pandas as pd
import boto3

from botocore.exceptions import ClientError
from config import make_postgres_connection, get_s3_client
from models import tables
from time import sleep


def dump_table_to_minio(cursor, table_name, bucket_name):
    # Fetch data from MySQL into a Pandas DataFrame
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql(query, con=cursor.connection)

    # Save the DataFrame to a Parquet file
    parquet_file = f"{table_name}.parquet"
    df.to_parquet(parquet_file, engine="pyarrow")

    # Initialize MinIO client
    minio_client = get_s3_client()
    ensure_bucket_exists(minio_client, bucket_name)
    # Upload Parquet file to MinIO bucket
    minio_client.upload_file(
        Filename=parquet_file, Bucket=bucket_name, Key=f"{table_name}/{parquet_file}"
    )


def ensure_bucket_exists(client, bucket_name):
    try:
        client.head_bucket(Bucket=bucket_name)
    except ClientError:
        # The bucket does not exist or you have no access. Create it.
        client.create_bucket(Bucket=bucket_name)


# MySQL and MinIO configurations

bucket_name = "my-bucket"

# Establish MySQL connection and cursor
if __name__ == "__main__":
    sleep(5)
    connection = make_postgres_connection()
    cursor = connection.cursor()

    cursor.execute("SET search_path TO public;")
    # Dump each table to MinIO
    for table in tables:
        print("Replicating {} to Parquet...".format(table))
        dump_table_to_minio(cursor, table, bucket_name)

    # Close the MySQL cursor and connection
    cursor.close()
    connection.close()
