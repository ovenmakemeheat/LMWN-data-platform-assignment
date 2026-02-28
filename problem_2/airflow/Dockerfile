ARG AIRFLOW_VERSION=2.8.0
FROM apache/airflow:${AIRFLOW_VERSION}

USER airflow
RUN pip install --no-cache-dir \
    "apache-airflow-providers-apache-spark" \
    "apache-airflow-providers-postgres" \
    "boto3" \
    "faker" \
    "connexion[swagger-ui]"

RUN airflow db migrate

RUN airflow users create --username admin --password admin --firstname admin --lastname admin --role Admin --email admin@example.com

COPY --chown=airflow:airflow airflow.cfg /opt/airflow/airflow.cfg

ENV AIRFLOW__CORE__LOAD_EXAMPLES=False