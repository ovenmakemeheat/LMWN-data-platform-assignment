up:
	docker compose up -d --build

down:
	docker compose down -v

etl:
	docker exec -it spark spark-submit /etl/etl_iceberg.py

trino:
	docker exec -it trino trino
