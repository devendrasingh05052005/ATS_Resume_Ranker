#!/usr/bin/env bash
set -euo pipefail

echo "Waiting for database and running migrations..."
ATTEMPTS=20
SLEEP_SECONDS=3
for i in $(seq 1 $ATTEMPTS); do
  if python manage.py migrate --noinput; then
    echo "Migrations applied."
    break
  fi
  echo "DB not ready yet (attempt $i/$ATTEMPTS). Retrying in ${SLEEP_SECONDS}s..."
  sleep ${SLEEP_SECONDS}
  if [[ "$i" == "$ATTEMPTS" ]]; then
    echo "Failed to run migrations after $ATTEMPTS attempts." >&2
    exit 1
  fi
done

echo "Starting Gunicorn..."
exec gunicorn ats_project.wsgi:application --bind 0.0.0.0:${PORT:-8000}
