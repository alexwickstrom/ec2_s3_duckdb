import duckdb
import polars as pl
from replicate_to_s3 import get_s3_client


def download_parquet_from_s3(client, table_name, base_path="/tmp"):
    bucket = "my-bucket"
    key = f"{table_name}/{table_name}.parquet"
    download_path = f"{base_path}/{table_name}.parquet"
    client.download_file(bucket, key, download_path)
    return download_path


def create_duckdb_table(con, table_name, parquet_path):
    create_table_query = (
        f"CREATE TABLE {table_name} AS SELECT * FROM parquet_scan('{parquet_path}')"
    )
    con.execute(create_table_query)


if __name__ == "__main__":
    # Initialize S3 client
    s3 = get_s3_client()

    # Initialize DuckDB connection
    con = duckdb.connect(database=":memory:", read_only=False)

    # List of table names to download and create in DuckDB
    table_names = ["Doctor", "Patient", "Appointment"]

    for table_name in table_names:
        # Download the Parquet file from S3
        parquet_path = download_parquet_from_s3(s3, table_name)

        # Create a DuckDB table from the Parquet file
        create_duckdb_table(con, table_name.lower(), parquet_path)

    # Now you can query the tables as you would with any other SQL tables
    result = con.execute("SELECT * FROM Doctor").fetchall()
    print(result)
