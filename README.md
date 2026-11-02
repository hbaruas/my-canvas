import base64
import datetime
import logging
import os
import re

# ==============================================================================
# 1. DISABLE CONSOLE TEXT TRUNCATION (Applies to CML/CDSW Output Logs)
# ==============================================================================
os.environ["MAX_TEXT_LENGTH"] = "10000000"

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pyspark.sql.functions as F
from pyspark.sql import SparkSession
from pyspark.sql.types import *
import spacy
from tqdm import tqdm
from wordcloud import WordCloud

# Adjust project root
os.chdir("/home/cdsw/online_job_ads/OECD_ROBERT_DUNN/OECD_PIPELINE")

# Import unified configuration
import config

print(config.GOLD_STANDARD)

# ==============================================================================
# SETUP LOGGING & DIRECTORIES
# ==============================================================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

os.makedirs(config.EXPORT_DIR, exist_ok=True)
os.makedirs(config.REPORTS_DIR, exist_ok=True)

# ==============================================================================
# SPARK CLUSTER INITIALIZATION (High Capacity: 70 Executors x 50GB)
# ==============================================================================
print("\n" + "=" * 58)
print("STARTING DYNAMIC OECD MACROECONOMIC PIPELINE (HIGH SCALE)")
print("=" * 58 + "\n")

print("Initializing Large Spark Cluster (50GB per Executor, 70 Instances)...")
spark = (
    SparkSession.builder.appName("OECD_Pipeline_HighScale")
    # --- Executor & Driver Sizing (Matches 50g / 5 cores / 70 executors) ---
    .config("spark.executor.memory", "50g")
    .config("spark.executor.cores", "5")
    .config("spark.dynamicAllocation.enabled", "true")
    .config("spark.dynamicAllocation.maxExecutors", "70")
    .config("spark.dynamicAllocation.minExecutors", "10")
    .config("spark.driver.memory", "16g")
    .config("spark.driver.maxResultSize", "8g")
    # --- Container Overhead Memory (Critical for YARN container stability) ---
    .config("spark.yarn.executor.memoryOverhead", "6g")
    .config("spark.yarn.driver.memoryOverhead", "2g")
    # --- Network, Heartbeats & Retries (Prevents MetadataFetchFailed drops) ---
    .config("spark.network.timeout", "800s")
    .config("spark.executor.heartbeatInterval", "60s")
    .config("spark.shuffle.io.maxRetries", "10")
    .config("spark.shuffle.io.retryWait", "30s")
    # --- Shuffle Partitions & Adaptive Query Execution ---
    .config("spark.sql.shuffle.partitions", "2000")
    .config("spark.sql.adaptive.enabled", "true")
    .config("spark.sql.adaptive.skewJoin.enabled", "true")
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
    # --- PyArrow Optimization ---
    .config("spark.sql.execution.arrow.pyspark.enabled", "true")
    .config("spark.sql.execution.arrow.maxRecordsPerBatch", "5000")
    .getOrCreate()
)

# Suppress driver verbosity while retaining critical execution failures
spark.sparkContext.setLogLevel("ERROR")
