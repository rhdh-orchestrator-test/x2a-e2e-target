---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys a FastAPI tutorial web application with PostgreSQL database backend. It installs Python dependencies, clones the application from GitHub, sets up a PostgreSQL database with dedicated user, and configures the FastAPI service to run via systemd on port 8000.

## Service Type and Instances

**Service Type**: Web Server / Application Server

**Configured Instances**:
- **fastapi-tutorial**: FastAPI web application service
  - Location/Path: /opt/fastapi-tutorial
  - Port/Socket: 8000 (HTTP)
  - Key Config: Runs via uvicorn ASGI server, connects to PostgreSQL database
  - Database: fastapi_db with dedicated user 'fastapi'
  - Repository: https://github.com/dibanez/fastapi_tutorial.git (main branch)

## File Structure

```
recipes/default.rb
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
   - Creates systemd service unit file for fastapi-tutorial service
   - Reloads systemd daemon configuration
   - Enables and starts fastapi-tutorial service
   - Resources: package (1), directory (1), git (1), execute (4), service (2), file (2)

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
- /etc/systemd/system/fastapi-tutorial.service (systemd unit file)

**Service endpoints to check**:
- Ports listening: 8000 (FastAPI application)
- Network interfaces: 0.0.0.0:8000 (all interfaces)

**Templates rendered**:
- No templates used (configuration deployed via file resources with inline content)

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
curl -s http://localhost:8000/health || curl -s http://localhost:8000/

# Database connectivity for fastapi_db database
psql -h localhost -U fastapi -d fastapi_db -c "SELECT version();"
psql -h localhost -U fastapi -d fastapi_db -c "SELECT current_database(), current_user;"
sudo -u postgres psql -c "\l" | grep fastapi_db
sudo -u postgres psql -c "\du" | grep fastapi

# Python environment validation for fastapi-tutorial instance
ls -lah /opt/fastapi-tutorial/venv/
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip list | grep fastapi
/opt/fastapi-tutorial/venv/bin/pip list | grep uvicorn

# Application files for fastapi-tutorial instance
ls -lah /opt/fastapi-tutorial/
cat /opt/fastapi-tutorial/.env
git -C /opt/fastapi-tutorial status
git -C /opt/fastapi-tutorial log --oneline -5

# Configuration validation for fastapi-tutorial service
cat /etc/systemd/system/fastapi-tutorial.service
systemctl show fastapi-tutorial | grep -E 'ExecStart|WorkingDirectory|User'

# Logs for fastapi-tutorial instance
journalctl -u fastapi-tutorial -f --lines 50
journalctl -u postgresql -f --lines 20
tail -f /var/log/postgresql/postgresql-*.log

# Network listening for fastapi-tutorial on port 8000
netstat -tulpn | grep 8000
ss -tlnp | grep uvicorn
lsof -i :8000

# Process verification for fastapi-tutorial instance
pgrep -f uvicorn
ps aux | grep "uvicorn app.main:app"
cat /proc/$(pgrep -f uvicorn)/cmdline | tr '\0' ' '

# Database connection from fastapi-tutorial application
cd /opt/fastapi-tutorial && /opt/fastapi-tutorial/venv/bin/python -c "
import os
from sqlalchemy import create_engine
engine = create_engine(os.getenv('DATABASE_URL', 'postgresql://fastapi:fastapi_password@localhost/fastapi_db'))
conn = engine.connect()
result = conn.execute('SELECT 1')
print('Database connection successful:', result.fetchone())
conn.close()
"
```