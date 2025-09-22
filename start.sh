#!/bin/sh
echo "Waiting for Postgres..."
until pg_isready -h database -p 5432; do
    sleep 2
done
echo "Postgres is ready, running migrations..."
alembic upgrade head
echo "Starting Uvicorn..."
uvicorn main:app --host 0.0.0.0 --port 8000 --log-level debug --reload
