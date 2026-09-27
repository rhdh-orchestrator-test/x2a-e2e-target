---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: A Python FastAPI web application server that clones a tutorial repository from GitHub, sets up a PostgreSQL database with a single database and user, configures a Python virtual environment with dependencies, and runs the application as a systemd service on port 8000.

## Service Type and Instances

**Service Type**: Web Server / Application Server

**Configured Instances**:
- **fastapi-tutorial**: FastAPI Python web application
  - Location/Path: /opt/fastapi-tutorial
  - Port/Socket: 8000 (HTTP)
  - Key Config: Runs via uvicorn ASGI server, uses PostgreSQL database, systemd service management

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
   - Clones FastAPI tutorial repository from https://github.com/dibanez/fastapi_tutorial.git (main branch)
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
- **Variable(s)**: `fastapi_password` (hardcoded string)
- **Source file(s)**: cookbooks/fastapi-tutorial/recipes/default.rb
- **Current storage**: hardcoded
- **Usage context**: PostgreSQL database authentication for fastapi user, used in DATABASE_URL connection string

## Checks for the Migration

**Files to verify**:
- /opt/fastapi-tutorial/ (application directory)
- /opt/fastapi-tutorial/venv/ (Python virtual environment)
- /opt/fastapi-tutorial/.env (environment configuration)
- /etc/systemd/system/fastapi-tutorial.service (systemd service file)
- /opt/fastapi-tutorial/requirements.txt (Python dependencies)

**Service endpoints to check**:
- Port 8000 (HTTP on all interfaces)

**Templates rendered**:
- No templates used (configuration files created with inline content)

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

# Database connectivity for fastapi_db database
psql -h localhost -U fastapi -d fastapi_db -c "SELECT version();"
psql -h localhost -U fastapi -d fastapi_db -c "SELECT current_database(), current_user;"
sudo -u postgres psql -c "SELECT usename FROM pg_user WHERE usename='fastapi';"
sudo -u postgres psql -c "SELECT datname FROM pg_database WHERE datname='fastapi_db';"

# Python environment validation for fastapi-tutorial instance
ls -la /opt/fastapi-tutorial/venv/bin/python3
/opt/fastapi-tutorial/venv/bin/python3 --version
/opt/fastapi-tutorial/venv/bin/pip list | grep fastapi
/opt/fastapi-tutorial/venv/bin/pip list | grep uvicorn

# Configuration validation for fastapi-tutorial instance
cat /opt/fastapi-tutorial/.env
test -f /opt/fastapi-tutorial/requirements.txt && echo "Requirements file exists"

# Git repository validation for fastapi-tutorial instance
cd /opt/fastapi-tutorial && git remote -v
cd /opt/fastapi-tutorial && git branch -a
cd /opt/fastapi-tutorial && git log --oneline -5

# Systemd service validation for fastapi-tutorial instance
cat /etc/systemd/system/fastapi-tutorial.service
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial

# Network listening for fastapi-tutorial instance
netstat -tulpn | grep 8000
ss -tlnp | grep uvicorn
lsof -i :8000

# Process checks for fastapi-tutorial instance
ps aux | grep uvicorn
pgrep -f "uvicorn app.main:app"
systemctl show fastapi-tutorial | grep -E 'MainPID|ActiveState|SubState'

# File permissions for fastapi-tutorial instance
ls -la /opt/fastapi-tutorial/
ls -la /opt/fastapi-tutorial/.env
ls -la /etc/systemd/system/fastapi-tutorial.service

# Database connection test for fastapi-tutorial instance
cd /opt/fastapi-tutorial && /opt/fastapi-tutorial/venv/bin/python3 -c "
import os
from sqlalchemy import create_engine
engine = create_engine('postgresql://fastapi:fastapi_password@localhost/fastapi_db')
conn = engine.connect()
result = conn.execute('SELECT 1')
print('Database connection successful')
conn.close()
"

# Logs for fastapi-tutorial instance
journalctl -u fastapi-tutorial -f --no-pager -n 50
journalctl -u postgresql -f --no-pager -n 20
```