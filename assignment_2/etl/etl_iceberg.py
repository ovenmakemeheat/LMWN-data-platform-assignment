from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("Iceberg ETL") \
    .getOrCreate()

data = [
    (1, "Alice", 100.0, "2025-01-01"),
    (2, "Bob", 200.0, "2025-01-02")
]

df = spark.createDataFrame(
    data, ["order_id", "customer", "amount", "order_date"]
)

spark.sql("CREATE DATABASE IF NOT EXISTS demo")

df.writeTo("demo.sales").createOrReplace()

spark.stop()
