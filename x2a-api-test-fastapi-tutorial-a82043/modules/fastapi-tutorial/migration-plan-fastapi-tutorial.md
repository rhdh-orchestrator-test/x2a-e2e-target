---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys a FastAPI tutorial web application with PostgreSQL database backend. It installs Python 3, clones a FastAPI tutorial repository from GitHub, sets up a virtual environment, configures PostgreSQL with a dedicated database and user, and runs the application as a systemd service on port 8000.

## Service Type and Instances

**Service Type**: Web Server / Application Server

**Configured Instances**:
- **fastapi-tutorial**: FastAPI web application service
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
   - Resources used: package (8), directory (1), git (1), execute (4), service (2), file (2)
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
- **Variable(s)**: fastapi_password
- **Source file(s)**: cookbooks/fastapi-tutorial/recipes/default.rb
- **Current storage**: Hardcoded in SQL commands and DATABASE_URL
- **Usage context**: PostgreSQL database authentication for FastAPI application connection

## Checks for the Migration

**Files to verify**: 
- /opt/fastapi-tutorial/ (application directory)
- /opt/fastapi-tutorial/venv/ (Python virtual environment)
- /opt/fastapi-tutorial/.env (environment configuration)
- /etc/systemd/system/fastapi-tutorial.service (systemd service file)
- /opt/fastapi-tutorial/requirements.txt (Python dependencies)

**Service endpoints to check**: 8000 (HTTP on all interfaces)
**Templates rendered**: None (configuration files created with static content)

## Pre-flight checks:
```bash
# Service status for fastapi-tutorial instance
systemctl status fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
ps aux | grep uvicorn
journalctl -u fastapi-tutorial -f --no-pager -n 50

# PostgreSQL service status
systemctl status postgresql
ps aux | grep postgres
journalctl -u postgresql -f --no-pager -n 20

# Application health check for fastapi-tutorial
curl -I http://localhost:8000
curl -s http://localhost:8000/docs
netstat -tulpn | grep 8000
ss -tlnp | grep uvicorn
lsof -i :8000

# Database connectivity for fastapi_db
psql -h localhost -U fastapi -d fastapi_db -c "SELECT version();"
psql -h localhost -U fastapi -d fastapi_db -c "SELECT current_database(), current_user;"
sudo -u postgres psql -c "\l" | grep fastapi_db
sudo -u postgres psql -c "\du" | grep fastapi

# Configuration validation for fastapi-tutorial
cat /opt/fastapi-tutorial/.env
test -f /opt/fastapi-tutorial/requirements.txt && echo "Requirements file exists"
cat /etc/systemd/system/fastapi-tutorial.service
ls -lah /opt/fastapi-tutorial/
stat /opt/fastapi-tutorial/.env

# Python environment validation
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip list
source /opt/fastapi-tutorial/venv/bin/activate && python -c "import fastapi; print(fastapi.__version__)"

# Git repository validation
cd /opt/fastapi-tutorial && git remote -v
cd /opt/fastapi-tutorial && git branch -a
cd /opt/fastapi-tutorial && git log --oneline -5
```