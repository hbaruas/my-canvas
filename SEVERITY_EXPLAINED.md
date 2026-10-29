from pyspark.sql import SparkSession
import pyspark.sql.functions as F

spark = SparkSession.builder.appName("year_check").getOrCreate()

df = spark.read.parquet(
    "/"
    ""
)

df.withColumn("year", F.year(F.to_date("date"))) \
  .groupBy("year") \
  .count() \
  .orderBy("year") \
  .show()
