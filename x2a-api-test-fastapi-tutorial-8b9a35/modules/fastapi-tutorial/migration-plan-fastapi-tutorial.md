---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys a FastAPI tutorial web application with PostgreSQL database backend. It installs Python dependencies, clones the application from GitHub, sets up a virtual environment, configures PostgreSQL with a dedicated database and user, and runs the FastAPI app as a systemd service on port 8000.

## Service Type and Instances

**Service Type**: Web Server / Application Server

**Configured Instances**:
- **fastapi-tutorial**: FastAPI web application service
  - Location/Path: /opt/fastapi-tutorial
  - Port/Socket: 8000 (HTTP)
  - Key Config: Runs via uvicorn ASGI server, uses PostgreSQL backend, environment variables in .env file

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
   - Step 3: Clones FastAPI tutorial repository from https://github.com/dibanez/fastapi_tutorial.git (main branch)
   - Step 4: Creates Python virtual environment at /opt/fastapi-tutorial/venv
   - Step 5: Installs Python dependencies from requirements.txt using pip
   - Step 6: Enables and starts PostgreSQL service
   - Step 7: Creates PostgreSQL database user 'fastapi' with password 'fastapi_password'
   - Step 8: Creates PostgreSQL database 'fastapi_db' owned by 'fastapi' user
   - Step 9: Grants ALL privileges on fastapi_db to fastapi user
   - Step 10: Deploys .env configuration file with PROJECT_NAME, API_VERSION, and DATABASE_URL
   - Step 11: Deploys systemd service file for fastapi-tutorial service
   - Step 12: Reloads systemd daemon (triggered by service file changes)
   - Step 13: Enables and starts fastapi-tutorial service
   - Resources: package (7), directory (1), git (1), execute (3), service (2), file (2)
   - Iterations: N/A (no .each loops present)

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

**Service endpoints to check**:
- Port 8000 (FastAPI application)
- Port 5432 (PostgreSQL)

**Templates rendered**: 0 (uses inline content in file resources)

## Pre-flight checks:
```bash
# Service status for fastapi-tutorial instance
systemctl status fastapi-tutorial
systemctl status postgresql
ps aux | grep uvicorn
ps aux | grep postgres

# FastAPI application health for fastapi-tutorial instance
curl -I http://localhost:8000
curl -s http://localhost:8000/docs
curl -s http://localhost:8000/health || echo "Health endpoint may not exist"

# Database connectivity for fastapi-tutorial instance
psql -h localhost -U fastapi -d fastapi_db -c "SELECT version();"
psql -h localhost -U fastapi -d fastapi_db -c "SELECT current_database(), current_user;"

# Application files and permissions for fastapi-tutorial instance
ls -lah /opt/fastapi-tutorial/
ls -lah /opt/fastapi-tutorial/venv/
cat /opt/fastapi-tutorial/.env
python3 -c "import sys; print(sys.executable)"
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip list | grep -E 'fastapi|uvicorn|psycopg'

# Git repository status for fastapi-tutorial instance
cd /opt/fastapi-tutorial && git remote -v
cd /opt/fastapi-tutorial && git branch -v
cd /opt/fastapi-tutorial && git log --oneline -5

# Configuration validation for fastapi-tutorial instance
cat /opt/fastapi-tutorial/.env | grep -E 'PROJECT_NAME|API_VERSION|DATABASE_URL'
cat /etc/systemd/system/fastapi-tutorial.service
systemctl show fastapi-tutorial | grep -E 'ExecStart|WorkingDirectory|User'

# Database verification for fastapi-tutorial instance
sudo -u postgres psql -c "\du" | grep fastapi
sudo -u postgres psql -c "\l" | grep fastapi_db
sudo -u postgres psql -d fastapi_db -c "\dt"

# Network listening for fastapi-tutorial instance
netstat -tulpn | grep 8000
netstat -tulpn | grep 5432
ss -tlnp | grep uvicorn
ss -tlnp | grep postgres
lsof -i :8000
lsof -i :5432

# Process verification for fastapi-tutorial instance
pgrep -f uvicorn
pgrep -f postgres
ps aux | grep "uvicorn app.main:app" | grep -v grep
systemctl is-active fastapi-tutorial
systemctl is-enabled fastapi-tutorial

# Virtual environment validation for fastapi-tutorial instance
test -d /opt/fastapi-tutorial/venv && echo "Virtual environment exists"
test -f /opt/fastapi-tutorial/venv/bin/activate && echo "Virtual environment is valid"
/opt/fastapi-tutorial/venv/bin/python -c "import fastapi; print('FastAPI imported successfully')"
/opt/fastapi-tutorial/venv/bin/python -c "import uvicorn; print('Uvicorn imported successfully')"

# Logs for fastapi-tutorial instance
journalctl -u fastapi-tutorial -f --no-pager -n 50
journalctl -u postgresql -f --no-pager -n 20
tail -f /var/log/postgresql/postgresql-*.log
```