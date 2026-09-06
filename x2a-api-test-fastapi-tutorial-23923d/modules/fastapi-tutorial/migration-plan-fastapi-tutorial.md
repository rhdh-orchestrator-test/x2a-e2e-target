---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: A FastAPI Python web application cookbook that installs a tutorial application from GitHub, sets up PostgreSQL database with a single database and user, and runs the application as a systemd service on port 8000.

## Service Type and Instances

**Service Type**: Web Server / Application Server

**Configured Instances**:
- **fastapi-tutorial**: FastAPI Python web application
  - Location/Path: /opt/fastapi-tutorial
  - Port/Socket: 8000 (HTTP)
  - Key Config: Runs via uvicorn ASGI server, uses PostgreSQL database, systemd managed service

## File Structure

```
recipes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs system packages: python3, python3-pip, python3-venv, git, postgresql, postgresql-contrib, libpq-dev
   - Creates application directory /opt/fastapi-tutorial with 755 permissions
   - Clones FastAPI tutorial repository from https://github.com/dibanez/fastapi_tutorial.git (branch: main)
   - Creates Python virtual environment at /opt/fastapi-tutorial/venv
   - Installs Python dependencies from requirements.txt using pip
   - Enables and starts PostgreSQL service
   - Creates PostgreSQL database user 'fastapi' with password 'fastapi_password'
   - Creates PostgreSQL database 'fastapi_db' owned by 'fastapi' user
   - Grants ALL privileges on fastapi_db to fastapi user
   - Creates .env configuration file with PROJECT_NAME, API_VERSION, and DATABASE_URL
   - Creates systemd service file for fastapi-tutorial service
   - Reloads systemd daemon configuration
   - Enables and starts fastapi-tutorial service
   - Iterations: No loops - single application instance configuration

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: python3, python3-pip, python3-venv, git, postgresql, postgresql-contrib, libpq-dev
**Service dependencies**: postgresql.service (FastAPI service depends on PostgreSQL)

## Credentials

**Detection Summary**: 1 credential detected across 1 file

**Source**:
  - **Provider**: Hardcoded
  - **URL**: N/A
  - **Path**: N/A

### Database Password
- **Variable(s)**: `fastapi_password`
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
- Port 8000 (HTTP on all interfaces)

**Templates rendered**: 0 (configuration files created with inline content)

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

# Database connectivity for fastapi_db
psql -h localhost -U fastapi -d fastapi_db -c "SELECT version();"
psql -h localhost -U fastapi -d fastapi_db -c "SELECT current_database(), current_user;"

# Configuration validation for fastapi-tutorial instance
cat /opt/fastapi-tutorial/.env | grep -E 'PROJECT_NAME|API_VERSION|DATABASE_URL'
cat /etc/systemd/system/fastapi-tutorial.service | grep -E 'ExecStart|WorkingDirectory|User'

# Python environment validation for fastapi-tutorial instance
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip list | grep -E 'fastapi|uvicorn|psycopg'
ls -la /opt/fastapi-tutorial/venv/bin/

# Application files for fastapi-tutorial instance
ls -la /opt/fastapi-tutorial/
cat /opt/fastapi-tutorial/requirements.txt
ls -la /opt/fastapi-tutorial/app/

# Logs for fastapi-tutorial instance
journalctl -u fastapi-tutorial -f --no-pager -n 50
journalctl -u postgresql -f --no-pager -n 20
tail -f /var/log/postgresql/postgresql-*.log

# Network listening for fastapi-tutorial instance
netstat -tulpn | grep 8000
ss -tlnp | grep uvicorn
lsof -i :8000

# Database status for fastapi_db
sudo -u postgres psql -c "\l" | grep fastapi_db
sudo -u postgres psql -c "\du" | grep fastapi
sudo -u postgres psql -d fastapi_db -c "SELECT schemaname,tablename FROM pg_tables WHERE schemaname='public';"

# Git repository status for fastapi-tutorial instance
cd /opt/fastapi-tutorial && git status
cd /opt/fastapi-tutorial && git log --oneline -5
cd /opt/fastapi-tutorial && git remote -v

# Process and resource checks for fastapi-tutorial instance
ps aux | grep fastapi-tutorial
systemctl show fastapi-tutorial | grep -E 'ActiveState|SubState|MainPID'
cat /proc/$(pgrep -f "uvicorn.*fastapi")/cmdline | tr '\0' ' '
```