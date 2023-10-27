CREATE VIEW daysheet_credits_matched AS
SELECT
    ...
FROM 
    parquet_scan('s3://my-bucket/first-table.parquet') AS t1
JOIN
    parquet_scan('s3://my-bucket/second-table.parquet') AS t2 ON t1.id = t2.id
WHERE
    ...;

-- Writing the view to a new Parquet file
COPY (SELECT * FROM daysheet_credits_matched) TO 's3://my-bucket/daysheet_credits_matched.parquet' (FORMAT 'parquet');
