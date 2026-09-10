#!/bin/sh
set -e

echo "=== [CAR DELIGHTS] Production Container Initialization ==="

# Wait for database if PostgreSQL host is provided
if [ -n "$POSTGRES_HOST" ] || [ -n "$DATABASE_URL" ]; then
  DB_HOST="${POSTGRES_HOST:-db}"
  DB_PORT="${POSTGRES_PORT:-5432}"
  
  echo "Waiting for PostgreSQL database at $DB_HOST:$DB_PORT..."
  while ! nc -z "$DB_HOST" "$DB_PORT"; do
    sleep 1
  done
  echo "PostgreSQL database is ready and accepting connections."
fi

# Run database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files for WhiteNoise / Nginx
echo "Collecting static assets..."
python manage.py collectstatic --noinput --clear

# Optional auto-seed for brand new fresh deployment if requested
if [ "$AUTO_SEED" = "True" ] || [ "$AUTO_SEED" = "true" ]; then
  echo "Seeding database with Car Delights catalog..."
  python manage.py seed_car_delights || echo "Catalog already seeded."
fi

echo "=== [CAR DELIGHTS] Ready for traffic. Launching WSGI server... ==="
exec "$@"
