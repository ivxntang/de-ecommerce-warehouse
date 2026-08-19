#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

if [ ! -f ".env" ]; then
  echo "Missing .env. Run: cp .env.example .env" >&2
  exit 1
fi

set -a
source .env
set +a

if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
fi

echo "[1/6] Generate + load incremental synthetic data"
python scripts/ingest.py

echo "[2/6] dbt run (staging models)"
export DBT_PROFILES_DIR="$(pwd)/dbt"
export DBT_PROJECT_DIR="$(pwd)/dbt"
dbt clean --project-dir "$DBT_PROJECT_DIR" --profiles-dir "$DBT_PROFILES_DIR"
dbt deps --project-dir "$DBT_PROJECT_DIR" --profiles-dir "$DBT_PROFILES_DIR"
dbt run --project-dir "$DBT_PROJECT_DIR" --select staging --profiles-dir "$DBT_PROFILES_DIR"

echo "[3/6] dbt snapshot (SCD2 customers)"
dbt snapshot --project-dir "$DBT_PROJECT_DIR" --profiles-dir "$DBT_PROFILES_DIR"

echo "[4/6] dbt run (marts)"
dbt run --project-dir "$DBT_PROJECT_DIR" --select marts --profiles-dir "$DBT_PROFILES_DIR"

echo "[5/6] dbt test"
dbt test --project-dir "$DBT_PROJECT_DIR" --profiles-dir "$DBT_PROFILES_DIR"

echo "[6/6] Validate warehouse outputs"
python scripts/validate_pipeline.py

echo "Done."
