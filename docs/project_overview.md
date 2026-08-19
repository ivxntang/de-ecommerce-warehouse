# E-commerce Warehouse Project Overview

## Purpose

This project is a reproducible local data engineering pipeline for synthetic e-commerce data. It demonstrates how raw operational data can be loaded into PostgreSQL, cleaned and tested with dbt, modeled into analytics marts, and explored through Metabase.

The project is designed for portfolio use. It uses generated data rather than real customer information and can be run locally with Docker and Python.

## What The Project Does

Each pipeline run:

1. Connects to PostgreSQL using the shared `.env` configuration.
2. Creates or updates a 200-product catalogue.
3. Creates 1,000 synthetic customers on the first run.
4. Mutates a sample of existing customers on later runs to demonstrate history tracking.
5. Generates 300 synthetic orders and their order items.
6. Loads data into the PostgreSQL `raw` schema using conflict-safe inserts and updates.
7. Builds dbt staging views.
8. Runs the customer SCD2 snapshot.
9. Builds dimensional and fact marts.
10. Runs dbt data-quality tests.
11. Runs additional warehouse validation checks.

The generated order batch is intentionally new on each run. Products and customers are upserted, while order and order-item keys are protected against duplicate inserts.

## Architecture

```text
Synthetic Python generator
          |
          v
PostgreSQL raw schema
          |
          v
       dbt staging views
          |
          +--------------------+
          |                    |
          v                    v
Customer SCD2 snapshot     dbt marts
                               |
                               v
                         Metabase dashboards
```

## Technology Stack

- Python 3.14-compatible dependency set
- pandas for synthetic data generation and dataframe handling
- SQLAlchemy and psycopg2 for PostgreSQL access
- python-dotenv for environment loading
- PostgreSQL 15 running in Docker
- dbt Core and dbt-postgres for transformations, snapshots, and tests
- Metabase for interactive analytics
- Bash for pipeline orchestration

## Repository Structure

```text
.
├── .env.example                 Shared database configuration template
├── docker-compose.yml           PostgreSQL and Metabase services
├── requirements.txt             Python and dbt dependencies
├── run_pipeline.sh              End-to-end pipeline runner
├── scripts/
│   ├── db_config.py             Shared database connection builder
│   ├── ingest.py                Synthetic data generation and loading
│   └── validate_pipeline.py     Post-pipeline warehouse checks
├── warehouse/
│   └── init.sql                 PostgreSQL schemas, tables, keys, and indexes
├── dbt/
│   ├── dbt_project.yml          dbt project configuration
│   ├── profiles.yml             Environment-based dbt connection profile
│   ├── models/staging/          Cleaned source-aligned views and tests
│   ├── models/marts/            Analytics dimensions and facts
│   ├── snapshots/                Customer history snapshot
│   └── tests/                    Custom financial reconciliation tests
├── docs/sql/
│   └── metabase_examples.sql    Example queries for dashboard exploration
└── dashboard.png                Example dashboard image
```

## Database Layers

### Raw layer

The raw schema contains the ingestion tables:

| Table | Grain | Purpose |
| --- | --- | --- |
| `raw.raw_customers` | One row per customer | Current customer attributes |
| `raw.raw_products` | One row per product | Current product catalogue |
| `raw.raw_orders` | One row per order | Order header, customer, status, and total |
| `raw.raw_order_items` | One row per order line | Product, quantity, price, and line amount |

The raw tables use primary keys and foreign keys. Order items reference both orders and products, and orders reference customers.

### Staging layer

The staging models standardize types and expose source tables through dbt references:

- `stg_customers`
- `stg_products`
- `stg_orders`
- `stg_order_items`

These models are views in the `staging_staging` schema under the current dbt profile behavior.

### Marts layer

The marts are designed for reporting:

- `dim_product`: product attributes and prices
- `dim_customer`: customer history with SCD2 validity fields
- `fct_order_items`: one row per order item, including order status
- `fct_daily_sales`: daily gross sales, order count, and units for paid and shipped orders

Cancelled and refunded orders are excluded from `fct_daily_sales`.

## Customer SCD2 Snapshot

The `snap_customers` snapshot tracks changes to customer attributes over time using the `updated_at` timestamp.

The resulting history contains dbt metadata columns:

- `dbt_scd_id`: version identifier
- `dbt_updated_at`: source update time
- `dbt_valid_from`: beginning of the version validity period
- `dbt_valid_to`: end of the period, or null for the current version

The `dim_customer` mart renames and exposes these as:

- `valid_from`
- `valid_to`
- `is_current`

To see the feature in action, run the pipeline more than once. The ingestion script changes a sample of customer attributes on later runs, and the snapshot records new versions.

## Data Quality

The dbt test suite checks:

- required customer, product, order, and order-item fields
- uniqueness of customer, product, and order identifiers
- valid order statuses
- customer-to-order relationships
- order-to-order-item relationships
- product-to-order-item relationships
- line amount equals quantity multiplied by unit price
- order total equals the sum of its order items

The final Python validation also checks that required raw and mart tables are non-empty and that order items do not reference missing orders or products.

## Configuration Contract

Copy `.env.example` to `.env`. All application components use the same database variables:

```env
DB_HOST=localhost
DB_PORT=5433
DB_NAME=ecom_warehouse
DB_USER=postgres
DB_PASSWORD=postgres
DBT_SCHEMA=staging
```

Port behavior:

- `localhost:5433` is the host connection used by Python and dbt.
- Docker maps host port `5433` to PostgreSQL container port `5432`.
- Metabase connects over the Docker network using host `postgres` and port `5432`.

Do not commit `.env` or real credentials.

## How To Run

```bash
cd /Users/ivan/Desktop/de-ecommerce-warehouse
cp .env.example .env
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
docker compose up -d
bash run_pipeline.sh
```

Open Metabase at <http://localhost:3000> and configure PostgreSQL with:

- Host: `postgres`
- Port: `5432`
- Database: `ecom_warehouse`
- Username: `postgres`
- Password: `postgres`

## Validation Commands

Static checks:

```bash
python -m py_compile scripts/db_config.py scripts/ingest.py scripts/validate_pipeline.py
bash -n run_pipeline.sh
```

Dbt checks:

```bash
set -a
source .env
set +a
dbt parse --project-dir dbt --profiles-dir dbt
dbt snapshot --project-dir dbt --profiles-dir dbt
```

The complete validated workflow is:

```bash
bash run_pipeline.sh
```

The runner cleans stale dbt target artifacts, builds staging models, snapshots customers, builds marts, runs dbt tests, and validates warehouse outputs.

## Metabase Query Examples

See [sql/metabase_examples.sql](sql/metabase_examples.sql) for examples covering:

- raw table counts
- recent daily sales
- customers with multiple SCD2 versions
- one customer's history
- top product categories
- latest order freshness

## Resetting The Local Database

The PostgreSQL data is stored in a Docker volume. To rebuild the disposable local warehouse from scratch:

```bash
docker compose down -v
docker compose up -d
bash run_pipeline.sh
```

Do not run `docker compose down -v` if you need to preserve the existing database.

## Portfolio Scope And Limitations

This project is complete as a local portfolio demonstration. It is not intended to represent a production deployment. Important differences include:

- synthetic data instead of a real source system
- Docker Compose instead of managed infrastructure
- cron or manual execution instead of a production orchestrator
- local environment variables instead of a secrets manager
- no cloud warehouse or public uptime guarantee
- no production alerting or centralized observability

A future production-oriented version could add CI/CD, cloud PostgreSQL, a managed secrets store, scheduled orchestration, retry policies, monitoring, alerting, and role-based database access.
