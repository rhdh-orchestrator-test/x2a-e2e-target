---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys one FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main`. It installs Python, Git, PostgreSQL, and development dependencies; creates a Python virtual environment; installs dependencies from `requirements.txt`; initializes PostgreSQL where required; provisions the `fastapi` PostgreSQL user and `fastapi_db` database; writes an environment file containing the database connection string; and runs the application as a systemd service listening on `0.0.0.0:8000`. The cookbook supports Fedora/RHEL and Debian/Ubuntu package families.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application server
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Location/Path: `/opt/fastapi-tutorial`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Port/Socket: `0.0.0.0:8000`
  - Startup command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Runtime user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Restart policy: `Restart=always`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Environment file: `/opt/fastapi-tutorial/.env`

- **postgresql**: PostgreSQL database service
  - Service resource: `postgresql`
  - Service actions: enable and start
  - Database user: `fastapi`
  - Database password: `fastapi_password`
  - Database: `fastapi_db`
  - Database owner: `fastapi`
  - Connection host: `localhost`
  - Port/Socket: Default PostgreSQL local port and Unix socket
  - Connection URL: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
  - Fedora/RHEL initialization marker: `/var/lib/pgsql/data/PG_VERSION`

## File Structure

Only the recipe file shown in the execution tree is used by this cookbook.

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

The cookbook uses inline Chef `file` resources for the `.env` file and systemd unit rather than cookbook template or static file resources.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Selects the package list based on the platform family.
   - On Fedora/RHEL systems, installs:
     - `python3`
     - `python3-pip`
     - `git`
     - `postgresql-server`
     - `postgresql-contrib`
     - `libpq-devel`
   - On Debian/Ubuntu systems, installs:
     - `python3`
     - `python3-pip`
     - `python3-venv`
     - `git`
     - `postgresql`
     - `postgresql-contrib`
     - `libpq-dev`
   - On Fedora/RHEL systems, runs `postgresql-setup --initdb` only when `/var/lib/pgsql/data/PG_VERSION` does not exist.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Checks out `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates `/opt/fastapi-tutorial/venv` with `python3 -m venv` only when the directory does not exist.
   - Installs dependencies with `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt` from `/opt/fastapi-tutorial`.
   - Enables and starts the `postgresql` service.
   - Creates PostgreSQL role `fastapi` with password `fastapi_password`, database `fastapi_db` owned by `fastapi`, and grants all database privileges to `fastapi`. The original shell commands use `|| true`, making repeated execution non-failing.
   - Writes `/opt/fastapi-tutorial/.env` with owner `root`, group `root`, and mode `0644`, containing:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Writes `/etc/systemd/system/fastapi-tutorial.service` with owner `root`, group `root`, and mode `0644`, containing:
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
   - Defines `execute[systemd_reload]` with command `systemctl daemon-reload` and default action `nothing`. The service unit file is intended to notify this resource immediately when the unit changes.
   - Enables and starts the `fastapi-tutorial` service after the repository, virtual environment, Python dependencies, PostgreSQL service, database objects, `.env` file, systemd unit, and daemon reload are available.
   - Iterations: None. No `.each` loops are present.

## Dependencies

**External cookbook dependencies**: None

**System package dependencies**:

- Fedora/RHEL:
  - `python3`
  - `python3-pip`
  - `git`
  - `postgresql-server`
  - `postgresql-contrib`
  - `libpq-devel`
- Debian/Ubuntu:
  - `python3`
  - `python3-pip`
  - `python3-venv`
  - `git`
  - `postgresql`
  - `postgresql-contrib`
  - `libpq-dev`

**Application dependency source**: `/opt/fastapi-tutorial/requirements.txt`

**Service dependencies**:

- `postgresql`
- `fastapi-tutorial`
- `network.target`

The FastAPI systemd unit declares `After=network.target postgresql.service`.

## Credentials

**Detection Summary**: 1 credential detected in 1 recipe file.

**Source**:
  - **Provider**: Hardcoded in the Chef recipe
  - **URL**: Not applicable
  - **Path**: `cookbooks/fastapi-tutorial/recipes/default.rb`

### PostgreSQL application password

- **Variable(s)**:
  - Current hardcoded literal: `fastapi_password`
  - Intended migration variable: `fastapi_db_password`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the `execute[create_db_user]` command and repeated in the inline `.env` content
- **Usage context**:
  - Sets the password for PostgreSQL user `fastapi`
  - Appears in the connection string:
    ```text
    DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
    ```
  - Is used to authenticate to database `fastapi_db`

The migration should replace the hardcoded value with an AAP variable, Ansible Vault variable, or external secret lookup. The generated `.env` file should use restrictive permissions rather than the current Chef mode `0644`.

No data bags, encrypted data bags, Chef Vault calls, CyberArk integrations, Conjur calls, environment-variable secret lookups, TLS certificate references, API keys, or tokens were identified.

## Checks for the Migration

**Files to verify**:

- `cookbooks/fastapi-tutorial/recipes/default.rb`
- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- `/var/lib/pgsql/data/PG_VERSION` on Fedora/RHEL systems

**Database objects to verify**:

- PostgreSQL role `fastapi`
- PostgreSQL database `fastapi_db`
- Database owner `fastapi`
- All expected privileges granted to `fastapi`

**Service endpoints to check**:

- FastAPI: `http://127.0.0.1:8000`
- FastAPI listener: `0.0.0.0:8000`
- PostgreSQL: `localhost`
- PostgreSQL Unix socket: system-default local socket

**Templates rendered**:

- No cookbook templates rendered: `0`

**Inline files created**:

- `/opt/fastapi-tutorial/.env`: rendered once
- `/etc/systemd/system/fastapi-tutorial.service`: rendered once

## Pre-flight checks

```bash
# Verify both service instances
systemctl status postgresql
systemctl status fastapi-tutorial
systemctl is-enabled postgresql
systemctl is-enabled fastapi-tutorial

# Expected:
# - postgresql is enabled and active
# - fastapi-tutorial is enabled and active
```

```bash
# Verify the FastAPI application instance
test -d /opt/fastapi-tutorial
test -f /opt/fastapi-tutorial/requirements.txt
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
/opt/fastapi-tutorial/venv/bin/pip check
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/uvicorn --version

# Verify the application service unit
test -f /etc/systemd/system/fastapi-tutorial.service
systemctl cat fastapi-tutorial
systemctl show fastapi-tutorial \
  --property=User,WorkingDirectory,ExecStart,Restart,FragmentPath
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service

# Verify the FastAPI listener and endpoints
ss -tlnp | grep ':8000'
lsof -iTCP:8000 -sTCP:LISTEN
curl -i http://127.0.0.1:8000/
curl -i --max-time 10 http://127.0.0.1:8000/docs
```

Expected FastAPI settings:

```text
User=root
WorkingDirectory=/opt/fastapi-tutorial
ExecStart=/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
```

```bash
# Verify the PostgreSQL instance
sudo -u postgres psql -c "SELECT version();"
sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='fastapi';"
sudo -u postgres psql -tAc "SELECT datname FROM pg_database WHERE datname='fastapi_db';"

# Verify database ownership and privileges
sudo -u postgres psql -tAc \
  "SELECT datname, pg_get_userbyid(datdba) FROM pg_database WHERE datname='fastapi_db';"

sudo -u postgres psql -c "\l+ fastapi_db"

# Verify application login using the migrated secret
PGPASSWORD="${fastapi_db_password}" \
psql -h localhost -U fastapi -d fastapi_db \
  -c "SELECT current_user, current_database();"
```

Expected database login result:

```text
current_user | current_database
-------------+-----------------
fastapi      | fastapi_db
```

```bash
# Verify environment configuration
test -f /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' \
  /opt/fastapi-tutorial/.env

# Verify expected keys:
# PROJECT_NAME
# API_VERSION
# DATABASE_URL
```

```bash
# Verify service logs for both instances
journalctl -u postgresql --no-pager -n 50
journalctl -u fastapi-tutorial --no-pager -n 100
```

Check for successful PostgreSQL and Uvicorn startup, absence of authentication failures, absence of Python import or dependency errors, and absence of repeated restart loops.

```bash
# Fedora/RHEL PostgreSQL initialization check
test -f /var/lib/pgsql/data/PG_VERSION
```

On Debian/Ubuntu systems, validate the active PostgreSQL cluster through the service and connection checks instead of expecting the Fedora/RHEL marker path.