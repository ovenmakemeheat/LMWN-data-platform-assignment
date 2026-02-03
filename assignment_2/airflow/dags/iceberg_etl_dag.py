from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime

with DAG(
    dag_id="iceberg_etl_pipeline",
    start_date=datetime(2025, 1, 1),
    schedule_interval="@hourly",
    catchup=False,
):
    etl = SparkSubmitOperator(
        task_id="run_spark_etl",
        application="/etl/etl_iceberg.py",
        conn_id="spark_default",
    )

    etl
