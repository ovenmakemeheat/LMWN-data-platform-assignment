# LMWN Data Platform Assignment

Complete solution for the LMWN Data Platform Engineer take-home assignment.

## Problem Summaries

**Problem 1**: PySpark DataFrame transformation - implements recursive flattening of nested structures while preserving arrays, and converts all column names to snake_case format.

**Problem 2**: Modern data platform using Apache Iceberg - containerized architecture with Spark, Trino, MinIO, and monitoring via Prometheus/Grafana.

## Development Environment Setup

### Prerequisites

- Python 3.10+ (specified in `.python-version`)
- uv (Python dependency manager)
- Docker & Docker Compose
- Make

### Python Environment (uv)

**Option 1: Manual Setup**

```bash
# Initialize project
uv init

# Add dependencies manually
uv add apache-airflow==2.8.0 apache-airflow-providers-apache-spark>=4.11.3 faker>=40.1.2 pyspark>=4.1.1

# Run scripts directly
uv run python problem_1/item1.py
uv run python problem_2/etl/etl_iceberg.py
```

**Option 2: Sync from pyproject.toml**

```bash
# Sync dependencies from pyproject.toml
uv sync

# Run scripts directly
uv run python problem_1/item1.py
uv run python problem_2/etl/etl_iceberg.py
```

### Problem 1 Quick Start

```bash
cd problem_1
uv run python item1.py
```

### Problem 2 Quick Start

```bash
cd problem_2
make up      # Start platform
make etl     # Run ETL
make trino   # Query data
make down    # Stop platform
```

## Project Structure

```
├── problem_1/     # PySpark data transformation
├── problem_2/     # Data platform (Docker, Spark, Trino)
├── pyproject.toml # Dependencies
└── .python-version # Python version
```

For detailed instructions, see individual README files in each problem directory.
