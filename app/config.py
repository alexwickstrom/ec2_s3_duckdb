import os

import boto3
import psycopg2
import pymysql
from botocore.client import Config

env_profile = "PROD"
BASE_SCHEMA = "chronometer_production"

tables = [
    "chronometer_doctor",
    "chronometer_patient",
    "chronometer_office",
    "chronometer_appointment",
    "billing_billinglineitem",
    "billing_cashpayment",
    "billing_lineitemtransaction",
]


def make_mysql_connection():
    return pymysql.connect(
        host=os.environ.get("MYSQL_HOST"),
        user=os.environ.get("MYSQL_USER"),
        password=os.environ.get("MYSQL_PASSWORD"),
        db=os.environ.get("MYSQL_DB"),
    )


def make_postgres_connection():
    if env_profile == "PROD":
        print([x for x in os.environ if "POSTGRES" in x])
        prod_credentials = {
            "host": os.environ.get("POSTGRES_HOST_PROD", "postgres"),
            "port": os.environ.get("POSTGRES_PORT_PROD", 5433),
            "dbname": os.environ.get("POSTGRES_DB_PROD", "mydatabase"),
            "user": os.environ.get("POSTGRES_USER_PROD", "postgres"),
            "password": os.environ.get("POSTGRES_PASSWORD_PROD", "mysecretpassword"),
        }
        try:
            return psycopg2.connect(**prod_credentials)
        except Exception as e:
            print(prod_credentials)
            print("Broken? What's dfferent?")
    elif env_profile == "DEV":
        return psycopg2.connect(
            host=os.environ.get("POSTGRES_HOST", "postgres"),
            port=os.environ.get("POSTGRES_PORT", 5433),
            dbname=os.environ.get("POSTGRES_DB", "mydatabase"),
            user=os.environ.get("POSTGRES_USER", "postgres"),
            password=os.environ.get("POSTGRES_PASSWORD", "mysecretpassword"),
        )
    else:
        raise NotImplementedError(
            "You need to specify an env_profile in config.py: PROD or DEV"
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


def print_tables_in_schema(connection, schema=BASE_SCHEMA):
    print("Printing tables in schema:")
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s
        """,
            (schema,),
        )

        tables = cursor.fetchall()
        for (table,) in tables:
            print(table)
    print()


def truncate_tables(connection):
    with connection.cursor() as cursor:
        for table_name in tables:
            cursor.execute(
                "DROP TABLE IF EXISTS {}.{} CASCADE;".format(BASE_SCHEMA, table_name)
            )


def vacuum(conn, table_name):
    old_isolation_level = conn.isolation_level
    conn.set_isolation_level(0)  # Set autocommit mode
    cursor = conn.cursor()
    cursor.execute(f"VACUUM (VERBOSE, ANALYZE) {table_name};")
    cursor.close()
    conn.set_isolation_level(old_isolation_level)  # Reset the isolation level


# Usage


def set_up_schemas(connection):
    with connection.cursor() as cursor:
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {BASE_SCHEMA};")
        cursor.execute("CREATE SCHEMA IF NOT EXISTS dev;")


def assert_tables(connection, table_classes):
    with connection.cursor() as cursor:
        for tc in table_classes:
            # Split schema and table name if it's provided in the format "schema.table"
            schema, table_name = (
                tc.TABLE_NAME.split(".")
                if "." in tc.TABLE_NAME
                else (None, tc.TABLE_NAME)
            )

            # Query to check the existence of a table (and schema if provided)
            if schema:
                cursor.execute(
                    "SELECT to_regclass(%s) IS NOT NULL", (f"{schema}.{table_name}",)
                )
            else:
                cursor.execute("SELECT to_regclass(%s) IS NOT NULL", (table_name,))

            # Fetch the result
            table_exists = cursor.fetchone()[0]
            if not table_exists:
                raise ValueError(f"Table {tc.TABLE_NAME} does not exist.")
