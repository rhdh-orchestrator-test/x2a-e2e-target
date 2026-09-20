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
  - Key Config: Runs via uvicorn ASGI server, uses PostgreSQL database, environment-based configuration

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
   - Step 10: Deploys .env configuration file with PROJECT_NAME, API_VERSION, and DATABASE_URL
   - Step 11: Deploys systemd service file for fastapi-tutorial service
   - Step 12: Reloads systemd daemon configuration
   - Step 13: Enables and starts fastapi-tutorial service
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
- 8000 (FastAPI application on 0.0.0.0:8000)

**Templates rendered**:
- No templates - uses inline content in file resources

## Pre-flight checks:
```bash
# Service status for fastapi-tutorial instance
systemctl status fastapi-tutorial
systemctl status postgresql
ps aux | grep uvicorn
ps aux | grep postgres

# Application health check for fastapi-tutorial instance
curl -I http://localhost:8000
curl -s http://localhost:8000/docs
curl -s http://localhost:8000/health || echo "Health endpoint may not exist"

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
grep -E 'PROJECT_NAME|API_VERSION|DATABASE_URL' /opt/fastapi-tutorial/.env
cat /etc/systemd/system/fastapi-tutorial.service
systemctl show fastapi-tutorial | grep -E 'ExecStart|WorkingDirectory|User'

# Application files for fastapi-tutorial instance
ls -lah /opt/fastapi-tutorial/
ls -lah /opt/fastapi-tutorial/app/
cat /opt/fastapi-tutorial/requirements.txt
git -C /opt/fastapi-tutorial status
git -C /opt/fastapi-tutorial log --oneline -5

# Network listening for fastapi-tutorial instance
netstat -tulpn | grep 8000
ss -tlnp | grep uvicorn
lsof -i :8000

# PostgreSQL service for fastapi-tutorial instance
systemctl status postgresql
netstat -tulpn | grep 5432
ss -tlnp | grep postgres
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity WHERE datname='fastapi_db';"

# Logs for fastapi-tutorial instance
journalctl -u fastapi-tutorial -f --no-pager -n 50
journalctl -u postgresql -f --no-pager -n 20
tail -f /var/log/postgresql/postgresql-*.log
systemctl --failed | grep -E 'fastapi-tutorial|postgresql'

# Process verification for fastapi-tutorial instance
pgrep -f uvicorn
pgrep postgres
ps aux | grep -E 'uvicorn|postgres' | grep -v grep

# File permissions for fastapi-tutorial instance
ls -lah /opt/fastapi-tutorial/.env
ls -lah /etc/systemd/system/fastapi-tutorial.service
stat /opt/fastapi-tutorial/ | grep Access
```