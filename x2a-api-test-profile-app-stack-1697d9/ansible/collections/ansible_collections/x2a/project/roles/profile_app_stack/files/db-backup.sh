#!/bin/sh
set -eu

DB_NAME=${1:?database name is required}
DB_HOST=${2:?database host is required}
BACKUP_DIR=/var/backups/test-app
mkdir -p "${BACKUP_DIR}"
exec /usr/bin/pg_dump --host="${DB_HOST}" --dbname="${DB_NAME}" \
  --file="${BACKUP_DIR}/${DB_NAME}-$(date +%Y%m%d%H%M%S).sql"
