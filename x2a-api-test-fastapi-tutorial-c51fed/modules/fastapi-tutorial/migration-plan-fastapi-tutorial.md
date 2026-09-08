---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: A Python FastAPI web application cookbook that installs a tutorial application from GitHub, sets up PostgreSQL database with dedicated user and database, configures environment variables, and runs the service via systemd on port 8000.

## Service Type and Instances

**Service Type**: Web Server / Application Server

**Configured Instances**:
- **fastapi-tutorial**: Single FastAPI web application instance
  - Location/Path: /opt/fastapi-tutorial
  - Port/Socket: 8000 (HTTP)
  - Key Config: Python virtual environment, PostgreSQL backend, systemd service management

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
   - Step 1: Installs system packages: python3, python3-pip, python3-venv, git, postgresql, postgresql-contrib, libpq-dev
   - Step 2: Creates application directory /opt/fastapi-tutorial with 755 permissions
   - Step 3: Clones FastAPI tutorial from https://github.com/dibanez/fastapi_tutorial.git (main branch)
   - Step 4: Creates Python virtual environment at /opt/fastapi-tutorial/venv
   - Step 5: Installs Python dependencies from requirements.txt using pip
   - Step 6: Enables and starts PostgreSQL service
   - Step 7: Creates PostgreSQL database user 'fastapi' with password 'fastapi_password'
   - Step 8: Creates PostgreSQL database 'fastapi_db' owned by 'fastapi' user
   - Step 9: Grants ALL privileges on fastapi_db to fastapi user
   - Step 10: Deploys .env configuration file with PROJECT_NAME, API_VERSION, DATABASE_URL
   - Step 11: Deploys systemd service file for fastapi-tutorial service
   - Step 12: Reloads systemd daemon configuration
   - Step 13: Enables and starts fastapi-tutorial service
   - Resources used: package (7), directory (1), git (1), execute (4), service (2), file (2)

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
- **Variable(s)**: `fastapi_password` (hardcoded string)
- **Source file(s)**: cookbooks/fastapi-tutorial/recipes/default.rb
- **Current storage**: hardcoded
- **Usage context**: PostgreSQL database authentication for FastAPI application connection

## Checks for the Migration

**Files to verify**:
- /opt/fastapi-tutorial/ (application directory)
- /opt/fastapi-tutorial/venv/ (Python virtual environment)
- /opt/fastapi-tutorial/.env (environment configuration)
- /etc/systemd/system/fastapi-tutorial.service (systemd service file)
- /opt/fastapi-tutorial/requirements.txt (Python dependencies)
- /opt/fastapi-tutorial/app/main.py (FastAPI application entry point)

**Service endpoints to check**:
- Port 8000 (FastAPI application)
- Port 5432 (PostgreSQL)

**Templates rendered**: 0 templates (all configuration uses inline content in file resources)

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
curl -s http://localhost:8000/redoc

# Database connectivity for fastapi-tutorial instance
psql -h localhost -U fastapi -d fastapi_db -c "SELECT version();"
psql -h localhost -U fastapi -d fastapi_db -c "SELECT current_database(), current_user;"
sudo -u postgres psql -c "\l" | grep fastapi_db
sudo -u postgres psql -c "\du" | grep fastapi

# Python environment validation for fastapi-tutorial instance
ls -lah /opt/fastapi-tutorial/venv/
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip list | grep fastapi
/opt/fastapi-tutorial/venv/bin/pip list | grep uvicorn

# Configuration validation for fastapi-tutorial instance
cat /opt/fastapi-tutorial/.env
cat /opt/fastapi-tutorial/.env | grep -E 'PROJECT_NAME|API_VERSION|DATABASE_URL'
cat /etc/systemd/system/fastapi-tutorial.service
systemctl show fastapi-tutorial | grep -E 'ExecStart|WorkingDirectory|User'

# Git repository status for fastapi-tutorial instance
cd /opt/fastapi-tutorial && git status
cd /opt/fastapi-tutorial && git log --oneline -5
cd /opt/fastapi-tutorial && git remote -v

# Application files for fastapi-tutorial instance
ls -lah /opt/fastapi-tutorial/
ls -lah /opt/fastapi-tutorial/app/
cat /opt/fastapi-tutorial/requirements.txt

# Network listening for fastapi-tutorial instance
netstat -tulpn | grep 8000
netstat -tulpn | grep 5432
ss -tlnp | grep uvicorn
ss -tlnp | grep postgres
lsof -i :8000
lsof -i :5432

# Process checks for fastapi-tutorial instance
ps aux | grep uvicorn | grep -v grep
ps aux | grep postgres | grep -v grep
systemctl show fastapi-tutorial | grep -E 'MainPID|ActiveState|SubState'

# Database connection test for fastapi-tutorial instance
cd /opt/fastapi-tutorial && /opt/fastapi-tutorial/venv/bin/python -c "
import os
os.environ['DATABASE_URL'] = 'postgresql://fastapi:fastapi_password@localhost/fastapi_db'
import psycopg2
try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    print('Database connection successful')
    conn.close()
except Exception as e:
    print(f'Database connection failed: {e}')
"

# Logs for fastapi-tutorial instance
journalctl -u fastapi-tutorial -f --no-pager -n 50
journalctl -u postgresql -f --no-pager -n 20
```