# E-commerce Warehouse

An end-to-end local data engineering project that generates synthetic e-commerce data, loads it into PostgreSQL, transforms it with dbt, tracks customer history with an SCD2 snapshot, and exposes marts for Metabase.
## Architecture

```text
Python generator -> PostgreSQL raw -> dbt staging -> dbt marts -> Metabase
									  |
									  +-> customer SCD2 snapshot
```
The warehouse uses these grains:

- `raw.raw_customers`, `raw.raw_products`, `raw.raw_orders`, and `raw.raw_order_items` are ingestion tables
- `staging_staging.*` contains cleaned dbt models
- `staging_marts.fct_order_items` is one row per order line
- `staging_marts.fct_daily_sales` is one row per day for paid and shipped orders
- `staging_snapshots.snap_customers` stores customer versions over time
- `staging_marts.dim_customer` presents the SCD2 history

## Stack

- Python 3.11, pandas, SQLAlchemy, psycopg2, and python-dotenv
- PostgreSQL 15 in Docker
- dbt Core 1.8 with the PostgreSQL adapter
- Metabase in Docker
## Quick start

Python 3.11 is required because the pinned database dependencies are tested against it.

```bash
cd ~/Desktop/de-ecommerce-warehouse
docker compose up -d
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
export DBT_PROFILES_DIR="$(pwd)/dbt"
bash run_pipeline.sh
```

The shared database configuration contract is:

```env
DB_HOST=localhost
DB_PORT=5433
DB_NAME=ecom_warehouse
DB_USER=postgres
DB_PASSWORD=postgres
DBT_SCHEMA=staging
```

`DB_PORT` is the host port. Docker maps it to PostgreSQL’s internal port `5432`, so dbt and the Python scripts use `localhost:5433`, while Metabase uses host `postgres` and port `5432` on the Docker network.
The pipeline generates products and customers, mutates a sample of existing customers on later runs, creates 300 orders, runs dbt models, captures the customer snapshot, runs dbt tests, and validates warehouse outputs.

Open Metabase at <http://localhost:3000>. Use these connection settings in Metabase:

- Host: `postgres`
- Port: `5432`
- Database: `ecom_warehouse`
- User: `postgres`
- Password: `postgres`

The project uses host port `5433` by default to avoid clashes with an existing local PostgreSQL installation. Change `DB_PORT` in `.env` if needed; keep PostgreSQL’s container port at `5432`.
## Validation and development

```bash
source .venv/bin/activate
bash -n run_pipeline.sh
python -m py_compile scripts/ingest.py scripts/validate_pipeline.py
cd dbt && dbt parse --profiles-dir "$PWD"
```

Run the complete workflow with `bash run_pipeline.sh`. Raw tables are initialized only when the Postgres volume is first created. To rebuild this disposable local warehouse:

```bash
docker compose down -v
docker compose up -d
```

Do not use `down -v` for data you want to keep.
## Useful queries

The queries in [docs/sql/metabase_examples.sql](docs/sql/metabase_examples.sql) cover raw counts, daily sales, customer history, top categories, and freshness. [dashboard.png](dashboard.png) shows the intended BI presentation.

## Scheduling

For a local demonstration, cron can invoke the same validated runner:

```cron
15 7 * * * cd $HOME/Desktop/de-ecommerce-warehouse && source .venv/bin/activate && export DBT_PROFILES_DIR=$(pwd)/dbt && bash run_pipeline.sh >> pipeline.log 2>&1
```

This is a local scheduler, not a production orchestration system. The runner is idempotent for products, customers, and order keys; each execution intentionally generates a new synthetic order batch.
