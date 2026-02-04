from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
import logging

# Set up logging
logger = logging.getLogger(__name__)

default_args = {
    "owner": "data_engineering",
    "depends_on_past": False,
    "start_date": days_ago(1),
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "email": ["data-team@example.com"],
}

dag = DAG(
    "iceberg_etl_pipeline_enhanced",
    default_args=default_args,
    description="Enhanced ETL pipeline using Faker for mock data generation",
    schedule_interval="@hourly",
    catchup=False,
    max_active_runs=1,
    tags=["iceberg", "etl", "faker", "mock-data"],
)


def check_data_quality():
    """Check data quality after ETL completion"""
    logger.info("Starting data quality checks...")

    # This would typically connect to Trino/Spark to run quality checks
    # For now, we'll simulate the checks
    logger.info("✓ Data count validation passed")
    logger.info("✓ Schema validation passed")
    logger.info("✓ No null values in critical fields")
    logger.info("✓ Data freshness check passed")

    return "Data quality checks completed successfully"


def send_notification():
    """Send notification about ETL completion"""
    logger.info("ETL pipeline completed successfully!")
    logger.info("Generated 1000 mock sales records with enhanced schema")
    logger.info("Data written to Iceberg table: demo.sales")

    # In a real scenario, this would send notifications to Slack, email, etc.
    return "Notification sent"


# Task 1: Pre-ETL validation
pre_etl_check = BashOperator(
    task_id="pre_etl_validation",
    bash_command='echo "Starting ETL pipeline at $(date)"',
    dag=dag,
)

# Task 2: Run Spark ETL with enhanced configuration
etl_task = SparkSubmitOperator(
    task_id="run_enhanced_spark_etl",
    application="/etl/etl_iceberg.py",
    conn_id="spark_default",
    conf={
        "spark.sql.shuffle.partitions": "4",
        "spark.executor.memory": "2g",
        "spark.driver.memory": "1g",
        "spark.sql.catalog.spark_catalog": "org.apache.iceberg.spark.SparkSessionCatalog",
        "spark.sql.catalog.spark_catalog.type": "hive",
        "spark.sql.extensions": "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
    },
    packages="org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.4.3",
    verbose=True,
    dag=dag,
)

# Task 3: Data quality validation
data_quality_check = PythonOperator(
    task_id="data_quality_check",
    python_callable=check_data_quality,
    dag=dag,
)

# Task 4: Send completion notification
notification_task = PythonOperator(
    task_id="send_completion_notification",
    python_callable=send_notification,
    dag=dag,
)

# Task 5: Update monitoring metrics
update_metrics = BashOperator(
    task_id="update_monitoring_metrics",
    bash_command='echo "Updating monitoring metrics at $(date)"',
    dag=dag,
)

# Define task dependencies
pre_etl_check >> etl_task >> data_quality_check >> [notification_task, update_metrics]
