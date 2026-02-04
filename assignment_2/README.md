# Assignment 2 — Data Platform Architecture & Guidelines

## 1. System Architecture Diagram

```mermaid
flowchart TB
  subgraph Sources
    A[Relational DBs / OLTP]
    B[Event Stream (Kafka)]
    C[3rd-party APIs / Files]
  end

  subgraph Ingest
    I1[Airflow Orchestrator]
    I2[Ingestion Workers (Spark / Python)]
    I3[Kafka Connect / Debezium]
  end

  subgraph Storage
    S1[Object Store (MinIO / S3)]
    S2[Iceberg Tables (on S3/MinIO)]
    S3[Hive Metastore / Catalog]
  end

  subgraph Compute
    K8S[Kubernetes]
    Spark[Spark (batch/ETL)]
    Trino[Trino (ad-hoc SQL)]
    HS[Hive / Metastore]
  end

  subgraph Observability
    P[Prometheus]
    G[Grafana]
    L[Centralized Logs]
    Alert[Alerting (PagerDuty/Email)]
  end

  A -->|CDC / Export| I3
  B -->|Stream| I1
  C -->|API / Files| I1
  I1 -->|trigger jobs| I2
  I2 -->|write parquet/iceberg| S1
  S1 --> S2
  S2 --> HS
  HS -->|metadata| S3
  Spark -->|processing| S2
  Trino -->|query| S2
  K8S --> Spark
  K8S --> Trino
  K8S --> I1
  K8S --> HS
  P -->|metrics| G
  L -->|logs| G
  I1 -->|metrics| P
  Spark -->|metrics| P
  Trino -->|metrics| P
  P --> Alert
```

Rationale:
- Object-store backed Iceberg provides cheap scalable storage with ACID and schema evolution.
- Decoupling orchestration (Airflow), compute (Spark/Trino), and storage (MinIO/S3) enables independent scaling and fault isolation.
- Kubernetes runs compute & services for elasticity; use managed k8s in cloud for operational overhead reduction.
- Catalog (Hive Metastore) centralizes metadata for query engines and guarantees consistency.

Cost-awareness:
- Use object storage (MinIO/S3) for low-cost, long-term storage; keep frequently queried data hot, archive old partitions to cheaper tiers.
- Right-size compute and use autoscaling + preemptible/spot instances for non-critical batch jobs.
- Partitioning and compaction reduce I/O and query costs; columnar formats (Parquet/ORC) reduce storage and read costs.
- Share compute clusters (multi-tenant) and schedule heavy workloads during off-peak for cost savings.
- Monitor usage and enable lifecycle rules to delete/compact/transfer cold data.

---

## 2. Setup and Deployment Guidelines

Prerequisites:
- Docker & docker-compose (dev)
- Kubernetes cluster (kind / minikube for local, managed k8s for staging/prod)
- kubectl, helm, make, python 3.8+
- Credentials for object storage and registry

Quick start (development - docker-compose):
1. Copy env: cp assignment_2/.env.example assignment_2/.env (or edit assignment_2/.env).
2. Start services: docker-compose -f assignment_2/docker-compose.yml up --build -d
   - This brings up Airflow, MinIO, Hive Metastore, Trino, Spark (as configured).
3. Load sample data and run DAGs via Airflow UI (default ports in docker-compose).

Staging / Production (k8s):
1. Ensure cluster and ingress ready; create namespace (e.g., data-platform).
2. Use Helm charts or provided manifests under assignment_2/k8s:
   - kubectl apply -f assignment_2/k8s/hive-metastore.yaml
   - kubectl apply -f assignment_2/k8s/minio.yaml
   - kubectl apply -f assignment_2/k8s/spark.yaml
   - kubectl apply -f assignment_2/k8s/trino.yaml
   - kubectl apply -f assignment_2/k8s/airflow.yaml
   - kubectl apply -f assignment_2/k8s/prometheus-pod.yaml
   - kubectl apply -f assignment_2/k8s/grafana.yaml
3. Configure secrets via Kubernetes Secret (do not commit secrets to repo).
4. Configure storage classes (S3 compatible) and PV/PVC as needed.
5. Configure Ingress and TLS (cert-manager) for secure endpoints.

Automation & IaC:
- Use Terraform for cloud infra (VPC, managed k8s, object storage).
- Use Helm charts for application deployment; store values files per-environment.
- CI/CD: push to main triggers tests, image build, and Helm release to staging; approvals for prod.
- Use Makefile (project includes one) for common tasks.

Monitoring during deployment:
- Deploy Prometheus & Grafana; include service monitors for Airflow, Spark, Trino.
- Enable alerting rules (CPU, memory, job failures, ETL DAG failures).
- Centralized logging (Fluentd/Promtail -> Loki / ELK) for log retention and search.

Environment recommendations:
- Development: docker-compose or local k8s, single-node, minimal resources.
- Staging: scaled down k8s cluster, mirrored config of prod, test quota/limits.
- Production: multi-zone k8s, autoscaling, HA replicas for critical services (Airflow Scheduler/Workers, Trino coordinator HA), backups and disaster recovery.

---

## 3. ETL Guidelines

Architecture:
- Orchestration: Airflow DAGs (assignment_2/airflow/dags/iceberg_etl_dag.py) schedules/executions.
- Processing: Spark jobs (assignment_2/spark/* and assignment_2/etl/etl_iceberg.py) perform transformations and write Iceberg tables to object store.
- Catalog: Hive metastore for table metadata (assignment_2/metastore/hive-site.xml).

ETL best practices:
- Idempotency: design tasks/jobs to be idempotent (use staging tables / write-then-rename).
- Atomic writes: use Iceberg transactional writes to avoid partial data visibility.
- Data validation: implement schema checks, row-level validation, and constraints; fail-fast on critical errors.
- Error handling & retries: exponential backoff and bounded retries; capture failed rows to poison queue (S3 prefix) for later reprocessing.
- Logging: structured logs (JSON) with correlation IDs; emit metrics for job duration, rows processed, errors.
- Scheduling: Airflow for dependencies; backfill carefully with date partition boundaries.

Incremental loads:
- Use watermark columns (updated_at) or CDC (Debezium -> Kafka Connect) for incremental ingestion.
- Prefer MERGE INTO Iceberg or UPSERT semantics to apply changes.
- Keep checkpoints stored in durable storage (e.g., S3 or metastore).

Schema changes:
- Use Iceberg schema evolution (add, rename, drop) with compatibility checks.
- Maintain a schema registry or metadata store to track historical schemas.
- Run compatibility tests in staging: apply migration to copy small sample and validate queries before full rollout.

Performance optimization:
- Partitioning strategy (by date, logical keys) to prune scans.
- Compaction and optimization jobs (small-file consolidation).
- Use vectorized reads, predicate pushdown, and column pruning.
- Cache frequently queried datasets (Presto/Trino caching, materialized views).
- Resource configs: tune spark.executor.memory and cores; use dynamic allocation.

---

## 4. Security and Governance

Authentication & Authorization:
- Airflow: enable RBAC, integrate with LDAP/OAuth/SAML for SSO.
- MinIO/S3: use per-service credentials and short-lived tokens where possible.
- Trino/Hive: enable authentication and role-based access control; map warehouse roles to data roles.
- Kubernetes: use RBAC, network policies, and pod security policies (or OPA/Gatekeeper).

Encryption & Data Protection:
- In transit: TLS for all HTTP/gRPC endpoints, secure inter-service mTLS in k8s (e.g., Istio).
- At rest: server-side encryption for object store, and enable KMS-managed keys. For sensitive fields, use field-level encryption.
- Key management: use cloud KMS or Vault; rotate keys periodically.

Secrets & Credentials:
- Store secrets in Kubernetes Secrets or external secret manager (HashiCorp Vault, cloud provider secret manager). Do not store creds in repo.
- Use IAM roles or service accounts for least-privilege access.

Governance & Data Lineage:
- Data ownership: assign owners per dataset and enforce SLAs.
- Metadata: maintain table metadata in the metastore; track dataset descriptions, owners, and tags.
- Lineage: instrument Airflow tasks and use OpenLineage / Marquez to record upstream/downstream relationships.
- Auditing: capture access logs for object store, query engines, and metastore; forward to centralized logging and retention policy.

Compliance:
- Implement data retention and deletion policies.
- PII detection and masking for regulated datasets.
- Periodic audits, policy-as-code checks (e.g., TerraScan, OPA).

Access Monitoring:
- Monitor queries and abnormal access patterns; set alerts for high-volume exports.
- Use IAM policies and query limits to prevent exfiltration.

---

## 5. Further Improvements and Enhancements (Must-Have)

Short-term:
- Add CI to validate Airflow DAGs and Spark jobs automatically (unit + integration).
- Implement automated cost reports (Prometheus exporters + cost tooling) and query-level cost attribution.
- Introduce centralized secret manager (Vault) and remove all plain-text secrets.

Medium-term:
- Autoscaling for Spark via Kubernetes operator (Spark-on-K8s) and Trino autoscaling.
- Implement CDC-based ingestion for low-latency updates (Debezium -> Kafka -> Spark Streaming).
- Add data quality framework (Great Expectations) integrated into DAGs with quality gates.

Long-term / Advanced:
- Move to cloud-managed object storage and k8s for operational savings and native integrations (e.g., S3, EKS/GKE/AKS).
- Introduce workload-aware autoscaling and cost-optimized spot instance pools for batch workloads.
- Add query caching layer and materialized views for interactive analytics.
- Adopt a data mesh model: publish/subscribe datasets with enforced contracts, enabling domain ownership.

Operational & Maintainability:
- Implement automated backups of metastore and periodic snapshot testing for disaster recovery.
- Implement blue/green or canary deploys for schema changes and query engine updates.
- Centralize observability dashboards and pre-built runbooks for common incidents.

---

## References & Useful Files
- Airflow DAGs: assignment_2/airflow/dags/iceberg_etl_dag.py
- ETL implementation: assignment_2/etl/etl_iceberg.py
- Spark config & Dockerfile: assignment_2/spark/
- K8s manifests: assignment_2/k8s/
- Local compose: assignment_2/docker-compose.yml
- Metastore config: assignment_2/metastore/hive-site.xml