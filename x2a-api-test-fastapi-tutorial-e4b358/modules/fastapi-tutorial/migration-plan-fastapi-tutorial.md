---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys a FastAPI tutorial web application with PostgreSQL database backend. It installs Python dependencies, clones the application from GitHub, sets up a virtual environment, configures PostgreSQL with a dedicated database and user, and runs the FastAPI service on port 8000 via systemd.

## Service Type and Instances

**Service Type**: Web Server / Application Server

**Configured Instances**:
- **fastapi-tutorial**: FastAPI web application service
  - Location/Path: /opt/fastapi-tutorial
  - Port/Socket: 8000 (HTTP)
  - Key Config: Runs via uvicorn ASGI server, uses PostgreSQL database, environment variables in .env file

## File Structure

```
recipes/default.rb
```

**Providers:**
```
(None - uses only built-in Chef resources)
```

**Templates:**
```
(None - uses inline content in file resources)
```

**Attributes:**
```
(None - no attribute files present)
```

**Files:**
```
(None - no static files deployed)
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
   - Deploys .env configuration file with PROJECT_NAME, API_VERSION, and DATABASE_URL
   - Deploys systemd service file for fastapi-tutorial service
   - Reloads systemd daemon (triggered by service file changes)
   - Enables and starts fastapi-tutorial service

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
- Ports listening: 8000 (FastAPI HTTP server)
- Network interfaces: 0.0.0.0:8000 (binds to all interfaces)

**Templates rendered**: None (uses inline content in file resources)

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

# Application environment for fastapi-tutorial instance
cat /opt/fastapi-tutorial/.env
ls -la /opt/fastapi-tutorial/
ls -la /opt/fastapi-tutorial/venv/bin/
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip list | grep -E 'fastapi|uvicorn|psycopg'

# Git repository status for fastapi-tutorial instance
cd /opt/fastapi-tutorial && git remote -v
cd /opt/fastapi-tutorial && git branch -a
cd /opt/fastapi-tutorial && git log --oneline -5

# Systemd service configuration for fastapi-tutorial instance
cat /etc/systemd/system/fastapi-tutorial.service
systemctl show fastapi-tutorial | grep -E 'ExecStart|WorkingDirectory|User'
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial

# Network listening for fastapi-tutorial instance
netstat -tulpn | grep 8000
ss -tlnp | grep uvicorn
lsof -i :8000

# Logs for fastapi-tutorial instance
journalctl -u fastapi-tutorial -f --no-pager -n 50
journalctl -u postgresql -f --no-pager -n 20
tail -f /var/log/postgresql/postgresql-*.log

# Process verification for fastapi-tutorial instance
pgrep -f uvicorn
ps aux | grep "uvicorn app.main:app"
cat /proc/$(pgrep -f uvicorn)/cmdline | tr '\0' ' '

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
```