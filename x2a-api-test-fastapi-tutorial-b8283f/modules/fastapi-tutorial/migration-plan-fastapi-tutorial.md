---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the `fastapi-tutorial` FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` under `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, and PostgreSQL development packages; creates a Python virtual environment; installs application dependencies; provisions the `fastapi` PostgreSQL role and `fastapi_db` database; creates an environment file; and manages the application with a systemd service listening on `0.0.0.0:8000`.

## Service Type and Instances

**Service Type**: Application Server

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application managed by systemd
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Location/Path: `/opt/fastapi-tutorial`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Entry point: `app.main:app`
  - Runtime: `/opt/fastapi-tutorial/venv/bin/uvicorn`
  - Bind address: `0.0.0.0`
  - Port/Socket: `8000/TCP`
  - Working directory: `/opt/fastapi-tutorial`
  - Service user: `root`
  - Restart policy: `always`
  - Service dependency: `postgresql.service`
  - Database: `fastapi_db`
  - Database user: `fastapi`

- **postgresql**: Local PostgreSQL database service supporting the FastAPI application
  - Service name: `postgresql`
  - Port/Socket: `localhost:5432` and the distribution-default local Unix socket
  - Database: `fastapi_db`
  - Database owner: `fastapi`
  - Role: `fastapi`

## File Structure

**MANDATORY: Preserve this section from the original plan.**

```text
cookbooks/fastapi-tutorial/recipes/default.rb
```

**Recipes:**
```text
cookbooks/fastapi-tutorial/recipes/default.rb
```

**Providers:**
```text
```

No custom resources or provider files are used.

**Templates:**
```text
```

No ERB templates are rendered. The `.env` file and systemd unit are created using inline Chef `file` resources.

**Attributes:**
```text
```

No attribute files are shown or used.

**Files:**
```text
```

No static cookbook files are deployed using `cookbook_file` or `remote_file`.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the system packages `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev` with one `package` resource.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates the virtual environment with `execute[create_venv]`:
     ```bash
     python3 -m venv /opt/fastapi-tutorial/venv
     ```
     The command is guarded by the existing path `/opt/fastapi-tutorial/venv`.
   - Installs Python dependencies with `execute[install_dependencies]`:
     ```bash
     /opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt
     ```
     The working directory is `/opt/fastapi-tutorial`. This command runs on every Chef convergence.
   - Enables and starts `service[postgresql]`.
   - Executes `execute[create_db_user]` as the `postgres` operating-system user to create:
     - PostgreSQL role `fastapi` with password `fastapi_password`
     - Database `fastapi_db` owned by `fastapi`
     - All privileges on `fastapi_db` granted to `fastapi`
   - The PostgreSQL commands use `|| true`, allowing existing roles, databases, or grants without failing.
   - Creates `/opt/fastapi-tutorial/.env` with owner `root`, group `root`, and mode `0644`, containing:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Creates `/etc/systemd/system/fastapi-tutorial.service` with owner `root`, group `root`, and mode `0644`. The unit:
     - Runs as `root`
     - Uses `/opt/fastapi-tutorial` as its working directory
     - Sets `PATH` to `/opt/fastapi-tutorial/venv/bin`
     - Starts `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
     - Starts after `network.target` and `postgresql.service`
     - Uses `Restart=always`
     - Is enabled through `multi-user.target`
   - Defines `execute[systemd_reload]` with `action :nothing`, running:
     ```bash
     systemctl daemon-reload
     ```
     It runs immediately only when the systemd unit file changes.
   - Enables and starts `service[fastapi-tutorial]` after the unit file is deployed and systemd has been reloaded.
   - Iterations: None. The cookbook contains no collection attributes or `.each` loops.

## Dependencies

**External cookbook dependencies**: None shown in the supplied metadata or execution tree.

**System package dependencies**:
- `python3`
- `python3-pip`
- `python3-venv`
- `git`
- `postgresql`
- `postgresql-contrib`
- `libpq-dev`

**Service dependencies**:
- `network.target`
- `postgresql.service`

**Application dependencies**:
- Python packages listed in `/opt/fastapi-tutorial/requirements.txt`
- Python virtual environment at `/opt/fastapi-tutorial/venv`

## Credentials

**Detection Summary**: 1 database credential detected in 1 source file.

**Source**:
  - **Provider**: Hardcoded in Chef recipe
  - **URL**: None
  - **Path**: None

### PostgreSQL `fastapi` database password

- **Variable(s)**: No separate Chef variable; the literal password is `fastapi_password`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the `execute[create_db_user]` command and repeated in the inline `.env` file content
- **Usage context**:
  - PostgreSQL role creation:
    ```sql
    CREATE USER fastapi WITH PASSWORD 'fastapi_password';
    ```
  - Application connection string:
    ```text
    DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
    ```

The migration should store this value in Ansible Vault and use the vaulted value both when creating the PostgreSQL role and when rendering `/opt/fastapi-tutorial/.env`.

No Chef data bags, encrypted data bags, Chef Vault calls, CyberArk integration, Conjur variables, external secret-manager URLs, TLS certificates, API keys, or environment-variable lookups are shown.

## Checks for the Migration

**Files to verify**:
- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/venv/bin/python`
- `/opt/fastapi-tutorial/venv/bin/pip`
- `/opt/fastapi-tutorial/venv/bin/uvicorn`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Database objects to verify**:
- PostgreSQL role `fastapi`
- PostgreSQL database `fastapi_db`
- Database owner `fastapi`
- All privileges on `fastapi_db` granted to `fastapi`

**Service endpoints to check**:
- `fastapi-tutorial`: `0.0.0.0:8000`
- `postgresql`: `localhost:5432`
- PostgreSQL distribution-default local Unix socket

**Templates rendered**:
- No templates rendered: 0
- `/opt/fastapi-tutorial/.env`: inline Chef file content, rendered once
- `/etc/systemd/system/fastapi-tutorial.service`: inline Chef file content, rendered once

## Pre-flight checks:

```bash
# Verify required packages
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

# Verify the fastapi-tutorial instance layout
test -d /opt/fastapi-tutorial
test -d /opt/fastapi-tutorial/venv
test -f /opt/fastapi-tutorial/requirements.txt
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn

# Verify the fastapi-tutorial repository
git -C /opt/fastapi-tutorial remote -v
git -C /opt/fastapi-tutorial branch --show-current
git -C /opt/fastapi-tutorial rev-parse --verify HEAD

# Expected repository and revision
# Repository: https://github.com/dibanez/fastapi_tutorial.git
# Revision: main

# Verify Python dependencies
/opt/fastapi-tutorial/venv/bin/pip list
/opt/fastapi-tutorial/venv/bin/pip check

# Verify the postgresql instance
systemctl status postgresql --no-pager
systemctl is-enabled postgresql
systemctl is-active postgresql

# Expected postgresql state:
# enabled
# active

# Verify the PostgreSQL role
sudo -u postgres psql -tAc \
  "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"

# Verify the PostgreSQL database and owner
sudo -u postgres psql -tAc \
  "SELECT datname, pg_catalog.pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"

# Verify application database connectivity
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_database(), current_user;"

# Verify database privileges
sudo -u postgres psql -tAc \
  "SELECT has_database_privilege('fastapi', 'fastapi_db', 'CONNECT');"

# Verify the environment file without exposing its contents in logs
stat -c '%U:%G %a %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' \
  /opt/fastapi-tutorial/.env

# Verify the fastapi-tutorial systemd unit
systemctl cat fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl show fastapi-tutorial \
  --property=User,WorkingDirectory,ExecStart,Restart,After

# Verify the fastapi-tutorial process
systemctl status fastapi-tutorial --no-pager
ps aux | grep '[u]vicorn app.main:app'

# Verify the fastapi-tutorial TCP endpoint
ss -tlnp | grep ':8000'
curl -i http://127.0.0.1:8000/

# Review application logs
journalctl -u fastapi-tutorial --no-pager -n 100

# Verify systemd dependency and reload behavior
systemctl show fastapi-tutorial --property=After
systemctl daemon-reload
systemctl restart fastapi-tutorial
systemctl is-active fastapi-tutorial
```

Verify that:

- `postgresql` is enabled and active.
- The `fastapi` role and `fastapi_db` database exist.
- `fastapi_db` is owned by `fastapi`.
- The application can connect using the configured credentials.
- `/opt/fastapi-tutorial/.env` has mode `0644`, owner `root`, and group `root`.
- `fastapi-tutorial` is enabled and active.
- Uvicorn runs `app.main:app` from `/opt/fastapi-tutorial/venv/bin/uvicorn`.
- The application listens on `0.0.0.0:8000`.
- The root HTTP request returns an application response; a `404 Not Found` is acceptable if no root route is defined.
- Logs show successful Uvicorn startup without import errors, PostgreSQL connection failures, or repeated restart cycles.
- Changes to `/etc/systemd/system/fastapi-tutorial.service` trigger the systemd daemon-reload handler before the service is started or restarted.