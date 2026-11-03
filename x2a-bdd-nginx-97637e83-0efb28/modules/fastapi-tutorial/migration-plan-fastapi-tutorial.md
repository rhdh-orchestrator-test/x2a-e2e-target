---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys one FastAPI application, `fastapi-tutorial`, from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main`. It installs Python, Git, PostgreSQL, and PostgreSQL development packages; creates `/opt/fastapi-tutorial` and its Python virtual environment; installs application dependencies; creates the PostgreSQL user and database; writes the application environment file; and manages a systemd service listening on TCP port `8000`.

## Service Type and Instances

**Service Type**: Application Server

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application server
  - Location/Path: `/opt/fastapi-tutorial`
  - Source repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Repository revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Application command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Bind address: `0.0.0.0`
  - Port/Socket: TCP `8000`
  - Working directory: `/opt/fastapi-tutorial`
  - Service user: `root`
  - Restart behavior: `Restart=always`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Database: PostgreSQL database `fastapi_db`
  - Database user: `fastapi`
  - Database host: `localhost`
  - Database port: PostgreSQL default/local connection; no explicit TCP port is configured

There are no collection attributes or `.each` loops in the cookbook. No additional instance expansion is required.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**
```text
recipes/default.rb
```

**Providers:**
```text
```

**Templates:**
```text
```

**Attributes:**
```text
```

**Files:**
```text
```

No provider, template, attribute, or static file is used. The `.env` file and systemd unit are generated inline by Chef `file` resources.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the seven system packages: `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - No package versions are pinned. Ubuntu supports `libpq-dev`; CentOS-family systems may require the package name `postgresql-devel`.
   - Cookbook metadata supports Ubuntu `>= 18.04` and CentOS `>= 7.0`.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Expects the repository to provide `/opt/fastapi-tutorial/requirements.txt`, the Python module `app.main`, and the FastAPI object `app`.
   - Runs `python3 -m venv /opt/fastapi-tutorial/venv` with a creation guard for `/opt/fastapi-tutorial/venv`.
   - Installs dependencies with `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt` from working directory `/opt/fastapi-tutorial`.
   - Enables and starts the `postgresql` service.
   - Creates PostgreSQL user `fastapi` with password `fastapi_password`, database `fastapi_db`, and owner `fastapi`.
   - Grants all privileges on `fastapi_db` to `fastapi`.
   - The original Chef implementation executes PostgreSQL commands through `sudo -u postgres psql` and appends `|| true`; the Ansible migration should replace this with idempotent `community.postgresql.postgresql_user`, `community.postgresql.postgresql_db`, and `community.postgresql.postgresql_privs` tasks.
   - Creates `/opt/fastapi-tutorial/.env` with:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Creates the `.env` file with owner `root`, group `root`, and mode `0644`. Because it contains a password, the Ansible implementation should preferably use mode `0600` unless compatibility requires `0644`.
   - Creates `/etc/systemd/system/fastapi-tutorial.service` with owner `root`, group `root`, and mode `0644`:
     ```ini
     [Unit]
     Description=FastAPI Tutorial Service
     After=network.target postgresql.service

     [Service]
     Type=simple
     User=root
     WorkingDirectory=/opt/fastapi-tutorial
     Environment="PATH=/opt/fastapi-tutorial/venv/bin"
     ExecStart=/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
     Restart=always

     [Install]
     WantedBy=multi-user.target
     ```
   - Defines `execute[systemd_reload]` with command `systemctl daemon-reload` and `action: nothing`.
   - Notifies `execute[systemd_reload]` immediately when `/etc/systemd/system/fastapi-tutorial.service` changes.
   - Enables and starts the `fastapi-tutorial` service after the application files, virtual environment, dependencies, PostgreSQL database, `.env` file, and systemd unit are ready.
   - Iterations: None. No `.each` loops or collection-based resources are present.

## Dependencies

**External cookbook dependencies**: None declared in `metadata.rb`.

**External source dependencies**:

- Git repository: `https://github.com/dibanez/fastapi_tutorial.git`
- Git revision: `main`

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

**Application dependency file**:

- `/opt/fastapi-tutorial/requirements.txt`

The contents of `requirements.txt` are supplied by the Git repository and are not defined in the cookbook.

## Credentials

**Detection Summary**: 1 hardcoded database credential detected, referenced in 2 locations within `cookbooks/fastapi-tutorial/recipes/default.rb`.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None
- **Path**: None
- **Data bag, vault, or secret manager**: None detected

### PostgreSQL Password

- **Variable(s)**:
  - Password literal: `fastapi_password`
  - Connection variable: `DATABASE_URL`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the recipe and repeated in the generated `/opt/fastapi-tutorial/.env` file
- **Usage context**:
  - PostgreSQL user creation:
    ```sql
    CREATE USER fastapi WITH PASSWORD 'fastapi_password';
    ```
  - Application database connection:
    ```dotenv
    DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
    ```

No data bag, encrypted data bag, Chef Vault, Conjur, CyberArk, Vault attribute, environment-variable secret lookup, TLS certificate, API key, or token references were detected. The Ansible migration should store this password in Ansible Vault.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Database objects to verify**:

- PostgreSQL user `fastapi`
- PostgreSQL database `fastapi_db`
- Owner of `fastapi_db`: `fastapi`
- All privileges on `fastapi_db` granted to `fastapi`

**Service endpoints to check**:

- **fastapi-tutorial**: HTTP endpoint at `http://127.0.0.1:8000/`
- **PostgreSQL**: Local PostgreSQL connection; no explicit TCP port is configured

**Templates rendered**:

- None; no `.erb` templates are used
- Inline files rendered: `/opt/fastapi-tutorial/.env` once and `/etc/systemd/system/fastapi-tutorial.service` once

**Services to verify**:

- `postgresql`: enabled and active
- `fastapi-tutorial`: enabled and active
- systemd daemon reloaded after the FastAPI unit is created or changed

## Pre-flight checks:

```bash
# Verify installed packages on Debian/Ubuntu systems
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

# Verify the fastapi-tutorial instance directory
stat -c '%A %U:%G %n' /opt/fastapi-tutorial
git -C /opt/fastapi-tutorial status --short
git -C /opt/fastapi-tutorial branch --show-current
test -f /opt/fastapi-tutorial/requirements.txt

# Verify the fastapi-tutorial virtual environment
test -x /opt/fastapi-tutorial/venv/bin/python
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip --version
/opt/fastapi-tutorial/venv/bin/pip check

# Verify PostgreSQL for the fastapi-tutorial instance
systemctl status postgresql --no-pager
systemctl is-enabled postgresql
systemctl is-active postgresql
sudo -u postgres pg_isready
sudo -u postgres psql -tAc "SELECT usename FROM pg_user WHERE usename = 'fastapi';"
sudo -u postgres psql -tAc "SELECT datname, pg_catalog.pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"
sudo -u postgres psql -c "\l+ fastapi_db"

# Verify PostgreSQL credentials and connectivity
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_user, current_database();"

# Expected values:
# current_user: fastapi
# current_database: fastapi_db

# Verify the fastapi-tutorial environment file without exposing the password
stat -c '%A %U:%G %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION)=' /opt/fastapi-tutorial/.env
grep -E '^DATABASE_URL=postgresql://fastapi:' /opt/fastapi-tutorial/.env

# Verify the fastapi-tutorial systemd unit
systemctl cat fastapi-tutorial
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
grep -F 'ExecStart=/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000' \
  /etc/systemd/system/fastapi-tutorial.service

# Reload and verify systemd state
systemctl daemon-reload
systemctl show fastapi-tutorial --property=LoadState,ActiveState,UnitFileState

# Verify the fastapi-tutorial service
systemctl status fastapi-tutorial --no-pager
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
ps aux | grep '[u]vicorn app.main:app'

# Verify the fastapi-tutorial endpoint
ss -tlnp | grep ':8000'
lsof -iTCP:8000 -sTCP:LISTEN
curl -i http://127.0.0.1:8000/

# Verify restart behavior and logs for fastapi-tutorial
systemctl restart fastapi-tutorial
systemctl is-active fastapi-tutorial
journalctl -u fastapi-tutorial --no-pager -n 100

# Verify application database configuration and service context
grep -E '^DATABASE_URL=postgresql://fastapi:.*@localhost/fastapi_db$' \
  /opt/fastapi-tutorial/.env
systemctl show fastapi-tutorial \
  --property=User,WorkingDirectory,Environment,ExecStart
```

