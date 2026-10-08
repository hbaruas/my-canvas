import pandas as pd
from pyspark.sql import SparkSession
import pyspark.sql.functions as F

BASE_DIR = "/home/cdsw/online_job_ads/OECD/OECD_PIPELINE"

INPUT_CSV  = BASE_DIR + "/Data_to_be_labeled.csv"
OUTPUT_CSV = BASE_DIR + "/labeled_full_texts.csv"
S3_SOURCE = "s3a://onscdp-prd-data01-d4946922/dapsen/workspace_zone/online_job_ads/OECD_DATA/microdata_29_September_2026_0859.parquet"

spark = (
    SparkSession.builder
    .appName("OECD_extract_job_texts")
    .config("spark.executor.memory", "20g")
    .config("spark.yarn.executor.memoryOverhead", "2g")
    .config("spark.executor.cores", 5)
    .config("spark.dynamicAllocation.maxExecutors", 12)
    .config("spark.sql.shuffle.partitions", 240)
    .getOrCreate()
)
spark.sparkContext.setLogLevel("ERROR")

id_df = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "false")
    .csv(INPUT_CSV)
    .select(F.col("doc_JobID").cast("string").alias("doc_JobID"))
    .distinct()
)
print(f"Job IDs loaded: {id_df.count():,}")

source_df = spark.read.parquet(S3_SOURCE)

result_df = (
    source_df
    .select(
        F.col("job_id").cast("string").alias("doc_JobID"),
        F.col("full_text").cast("string").alias("full_text"),
    )
    .join(F.broadcast(id_df), on="doc_JobID", how="inner")
)

matched = result_df.count()
print(f"Matched: {matched:,}")

result_df.toPandas().to_csv(OUTPUT_CSV, index=False)
print(f"Written to: {OUTPUT_CSV}")

spark.stop()
