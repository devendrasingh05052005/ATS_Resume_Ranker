#!/usr/bin/env bash
set -euo pipefail

echo "Starting Gunicorn..."
exec gunicorn ats_project.wsgi:application --bind 0.0.0.0:${PORT:-8000}
