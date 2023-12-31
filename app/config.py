import os

import boto3
import psycopg2
import pymysql
from botocore.client import Config


def make_mysql_connection():
    return pymysql.connect(
        host=os.environ.get("MYSQL_HOST"),
        user=os.environ.get("MYSQL_USER"),
        password=os.environ.get("MYSQL_PASSWORD"),
        db=os.environ.get("MYSQL_DB"),
    )


def make_postgres_connection():
    return psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "postgres"),
        port=os.environ.get("POSTGRES_PORT", 5433),
        dbname=os.environ.get("POSTGRES_DB", "mydatabase"),
        user=os.environ.get("POSTGRES_USER", "postgres"),
        password=os.environ.get("POSTGRES_PASSWORD", "mysecretpassword"),
    )


minio_config = {
    "endpoint_url": os.environ.get("S3_ENDPOINT", "http://localhost:9000"),
    "aws_access_key_id": os.environ.get("AWS_ACCESS_KEY_ID", "minio-access-key"),
    "aws_secret_access_key": os.environ.get(
        "AWS_SECRET_ACCESS_KEY", "minio-secret-key"
    ),
}


def get_s3_client(creds=minio_config):
    return boto3.client(
        "s3",
        endpoint_url=creds["endpoint_url"],
        aws_access_key_id=creds["aws_access_key_id"],
        aws_secret_access_key=creds["aws_secret_access_key"],
        config=Config(signature_version="s3v4"),
    )
