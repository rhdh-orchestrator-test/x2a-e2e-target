#!/usr/bin/env bash
set -euo pipefail

db_name="${1:?database name is required}"
db_host="${2:?database host is required}"
backup_dir="/var/backups/${db_name}"
mkdir -p "${backup_dir}"
backup_file="${backup_dir}/${db_name}-$(date +%Y%m%d%H%M%S).sql.gz"

pg_dump --host="${db_host}" --dbname="${db_name}" | gzip > "${backup_file}"
find "${backup_dir}" -type f -name '*.sql.gz' -mtime +7 -delete
