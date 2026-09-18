---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: A Python web application cookbook that deploys a FastAPI tutorial application with PostgreSQL database backend. It installs system dependencies, clones the application from GitHub, sets up a Python virtual environment, configures PostgreSQL with a dedicated database and user, and runs the FastAPI application as a systemd service on port 8000.

## Service Type and Instances

**Service Type**: Application Server

**Configured Instances**:
- **fastapi-tutorial**: FastAPI web application service
  - Location/Path: /opt/fastapi-tutorial
  - Port/Socket: 8000 (HTTP)
  - Key Config: Runs via uvicorn ASGI server, uses PostgreSQL database, managed by systemd

## File Structure

```
recipes/default.rb
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
   - Step 9: Grants all privileges on fastapi_db to fastapi user
   - Step 10: Deploys .env configuration file with PROJECT_NAME, API_VERSION, and DATABASE_URL
   - Step 11: Deploys systemd service file for fastapi-tutorial service
   - Step 12: Reloads systemd daemon configuration
   - Step 13: Enables and starts fastapi-tutorial service
   - Resources used: package (7), directory (1), git (1), execute (4), service (2), file (2)
   - Iterations: No loops present

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: python3, python3-pip, python3-venv, git, postgresql, postgresql-contrib, libpq-dev
**Service dependencies**: postgresql.service (systemd dependency)

## Credentials

**Detection Summary**: 1 credential detected across 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Database Password
- **Variable(s)**: `fastapi_password` (hardcoded in PostgreSQL commands and DATABASE_URL)
- **Source file(s)**: cookbooks/fastapi-tutorial/recipes/default.rb
- **Current storage**: hardcoded
- **Usage context**: PostgreSQL database authentication for FastAPI application connection

## Checks for the Migration

**Files to verify**:
- /opt/fastapi-tutorial/.env (environment configuration)
- /etc/systemd/system/fastapi-tutorial.service (systemd service definition)
- /opt/fastapi-tutorial/venv/ (Python virtual environment)
- /opt/fastapi-tutorial/ (application source code from git)

**Service endpoints to check**:
- 8000 (FastAPI application on 0.0.0.0:8000)

**Templates rendered**: 0 (configuration files created using inline content)

## Pre-flight checks:
```bash
# Service status for fastapi-tutorial instance
systemctl status fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl is-enabled fastapi-tutorial
ps aux | grep "uvicorn app.main:app" | grep -v grep
pgrep -f "uvicorn app.main:app"

# PostgreSQL service status
systemctl status postgresql
ps aux | grep postgres

# FastAPI application health check
curl -I http://localhost:8000
curl -s http://localhost:8000/docs
curl -s http://localhost:8000/health || echo "Health endpoint may not exist"
netstat -tulpn | grep 8000
ss -tlnp | grep uvicorn
lsof -i :8000

# Database connectivity for fastapi-tutorial
psql -h localhost -U fastapi -d fastapi_db -c "SELECT version();"
psql -h localhost -U fastapi -d fastapi_db -c "SELECT current_database(), current_user;"
sudo -u postgres psql -c "SELECT usename FROM pg_user WHERE usename='fastapi';"
sudo -u postgres psql -c "SELECT datname FROM pg_database WHERE datname='fastapi_db';"
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity WHERE datname='fastapi_db';"

# Configuration validation for fastapi-tutorial
cat /opt/fastapi-tutorial/.env | grep -E 'PROJECT_NAME|API_VERSION|DATABASE_URL'
cat /etc/systemd/system/fastapi-tutorial.service | grep -E 'ExecStart|WorkingDirectory|User'
ls -la /opt/fastapi-tutorial/.env
ls -la /etc/systemd/system/fastapi-tutorial.service

# Python environment validation
ls -la /opt/fastapi-tutorial/venv/bin/
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip list | grep -E 'fastapi|uvicorn|psycopg'
test -f /opt/fastapi-tutorial/requirements.txt && echo "Requirements file exists"

# Application source code verification
ls -la /opt/fastapi-tutorial/
test -f /opt/fastapi-tutorial/app/main.py && echo "Main application file exists"
cd /opt/fastapi-tutorial && git status
cd /opt/fastapi-tutorial && git log --oneline -5

# Service logs
journalctl -u fastapi-tutorial -f --no-pager -n 50
journalctl -u postgresql -f --no-pager -n 20
tail -f /var/log/postgresql/postgresql-*.log
```