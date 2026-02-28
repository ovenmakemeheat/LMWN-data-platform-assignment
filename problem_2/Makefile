.PHONY: up down etl trino spark-sql spark-shell pyspark

up:
	docker compose up -d --build

down:
	docker compose down -v

etl:
	docker exec -it spark-iceberg spark-submit /etl/etl_iceberg.py

trino:
	docker exec -it trino trino

spark-sql:
	docker exec -it spark-iceberg spark-sql

spark-shell:
	docker exec -it spark-iceberg spark-shell

pyspark:
	docker exec -it spark-iceberg pyspark
