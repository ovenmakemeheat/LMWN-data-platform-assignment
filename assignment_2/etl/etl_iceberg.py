from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType,
    StructField,
    IntegerType,
    StringType,
    DoubleType,
    TimestampType,
)
from faker import Faker
import random
from datetime import datetime, timedelta


def generate_mock_sales_data(num_records=1000):
    """Generate realistic mock sales data using Faker"""
    fake = Faker()
    fake.seed_instance(42)  # For reproducible data

    data = []
    start_date = datetime(2025, 1, 1)

    for i in range(1, num_records + 1):
        # Generate realistic customer data
        customer_name = fake.name()
        customer_email = fake.email()
        customer_city = fake.city()
        customer_country = fake.country()

        # Generate product data
        product_categories = ["Electronics", "Clothing", "Books", "Home", "Sports"]
        product_category = random.choice(product_categories)
        product_name = fake.catch_phrase()

        # Generate order data with realistic amounts
        if product_category == "Electronics":
            amount = round(random.uniform(50, 2000), 2)
        elif product_category == "Clothing":
            amount = round(random.uniform(20, 200), 2)
        elif product_category == "Books":
            amount = round(random.uniform(10, 50), 2)
        elif product_category == "Home":
            amount = round(random.uniform(30, 500), 2)
        else:  # Sports
            amount = round(random.uniform(15, 300), 2)

        # Generate order date with some time distribution
        days_ago = random.randint(0, 365)
        order_date = start_date + timedelta(days=days_ago)

        # Generate order status
        order_status = random.choice(["pending", "completed", "cancelled", "refunded"])

        data.append(
            (
                i,
                customer_name,
                customer_email,
                customer_city,
                customer_country,
                product_name,
                product_category,
                amount,
                order_date,
                order_status,
            )
        )

    return data


def main():
    # Initialize Spark session with Iceberg configuration
    spark = (
        SparkSession.builder.appName("Iceberg ETL with Faker")
        .config(
            "spark.sql.extensions",
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
        )
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.iceberg.spark.SparkSessionCatalog",
        )
        .config("spark.sql.catalog.spark_catalog.type", "hive")
        .config("spark.sql.catalog.local", "org.apache.iceberg.spark.SparkCatalog")
        .config("spark.sql.catalog.local.type", "hadoop")
        .config("spark.sql.catalog.local.warehouse", "s3a://warehouse/")
        .getOrCreate()
    )

    # Define schema for the sales data
    schema = StructType(
        [
            StructField("order_id", IntegerType(), False),
            StructField("customer_name", StringType(), False),
            StructField("customer_email", StringType(), False),
            StructField("customer_city", StringType(), False),
            StructField("customer_country", StringType(), False),
            StructField("product_name", StringType(), False),
            StructField("product_category", StringType(), False),
            StructField("amount", DoubleType(), False),
            StructField("order_date", TimestampType(), False),
            StructField("order_status", StringType(), False),
        ]
    )

    print("Generating mock sales data...")
    mock_data = generate_mock_sales_data(1000)

    print(f"Generated {len(mock_data)} records")

    # Create DataFrame with mock data
    df = spark.createDataFrame(mock_data, schema)

    # Show sample data
    print("Sample data:")
    df.show(5, truncate=False)
    df.printSchema()

    # Create database if it doesn't exist
    spark.sql("CREATE DATABASE IF NOT EXISTS demo")

    # Write data to Iceberg table
    print("Writing data to Iceberg table...")
    df.writeTo("demo.sales").createOrReplace()

    # Verify the table was created
    print("Table created successfully!")
    spark.sql("SELECT COUNT(*) as total_records FROM demo.sales").show()

    # Show table properties
    spark.sql("DESCRIBE EXTENDED demo.sales").show(truncate=False)

    spark.stop()


if __name__ == "__main__":
    main()
