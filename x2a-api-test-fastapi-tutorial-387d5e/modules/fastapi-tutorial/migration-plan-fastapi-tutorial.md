---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys a FastAPI tutorial web application with PostgreSQL database backend. It installs Python 3, clones the FastAPI tutorial from GitHub, sets up a virtual environment, configures PostgreSQL with a dedicated database and user, and runs the application as a systemd service on port 8000.

## Service Type and Instances

**Service Type**: Web Server / Application Server

**Configured Instances**:
- **fastapi-tutorial**: FastAPI web application service
  - Location/Path: /opt/fastapi-tutorial
  - Port/Socket: 8000 (HTTP)
  - Key Config: Runs via uvicorn ASGI server, uses PostgreSQL database, systemd managed service

## File Structure

```
cookbooks/fastapi-tutorial/
├── recipes/
│   └── default.rb
└── metadata.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Step 1: Installs system packages (python3, python3-pip, python3-venv, git, postgresql, postgresql-contrib, libpq-dev)
   - Step 2: Creates application directory /opt/fastapi-tutorial with 755 permissions
   - Step 3: Clones FastAPI tutorial repository from https://github.com/dibanez/fastapi_tutorial.git (main branch)
   - Step 4: Creates Python virtual environment at /opt/fastapi-tutorial/venv
   - Step 5: Installs Python dependencies from requirements.txt using pip
   - Step 6: Enables and starts PostgreSQL service
   - Step 7: Creates PostgreSQL database user 'fastapi' with password 'fastapi_password'
   - Step 8: Creates PostgreSQL database 'fastapi_db' owned by 'fastapi' user
   - Step 9: Grants ALL privileges on fastapi_db to fastapi user
   - Step 10: Creates .env configuration file with PROJECT_NAME, API_VERSION, and DATABASE_URL
   - Step 11: Creates systemd service file for fastapi-tutorial service
   - Step 12: Reloads systemd daemon configuration
   - Step 13: Enables and starts fastapi-tutorial service
   - Resources: package (7), directory (1), git (1), execute (4), service (2), file (2)

## Dependencies

**External cookbook dependencies**: None (no external cookbooks required)
**System package dependencies**: python3, python3-pip, python3-venv, git, postgresql, postgresql-contrib, libpq-dev
**Service dependencies**: postgresql.service (FastAPI service depends on PostgreSQL)

## Credentials

**Detection Summary**: 1 credential detected across 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Database Password
- **Variable(s)**: `fastapi_password` (hardcoded in SQL commands and DATABASE_URL)
- **Source file(s)**: cookbooks/fastapi-tutorial/recipes/default.rb
- **Current storage**: hardcoded
- **Usage context**: PostgreSQL database authentication for FastAPI application connection

## Checks for the Migration

**Files to verify**:
- /opt/fastapi-tutorial/ (application directory)
- /opt/fastapi-tutorial/venv/ (Python virtual environment)
- /opt/fastapi-tutorial/.env (environment configuration)
- /etc/systemd/system/fastapi-tutorial.service (systemd service file)
- PostgreSQL database 'fastapi_db' and user 'fastapi'

**Service endpoints to check**:
- Port 8000 (FastAPI application)
- Port 5432 (PostgreSQL)

**Templates rendered**: 0 (configuration files created inline with file resources)

## Pre-flight checks:
```bash
# Service status for fastapi-tutorial instance
systemctl status fastapi-tutorial
systemctl status postgresql
ps aux | grep uvicorn
ps aux | grep postgres

# FastAPI application health for fastapi-tutorial instance
curl -I http://localhost:8000/
curl -s http://localhost:8000/docs
curl -s http://localhost:8000/health || echo "Health endpoint may not exist"

# Database connectivity for fastapi-tutorial instance
sudo -u postgres psql -c "\l" | grep fastapi_db
sudo -u postgres psql -c "\du" | grep fastapi
psql -h localhost -U fastapi -d fastapi_db -c "SELECT version();"
psql -h localhost -U fastapi -d fastapi_db -c "SELECT current_database(), current_user;"

# Application configuration for fastapi-tutorial instance
cat /opt/fastapi-tutorial/.env
grep -E 'PROJECT_NAME|API_VERSION|DATABASE_URL' /opt/fastapi-tutorial/.env

# Python environment validation for fastapi-tutorial instance
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip list | grep -E 'fastapi|uvicorn|psycopg'
ls -la /opt/fastapi-tutorial/venv/bin/

# Git repository status for fastapi-tutorial instance
cd /opt/fastapi-tutorial && git remote -v
cd /opt/fastapi-tutorial && git branch -a
cd /opt/fastapi-tutorial && git log --oneline -5

# Systemd service configuration for fastapi-tutorial instance
cat /etc/systemd/system/fastapi-tutorial.service
systemctl show fastapi-tutorial | grep -E 'ActiveState|SubState|MainPID'
systemctl is-enabled fastapi-tutorial
systemctl is-enabled postgresql

# Network listening for fastapi-tutorial instance
netstat -tulpn | grep 8000
netstat -tulpn | grep 5432
ss -tlnp | grep uvicorn
ss -tlnp | grep postgres
lsof -i :8000
lsof -i :5432

# Application directory structure for fastapi-tutorial instance
ls -lah /opt/fastapi-tutorial/
ls -lah /opt/fastapi-tutorial/venv/
find /opt/fastapi-tutorial -name "*.py" | head -10
cat /opt/fastapi-tutorial/requirements.txt

# Database connection test for fastapi-tutorial instance
cd /opt/fastapi-tutorial && /opt/fastapi-tutorial/venv/bin/python -c "
import os
from sqlalchemy import create_engine
engine = create_engine('postgresql://fastapi:fastapi_password@localhost/fastapi_db')
conn = engine.connect()
result = conn.execute('SELECT 1')
print('Database connection successful:', result.fetchone())
conn.close()
"

# Logs for fastapi-tutorial instance
journalctl -u fastapi-tutorial -f --no-pager -n 50
journalctl -u postgresql -f --no-pager -n 20
tail -f /var/log/postgresql/postgresql-*.log
```