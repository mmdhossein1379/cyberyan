#!/bin/sh


set -e


echo "Waiting for database..."

python -m app.scripts.wait_for_db


echo "Running database migrations..."

alembic upgrade head


echo "Checking database seed..."

python -m app.scripts.seed


echo "Checking Elasticsearch index..."

python -m app.scripts.index_elasticsearch &

echo "Starting FastAPI..."
exec uvicorn app.main:app \
  --host 0.0.0.0 \
  --port "${PORT:-8000}"
