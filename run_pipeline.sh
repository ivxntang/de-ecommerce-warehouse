#!/usr/bin/env bash
set -euo pipefail

if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
fi

echo "[1/5] Generate + load incremental synthetic data"
python scripts/ingest.py

echo "[2/5] dbt run (staging + marts)"
export DBT_PROFILES_DIR="$(pwd)/dbt"
dbt deps || true
dbt run

echo "[3/5] dbt snapshot (SCD2 customers)"
dbt snapshot

echo "[4/5] dbt run (rebuild marts that depend on snapshots)"
dbt run --select marts

echo "[5/5] dbt test"
dbt test

echo "Done."
