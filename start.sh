#!/usr/bin/env bash
set -euo pipefail

# Safety: fail fast if DATABASE_URL isn't set
: "${DATABASE_URL:?DATABASE_URL is not set}"

# Run migrations every startup (safe for dev/prod)
alembic upgrade head

# Start server
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT}"
touch