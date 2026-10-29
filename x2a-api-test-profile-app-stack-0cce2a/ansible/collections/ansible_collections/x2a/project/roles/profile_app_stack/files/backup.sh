#!/usr/bin/env bash
set -euo pipefail

database="${1:?database name is required}"
host="${2:?database host is required}"
backup_dir="/var/backups/profile_app_stack"
mkdir -p "$backup_dir"
pg_dump --host "$host" --dbname "$database" > "$backup_dir/${database}-$(date +%Y%m%d%H%M%S).sql"
