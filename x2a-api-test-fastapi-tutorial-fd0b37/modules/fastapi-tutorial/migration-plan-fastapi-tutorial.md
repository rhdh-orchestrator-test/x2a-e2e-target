---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: A FastAPI Python web application with PostgreSQL database backend. Single instance deployment running on port 8000 with systemd service management. Clones application from GitHub, sets up Python virtual environment, configures database, and deploys as a system service.

## Service Type and Instances

**Service Type**: Web Server / Application Server

**Configured Instances**:
- **fastapi-tutorial**: FastAPI Python web application
  - Location/Path: /opt/fastapi-tutorial
  - Port/Socket: 8000 (HTTP)
  - Key Config: Uvicorn ASGI server, PostgreSQL database connection, systemd service management

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
   - Iterations: None (no loops in this cookbook)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: python3, python3-pip, python3-venv, git, postgresql, postgresql-contrib, libpq-dev
**Service dependencies**: postgresql.service

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
curl -I http://localhost:8000
curl -s http://localhost:8000/docs
curl -s http://localhost:8000/health || echo "Health endpoint may not exist"

# Database connectivity for fastapi_db database
psql -h localhost -U fastapi -d fastapi_db -c "SELECT version();"
psql -h localhost -U fastapi -d fastapi_db -c "SELECT current_database(), current_user;"

# Application directory and files for fastapi-tutorial instance
ls -lah /opt/fastapi-tutorial/
ls -lah /opt/fastapi-tutorial/venv/
cat /opt/fastapi-tutorial/.env
test -f /opt/fastapi-tutorial/requirements.txt && echo "Requirements file exists"

# Python virtual environment for fastapi-tutorial instance
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip list | grep -E 'fastapi|uvicorn|psycopg'

# Systemd service configuration for fastapi-tutorial instance
cat /etc/systemd/system/fastapi-tutorial.service
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial

# Database setup verification for fastapi user and fastapi_db database
sudo -u postgres psql -c "\du fastapi"
sudo -u postgres psql -c "\l fastapi_db"
sudo -u postgres psql -c "\dp" fastapi_db

# Network listening for fastapi-tutorial instance
netstat -tulpn | grep 8000
netstat -tulpn | grep 5432
ss -tlnp | grep uvicorn
ss -tlnp | grep postgres
lsof -i :8000
lsof -i :5432

# Process checks for fastapi-tutorial instance
ps aux | grep uvicorn
top -p $(pgrep uvicorn) -n 1
cat /proc/$(pgrep uvicorn)/status | grep -E 'Threads|VmRSS|VmSize'

# Git repository status for fastapi-tutorial instance
cd /opt/fastapi-tutorial && git status
cd /opt/fastapi-tutorial && git log -1 --oneline
cd /opt/fastapi-tutorial && git remote -v

# Logs for fastapi-tutorial instance
journalctl -u fastapi-tutorial -f --no-pager -n 50
journalctl -u postgresql -f --no-pager -n 20
tail -f /var/log/postgresql/postgresql-*.log
```