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
    .select(F.trim(F.col("doc_JobID")).cast("string").alias("doc_JobID"))
    .distinct()
)
id_count = id_df.count()
print(f"Job IDs loaded: {id_count:,}")
print("Sample IDs from CSV:")
id_df.show(5, truncate=False)

source_df = spark.read.parquet(S3_SOURCE)

# Show a few raw job_id values from the parquet so we can compare formats
print("Sample job_id values from parquet:")
source_df.select(F.col("job_id")).show(5, truncate=False)
print(f"Parquet job_id column type: {dict(source_df.dtypes)['job_id']}")

result_df = (
    source_df
    .select(
        F.trim(F.col("job_id").cast("string")).alias("doc_JobID"),
        F.col("full_text").cast("string").alias("full_text"),
        F.col("soc2020").cast("string").alias("soc2020"),
        F.col("date").cast("string").alias("date"),
    )
    .join(F.broadcast(id_df), on="doc_JobID", how="inner")
)

matched = result_df.count()
print(f"Matched: {matched:,} of {id_count:,}")

result_df.toPandas().to_csv(OUTPUT_CSV, index=False)
print(f"Written to: {OUTPUT_CSV}")

spark.stop()
