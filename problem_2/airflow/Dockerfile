ARG AIRFLOW_VERSION=2.8.0
FROM apache/airflow:${AIRFLOW_VERSION}

USER airflow
RUN pip install --no-cache-dir \
    "apache-airflow-providers-apache-spark" \
    "apache-airflow-providers-postgres" \
    "boto3" \
    "faker"

COPY --chown=airflow:airflow airflow.cfg /opt/airflow/airflow.cfg

ENV AIRFLOW__CORE__LOAD_EXAMPLES=False