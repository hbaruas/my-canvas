"""
extract_job_texts.py
--------------------
One-off script: given a CSV of job IDs, pull the matching full_text
values from the production parquet store on S3 and write them out as a
CSV with two columns: job_id, full_text.

Usage
-----
    python extract_job_texts.py \
        --ids     /path/to/input_job_ids.csv \
        --output  /path/to/output_full_texts.csv

The input CSV must have at least one column named  job_id.
The output CSV will have exactly two columns:       job_id, full_text.
"""

import argparse
import sys
import os

# ── Configuration ─────────────────────────────────────────────────────────────

S3_PARQUET_PATH = (
    "s3a://onscdp-prd-data01-d4946922/dapsen/workspace_zone/"
    "online_job_ads/OECD_DATA/microdata_29_September_2026_0859.parquet"
)

# Spark tuning — increase driver memory if the output CSV is very large
DRIVER_MEMORY   = "8g"
EXECUTOR_MEMORY = "4g"

# ── Argument parsing ──────────────────────────────────────────────────────────

parser = argparse.ArgumentParser(
    description="Extract full_text for a list of job IDs from the S3 parquet store."
)
parser.add_argument(
    "--ids",
    required=True,
    metavar="PATH",
    help="CSV file containing a column called job_id.",
)
parser.add_argument(
    "--output",
    required=True,
    metavar="PATH",
    help="Where to write the output CSV (job_id, full_text).",
)
args = parser.parse_args()

if not os.path.exists(args.ids):
    print(f"ERROR: input file not found: {args.ids}")
    sys.exit(1)

# ── Spark session ─────────────────────────────────────────────────────────────

from pyspark.sql import SparkSession
import pyspark.sql.functions as F

print("Initialising Spark ...")
spark = (
    SparkSession.builder
    .appName("OECD_extract_job_texts")
    # ── S3 / Hadoop-AWS ──────────────────────────────────────────────────────
    # On EMR or any IAM-role-attached instance these two lines are sufficient.
    # If running locally with explicit keys, set the environment variables
    # AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY before launching this script,
    # or add .config("spark.hadoop.fs.s3a.access.key", "...") entries here.
    .config("spark.hadoop.fs.s3a.impl",
            "org.apache.hadoop.fs.s3a.S3AFileSystem")
    .config("spark.hadoop.fs.s3a.aws.credentials.provider",
            "com.amazonaws.auth.InstanceProfileCredentialsProvider,"
            "com.amazonaws.auth.EnvironmentVariableCredentialsProvider")
    # ── Memory ───────────────────────────────────────────────────────────────
    .config("spark.driver.memory",   DRIVER_MEMORY)
    .config("spark.executor.memory", EXECUTOR_MEMORY)
    .config("spark.sql.shuffle.partitions", "200")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("ERROR")
print("Spark ready.")

# ── Step 1: load the list of job IDs ─────────────────────────────────────────

print(f"Reading job IDs from: {args.ids}")
id_df = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "false")   # treat everything as string
    .csv(args.ids)
)

if "job_id" not in id_df.columns:
    print(f"ERROR: input CSV has no column called 'job_id'. "
          f"Columns found: {id_df.columns}")
    spark.stop()
    sys.exit(1)

# Deduplicate and cast to string to match the parquet column type
id_df = id_df.select(F.col("job_id").cast("string").alias("job_id")).distinct()
id_count = id_df.count()
print(f"  {id_count:,} unique job IDs loaded.")

# ── Step 2: read the parquet store ───────────────────────────────────────────

print(f"Reading parquet from S3 ...")
print(f"  {S3_PARQUET_PATH}")

source_df = (
    spark.read
    .option("mergeSchema", "false")   # faster — all part files share the same schema
    .parquet(S3_PARQUET_PATH)
)

# Confirm the expected columns exist before doing any heavy work
required_cols = {"job_id", "full_text"}
actual_cols   = set(source_df.columns)
missing       = required_cols - actual_cols

if missing:
    print(f"ERROR: parquet is missing expected columns: {missing}")
    print(f"Columns actually present: {sorted(actual_cols)}")
    spark.stop()
    sys.exit(1)

print(f"  Parquet schema OK. Columns present: {sorted(actual_cols)}")

# ── Step 3: filter to matching job IDs (broadcast join) ──────────────────────
# The ID list is small; broadcast it so Spark avoids a full shuffle of the
# 62M-row parquet.

print("Filtering parquet to matching job IDs (broadcast join) ...")

result_df = (
    source_df
    .select(
        F.col("job_id").cast("string").alias("job_id"),
        F.col("full_text").cast("string").alias("full_text"),
    )
    .join(F.broadcast(id_df), on="job_id", how="inner")
)

# ── Step 4: write output CSV ──────────────────────────────────────────────────

print(f"Writing output to: {args.output}")

# Coalesce to a single file so the output is one plain CSV, not a Spark
# part-file directory.  This is fine because the output is only as large
# as the number of IDs you requested.
(
    result_df
    .coalesce(1)
    .write
    .option("header", "true")
    .option("quote", '"')
    .option("escape", '"')
    .mode("overwrite")
    .csv(args.output + "_tmp_spark")
)

# Spark writes to a directory; find the one real part file and rename it
import glob
import shutil

part_files = glob.glob(os.path.join(args.output + "_tmp_spark", "part-*.csv"))
if not part_files:
    print("ERROR: Spark produced no output part file.")
    spark.stop()
    sys.exit(1)

shutil.move(part_files[0], args.output)
shutil.rmtree(args.output + "_tmp_spark", ignore_errors=True)

# ── Step 5: quick sanity check ────────────────────────────────────────────────

matched = result_df.count()
print()
print("=" * 50)
print("Done.")
print(f"  Job IDs requested : {id_count:,}")
print(f"  Job IDs matched   : {matched:,}")
unmatched = id_count - matched
if unmatched > 0:
    print(f"  WARNING: {unmatched:,} job IDs were not found in the parquet.")
print(f"  Output CSV        : {args.output}")
print("=" * 50)

spark.stop()
