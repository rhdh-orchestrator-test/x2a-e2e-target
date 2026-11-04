#!/bin/bash
# PostgreSQL database backup script
# Managed by Ansible — do not edit manually

set -euo pipefail

DB_NAME="${1:?Usage: $0 <db_name> <db_host>}"
DB_HOST="${2:-localhost}"
BACKUP_DIR="/var/backups/postgresql"
RETENTION_DAYS=30
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.sql.gz"

mkdir -p "${BACKUP_DIR}"

# Use the PostgreSQL service account for local peer authentication. Remote
# backups run as the cron user and use the configured PostgreSQL authentication.
if [[ "${DB_HOST}" == "localhost" || "${DB_HOST}" == "127.0.0.1" ]]; then
    runuser -u postgres -- pg_dump -h "${DB_HOST}" "${DB_NAME}" | gzip > "${BACKUP_FILE}"
else
    pg_dump -h "${DB_HOST}" "${DB_NAME}" | gzip > "${BACKUP_FILE}"
fi

chmod 600 "${BACKUP_FILE}"
find "${BACKUP_DIR}" -name "${DB_NAME}_*.sql.gz" -mtime +"${RETENTION_DAYS}" -delete

echo "Backup completed: ${BACKUP_FILE}"
