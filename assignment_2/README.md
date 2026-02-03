# Data Platform Engineer – Problem 2

## Apache Iceberg Lakehouse Data Platform

---

## 1. Overview

This project demonstrates the design and implementation of a **scalable, cost-efficient data platform** using a modern **lakehouse architecture**.
The platform is built to support **terabyte-scale data**, **concurrent analytical queries**, and **different query frequencies** (hourly monitoring and daily reporting).

The solution uses **Apache Iceberg** as the core table format, **Apache Spark** for ETL, **Trino** as the query engine, **Airflow** for orcฟhestration, and **Prometheus + Grafana** for monitoring.
All components are **containerized** and can also be deployed on **Kubernetes**.

---

## 2. Architecture Summary

### High-Level Architecture

External Data
→ Spark ETL
→ Apache Iceberg Tables (Object Storage)
→ Trino Query Engine
→ BI Tools / SQL Clients

### Key Design Principles

* Separation of **storage** and **compute**
* Horizontal scalability
* Cost-efficient object storage
* Open table format (Iceberg)
* Cloud-native and containerized

---

## 3. Technology Stack

| Layer                 | Technology                           |
| --------------------- | ------------------------------------ |
| Storage               | MinIO (S3-compatible Object Storage) |
| Table Format          | Apache Iceberg                       |
| Metadata Catalog      | Hive Metastore                       |
| ETL Processing        | Apache Spark                         |
| Orchestration         | Apache Airflow                       |
| Query Engine          | Trino                                |
| Monitoring            | Prometheus + Grafana                 |
| Containerization      | Docker & Docker Compose              |
| Orchestration (Bonus) | Kubernetes                           |

---

## 4. Why Apache Iceberg?

Apache Iceberg is chosen as the main table format because it provides:

* ACID transactions on data lakes
* Schema evolution
* Time travel and snapshot isolation
* Efficient metadata pruning
* Compatibility with Spark and Trino

This makes Iceberg suitable for large-scale analytical workloads while keeping storage costs low.

---

## 5. Setup & Deployment (Docker Compose)

### 5.1 Prerequisites

* Docker & Docker Compose
* Make (optional but recommended)

---

### 5.2 Start the Platform

```bash
make up
```

This command starts:

* MinIO (object storage)
* Hive Metastore
* Spark
* Trino
* Airflow
* Prometheus
* Grafana

---

### 5.3 Access Services

| Service       | URL                                            |
| ------------- | ---------------------------------------------- |
| MinIO Console | [http://localhost:9001](http://localhost:9001) |
| Trino UI      | [http://localhost:8080](http://localhost:8080) |
| Airflow UI    | [http://localhost:8081](http://localhost:8081) |
| Prometheus    | [http://localhost:9090](http://localhost:9090) |
| Grafana       | [http://localhost:3000](http://localhost:3000) |

---

## 6. ETL Pipeline

### 6.1 ETL Process

1. External data is loaded into Spark
2. Data is transformed and cleaned
3. Data is written as an **Iceberg table**
4. Metadata is registered in Hive Metastore

---

### 6.2 Run ETL Manually

```bash
make etl
```

---

### 6.3 Airflow-Orchestrated ETL

* ETL pipeline is scheduled **hourly**
* Automatic retries on failure
* Centralized monitoring via Airflow UI

DAG Name:

```
iceberg_etl_pipeline
```

---

## 7. Querying the Data Platform

### 7.1 Connect to Trino

```bash
make trino
```

---

### 7.2 Example Queries

```sql
SELECT * FROM iceberg.demo.sales;

SELECT order_date, SUM(amount)
FROM iceberg.demo.sales
GROUP BY order_date;
```

---

## 8. Supporting Different Query Patterns

### Daily Reports (Team A)

* Scheduled queries
* Optional materialized views
* Optimized for read performance

### Hourly Monitoring (Team B)

* Frequent queries on recent partitions
* Iceberg metadata filtering reduces scan cost

---

## 9. Monitoring & Observability

### Tools Used

* **Prometheus**: Collects metrics
* **Grafana**: Visualizes performance

### Metrics Monitored

* Trino query latency
* Spark job execution time
* CPU and memory usage
* System health

Monitoring helps detect performance bottlenecks and control compute costs.

---

## 10. Security & Governance

### Security

* Object storage access control
* Trino role-based access control
* Network isolation via containers

### Governance

* Schema enforcement using Iceberg
* Centralized metadata catalog
* Query auditability via Trino logs

---

## 11. Kubernetes Deployment (Bonus)

All platform components can be deployed on Kubernetes using the manifests in the `k8s/` directory.

### Benefits of Kubernetes

* Horizontal scalability
* Fault tolerance
* Resource isolation
* Cloud-native deployment
* Cost-efficient autoscaling

Deploy with:

```bash
kubectl apply -f k8s/
```

---

## 12. Cost Awareness

This platform is designed to be cost-efficient by:

* Using object storage instead of data warehouses
* Separating storage and compute
* Scaling query engines only when needed
* Avoiding data duplication
* Leveraging Iceberg metadata pruning

---

## 13. Conclusion

This project demonstrates a **production-style data platform** that:

* Scales to terabyte-level data
* Supports multiple query patterns
* Uses open-source technologies
* Is cloud-native and containerized
* Balances performance and cost

The architecture is flexible and can be extended with additional governance, security, and optimization features as data usage grows.

---

If you want, I can also:

* Shorten this to a **2-page version**
* Align wording exactly to **LMWN evaluation style**
* Add a **system architecture diagram explanation**
* Prepare **interview talking points** based on this README
