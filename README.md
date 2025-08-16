# E-commerce Orders Warehouse (Local, macOS-friendly)

A **universal, recruiter-friendly** data engineering project: synthetic e-commerce data → Postgres warehouse → dbt transforms/tests + SCD2 (snapshots) → Metabase dashboard. Incremental loads, idempotent upserts, cron scheduling.

## Stack
- **Python 3.11** (data gen + loaders with `pandas`, `SQLAlchemy`)
- **Postgres 15** (Docker)
- **dbt-core + dbt-postgres** (staging + marts + **SCD2 customers via snapshots**)
- **Metabase** (Docker) for BI
- **cron** for daily incrementals

## Quick start
```bash
cd ~/Desktop
unzip de-ecommerce-warehouse.zip -d .
cd de-ecommerce-warehouse

# Start services
docker compose up -d

# Python env
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Env vars
cp .env.example .env

# Point dbt to local profiles
export DBT_PROFILES_DIR=$(pwd)/dbt

# First run (seed baseline + one incremental batch)
bash run_pipeline.sh
```

Open Metabase: http://localhost:3000
Connect to Postgres:
- Host: **host.docker.internal**
- Port: **5432**
- DB: **ecom_warehouse**
- User: **postgres**
- Password: **postgres**

## What to demo
- **Star schema**: `dim_customer` (SCD2 from snapshots), `dim_product`; facts: `fct_order_items`, `fct_daily_sales`
- **Incremental loads**: new orders daily; a % of customers change attributes → SCD2 rows
- **Quality**: dbt tests (unique/not_null), constraints in raw
- **Orchestration**: single runner + cron entry
- **Docs**: show `dbt docs generate` (optional)

## Cron (daily 7:15 AM SGT)
```bash
crontab -e
15 7 * * * cd $HOME/Desktop/de-ecommerce-warehouse && source .venv/bin/activate && export DBT_PROFILES_DIR=$(pwd)/dbt && bash run_pipeline.sh >> pipeline.log 2>&1
```
