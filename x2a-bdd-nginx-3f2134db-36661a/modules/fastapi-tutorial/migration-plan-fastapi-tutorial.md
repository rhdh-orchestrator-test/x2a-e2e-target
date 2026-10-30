---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This Chef cookbook deploys the FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, PostgreSQL development dependencies, and application requirements; creates a Python virtual environment; configures the local PostgreSQL role `fastapi` and database `fastapi_db`; writes the database connection configuration to `.env`; and runs the application through the `fastapi-tutorial` systemd service on port `8000`.

## Service Type and Instances

**Service Type**: Application server with a local PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application served by Uvicorn
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Branch/revision: `main`
  - Location/Path: `/opt/fastapi-tutorial`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Environment file: `/opt/fastapi-tutorial/.env`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Service user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Start command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Listen address: `0.0.0.0`
  - Port: `8000`
  - Restart policy: `Restart=always`

- **postgresql**: Local PostgreSQL database service for the FastAPI application
  - Service name: `postgresql`
  - Database user: `fastapi`
  - Database password: `fastapi_password`
  - Database name: `fastapi_db`
  - Database owner: `fastapi`
  - Host: `localhost`
  - Default TCP port: `5432` when TCP listening is enabled
  - Connection string: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`

## File Structure

**MANDATORY: Preserve this section from the original plan.**

```text
cookbooks/fastapi-tutorial/
└── recipes/
    └── default.rb
```

**Recipes:**
```text
cookbooks/fastapi-tutorial/recipes/default.rb
```

**Providers:**
```text
None
```

**Templates:**
```text
None
```

**Attributes:**
```text
None
```

**Files:**
```text
None
```

The cookbook creates these files dynamically using inline Chef `file` resources:

```text
/opt/fastapi-tutorial/.env
/etc/systemd/system/fastapi-tutorial.service
```

These are not cookbook static files or templates.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the required system packages: `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` into `/opt/fastapi-tutorial` at revision `main`.
   - Creates `/opt/fastapi-tutorial/venv` with `python3 -m venv` when the virtual-environment path does not already exist.
   - Installs Python dependencies from `/opt/fastapi-tutorial/requirements.txt` using `/opt/fastapi-tutorial/venv/bin/pip`.
   - Enables and starts the `postgresql` service.
   - Creates the PostgreSQL role `fastapi` with password `fastapi_password`.
   - Creates the PostgreSQL database `fastapi_db` owned by `fastapi`.
   - Grants all privileges on `fastapi_db` to `fastapi`.
   - Uses `|| true` for the PostgreSQL shell commands, allowing existing roles, databases, and grants without failing.
   - Writes `/opt/fastapi-tutorial/.env` with owner `root`, group `root`, and mode `0644`.
   - Renders the following environment values:
     - `PROJECT_NAME="FastAPI Tutorial"`
     - `API_VERSION=1.0.0`
     - `DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db`
   - Writes `/etc/systemd/system/fastapi-tutorial.service` with owner `root`, group `root`, and mode `0644`.
   - Defines the `fastapi-tutorial` systemd service to run as `root` from `/opt/fastapi-tutorial`.
   - Configures Uvicorn to run `app.main:app` on `0.0.0.0:8000`.
   - Configures `Restart=always`, `After=network.target postgresql.service`, and `WantedBy=multi-user.target`.
   - Immediately notifies `execute[systemd_reload]` when the systemd unit changes.
   - Executes `systemctl daemon-reload` through `execute[systemd_reload]`, whose normal action is `nothing`.
   - Enables and starts the `fastapi-tutorial` service after the application files, dependencies, PostgreSQL service, database objects, environment file, and systemd unit are configured.
   - Iterations: None; the cookbook contains no `.each` loops or collection-based instance expansion.

## Dependencies

**External cookbook dependencies**: None listed in the supplied metadata; no `include_recipe` calls, custom resources, or providers are used.

**System package dependencies**:
- `python3`
- `python3-pip`
- `python3-venv`
- `git`
- `postgresql`
- `postgresql-contrib`
- `libpq-dev`

**Service dependencies**:
- `postgresql`
- `fastapi-tutorial`

**Application dependency source**:
- `/opt/fastapi-tutorial/requirements.txt`, obtained from the Git repository and installed into `/opt/fastapi-tutorial/venv`

## Credentials

**Detection Summary**: 1 database credential detected in 1 source recipe and materialized into the generated `.env` file.

**Source**:
- **Provider**: Hardcoded in the Chef recipe
- **URL**: None
- **Path**: None
- **Data bag or vault path**: None detected

### PostgreSQL `fastapi` User Password

- **Variable(s)**: `fastapi_password`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the `execute[create_db_user]` command
- **Generated file**: `/opt/fastapi-tutorial/.env`
- **Usage context**: PostgreSQL authentication for the FastAPI application
- **Database user**: `fastapi`
- **Database**: `fastapi_db`
- **Connection string**: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`

The password is present in both the PostgreSQL role creation command and the generated `DATABASE_URL`. The Ansible migration should store it in Ansible Vault while rendering the same effective database configuration.

No data bag, encrypted data bag, Chef Vault, Conjur, CyberArk, environment-variable secret lookup, TLS certificate, private key, API token, or external secret-manager endpoint was detected.

## Checks for the Migration

**Files to verify**:
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Directories to verify**:
- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/venv`

**Database objects to verify**:
- PostgreSQL role `fastapi`
- PostgreSQL database `fastapi_db`
- Owner of `fastapi_db`: `fastapi`
- All privileges on `fastapi_db` granted to `fastapi`

**Service endpoints to check**:
- `fastapi-tutorial`: TCP port `8000`, bound to `0.0.0.0`
- `postgresql`: local service, normally TCP port `5432` when TCP listening is enabled
- PostgreSQL local Unix socket: distribution-dependent and not explicitly configured

**Templates rendered**:
- None

**Inline files rendered**:
- `/opt/fastapi-tutorial/.env`: once
- `/etc/systemd/system/fastapi-tutorial.service`: once

## Pre-flight checks

```bash
# Verify all required packages
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

# Verify the fastapi-tutorial application directory
stat -c '%A %U:%G %n' /opt/fastapi-tutorial
# Expected: root:root ownership and mode 0755

# Verify the fastapi-tutorial repository and requirements
git -C /opt/fastapi-tutorial remote -v
git -C /opt/fastapi-tutorial branch --show-current
test -f /opt/fastapi-tutorial/requirements.txt

# Verify the fastapi-tutorial virtual environment
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip check

# Verify the postgresql instance
systemctl is-enabled postgresql
systemctl is-active postgresql
systemctl status postgresql --no-pager
sudo -u postgres psql -c "SELECT version();"

# Verify the fastapi PostgreSQL role
sudo -u postgres psql -tAc \
  "SELECT usename FROM pg_user WHERE usename = 'fastapi';"
# Expected: fastapi

# Verify the fastapi_db database and owner
sudo -u postgres psql -tAc \
  "SELECT datname FROM pg_database WHERE datname = 'fastapi_db';"
# Expected: fastapi_db

sudo -u postgres psql -tAc \
  "SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"
# Expected: fastapi

# Verify PostgreSQL connectivity for the fastapi application credentials
PGPASSWORD='fastapi_password' \
psql -h localhost -U fastapi -d fastapi_db -c "SELECT 1;"

# Verify database privileges
sudo -u postgres psql -c "\l+ fastapi_db"

# Verify the fastapi-tutorial environment file
stat -c '%A %U:%G %n' /opt/fastapi-tutorial/.env
# Expected: root:root ownership and mode 0644

grep '^PROJECT_NAME=' /opt/fastapi-tutorial/.env
grep '^API_VERSION=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=postgresql://fastapi:.*@localhost/fastapi_db$' \
  /opt/fastapi-tutorial/.env

# Verify the fastapi-tutorial systemd unit
stat -c '%A %U:%G %n' /etc/systemd/system/fastapi-tutorial.service
# Expected: root:root ownership and mode 0644

systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl daemon-reload
systemctl cat fastapi-tutorial
systemctl show fastapi-tutorial \
  --property=User,WorkingDirectory,ExecStart,Restart,After

# Verify the fastapi-tutorial service
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl status fastapi-tutorial --no-pager

# Verify the FastAPI process and endpoint
ps aux | grep '[u]vicorn app.main:app'
ss -tlnp | grep ':8000'
lsof -iTCP:8000 -sTCP:LISTEN
curl -i http://127.0.0.1:8000/
curl -sS -o /dev/null -w 'HTTP status: %{http_code}\n' \
  http://127.0.0.1:8000/

# Verify the fastapi-tutorial service can restart
sudo systemctl restart fastapi-tutorial
systemctl is-active fastapi-tutorial

# Review service logs and failed units
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u postgresql --no-pager -n 100
systemctl --failed

# Confirm final application database connectivity
PGPASSWORD='fastapi_password' \
psql -h localhost -U fastapi -d fastapi_db \
  -c "SELECT current_user, current_database();"

# Confirm FastAPI remains available
curl -sS -o /dev/null -w '%{http_code}\n' \
  http://127.0.0.1:8000/
```

The FastAPI root endpoint's exact HTTP status depends on the checked-out application code. The migration is successful when `fastapi-tutorial` is active, port `8000` is listening, PostgreSQL accepts the configured credentials, and the endpoint returns an HTTP response rather than a connection failure.