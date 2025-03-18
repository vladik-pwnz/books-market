#!/bin/sh

echo "Waiting for PostgreSQL to be ready..."
until nc -z "$DB_HOST" "$DB_PORT"; do
  echo "PostgreSQL is not ready yet..."
  sleep 2
done
echo "✅ PostgreSQL is up!"

# Use Docker Secrets only if running in Swarm mode
SECRET_FILE="/run/secrets/fastapi_secret_key"

if [ -f "$SECRET_FILE" ]; then
    export SECRET_KEY=$(cat $SECRET_FILE)
    echo "✅ Loaded SECRET_KEY from Docker Secret."
elif [ -n "$SECRET_KEY" ]; then
    echo "✅ Loaded SECRET_KEY from .env."
else
    echo "❌ ERROR: SECRET_KEY is missing! Check .env or Docker Secrets."
    exit 1
fi

echo "Starting Uvicorn..."
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
