"""
extract_job_texts.py
--------------------
Reads Data_to_be_labeled.csv (same folder as this script), looks up the
full_text for each doc_JobID from the production parquet on S3, and writes
the result as labeled_full_texts.csv in the same folder.
"""

import os
import glob
import shutil

from pyspark.sql import SparkSession
import pyspark.sql.functions as F

# ── Paths (all relative to this script's directory) ───────────────────────────

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
INPUT_CSV    = os.path.join(SCRIPT_DIR, "Data_to_be_labeled.csv")
OUTPUT_CSV   = os.path.join(SCRIPT_DIR, "labeled_full_texts.csv")
S3_SOURCE    = (
    "s3a://onscdp-prd-data01-d4946922/dapsen/workspace_zone/"
    "online_job_ads/OECD_DATA/microdata_29_September_2026_0859.parquet"
)

# ── Spark session (production cluster config) ─────────────────────────────────

print("Initializing Spark ...")
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
print("Spark ready.")

# ── Step 1: load the job IDs to look up ───────────────────────────────────────

print(f"Reading job IDs from: {INPUT_CSV}")
id_df = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "false")
    .csv(INPUT_CSV)
    .select(F.col("doc_JobID").cast("string").alias("doc_JobID"))
    .distinct()
)
id_count = id_df.count()
print(f"  {id_count:,} unique job IDs loaded.")

# ── Step 2: read the parquet and join ─────────────────────────────────────────

print(f"Reading parquet from: {S3_SOURCE}")
source_df = spark.read.parquet(S3_SOURCE)

# The raw parquet uses job_id; our lookup CSV uses doc_JobID — they are the
# same value so we align them before joining.
result_df = (
    source_df
    .select(
        F.col("job_id").cast("string").alias("doc_JobID"),
        F.col("full_text").cast("string").alias("full_text"),
    )
    .join(F.broadcast(id_df), on="doc_JobID", how="inner")
)

matched = result_df.count()
print(f"  Matched {matched:,} of {id_count:,} job IDs.")
if matched < id_count:
    print(f"  WARNING: {id_count - matched:,} job IDs were not found in the parquet.")

# ── Step 3: write output as a single CSV file ─────────────────────────────────

TMP_DIR = OUTPUT_CSV + "_tmp"
(
    result_df
    .coalesce(1)
    .write
    .option("header", "true")
    .option("quote", '"')
    .option("escape", '"')
    .mode("overwrite")
    .csv(TMP_DIR)
)

part_files = glob.glob(os.path.join(TMP_DIR, "part-*.csv"))
shutil.move(part_files[0], OUTPUT_CSV)
shutil.rmtree(TMP_DIR, ignore_errors=True)

print(f"\nDone. Output written to: {OUTPUT_CSV}")
spark.stop()
