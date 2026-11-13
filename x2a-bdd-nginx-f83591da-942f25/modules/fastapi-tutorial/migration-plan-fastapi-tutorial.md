---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` under `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, and required system packages; creates a Python virtual environment; installs application requirements; initializes and starts PostgreSQL; creates the `fastapi` role and `fastapi_db` database; writes the application `.env` file; and runs the application through a systemd service named `fastapi-tutorial` on port `8000`. One hardcoded database credential is present.

## Service Type and Instances

**Service Type**: Application Server with PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application server
  - Location/Path: `/opt/fastapi-tutorial`
  - Source Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Repository Revision: `main`
  - Virtual Environment: `/opt/fastapi-tutorial/venv`
  - Application Entry Point: `app.main:app`
  - Process Command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Bind Address: `0.0.0.0`
  - Port: `8000`
  - Runtime User: `root`
  - Working Directory: `/opt/fastapi-tutorial`
  - Service Name: `fastapi-tutorial`
  - Restart Policy: `always`

- **postgresql**: PostgreSQL database service
  - Service Name: `postgresql`
  - Action: enabled and started
  - Host: `localhost`
  - Port: `5432`
  - Database: `fastapi_db`
  - Database Owner: `fastapi`
  - Database User: `fastapi`

## File Structure

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

The cookbook creates configuration files directly with Chef `file` resources. No static files or `.erb` templates are present.

## Module Explanation

The cookbook has one recipe, with no `include_recipe` calls or `.each` loops. Execution starts and completes in `cookbooks/fastapi-tutorial/recipes/default.rb`.

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Detects whether the platform is Fedora/RHEL or another platform family.
   - Installs platform-specific packages.

     Fedora/RHEL packages:
     - `python3`
     - `python3-pip`
     - `git`
     - `postgresql-server`
     - `postgresql-contrib`
     - `libpq-devel`

     Non-Fedora/RHEL packages:
     - `python3`
     - `python3-pip`
     - `python3-venv`
     - `git`
     - `postgresql`
     - `postgresql-contrib`
     - `libpq-dev`

   - On Fedora/RHEL, initializes PostgreSQL with `postgresql-setup --initdb`, using `/var/lib/pgsql/data/PG_VERSION` as the idempotence marker.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates `/opt/fastapi-tutorial/venv` with:
     ```bash
     python3 -m venv /opt/fastapi-tutorial/venv
     ```
   - Installs Python dependencies from `/opt/fastapi-tutorial/requirements.txt` using:
     ```bash
     /opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt
     ```
   - Enables and starts the `postgresql` service.
   - Creates PostgreSQL role `fastapi` with password `fastapi_password`.
   - Creates database `fastapi_db` owned by `fastapi`.
   - Grants all privileges on `fastapi_db` to `fastapi`.
   - Writes `/opt/fastapi-tutorial/.env` with owner `root`, group `root`, and mode `0644`:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Writes `/etc/systemd/system/fastapi-tutorial.service` with owner `root`, group `root`, and mode `0644`:
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
   - Immediately reloads systemd with `systemctl daemon-reload` when the unit file changes.
   - Enables and starts the `fastapi-tutorial` service after the repository, virtual environment, dependencies, environment file, PostgreSQL service, database objects, and systemd unit are ready.
   - The database creation commands tolerate existing objects with `|| true`; an Ansible migration should use PostgreSQL modules for semantic idempotence.

## Dependencies

**External cookbook dependencies**: None declared in the supplied `metadata.rb`.

**System package dependencies**:

- Fedora/RHEL:
  - `python3`
  - `python3-pip`
  - `git`
  - `postgresql-server`
  - `postgresql-contrib`
  - `libpq-devel`
- Non-Fedora/RHEL:
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

**Ordering dependencies**:

- Install PostgreSQL packages before initialization.
- Initialize PostgreSQL on Fedora/RHEL before starting its service.
- Start PostgreSQL before creating the `fastapi` role and `fastapi_db`.
- Synchronize the repository before creating the virtual environment or installing requirements.
- Create the virtual environment and install dependencies before starting `fastapi-tutorial`.
- Reload systemd after writing the unit file and before starting `fastapi-tutorial`.

## Credentials

**Detection Summary**: 1 logical database credential detected in 1 recipe file.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None
- **Path**: None
- **External secret reference**: None detected

### PostgreSQL `fastapi` database password

- **Variable(s)**: No variable; hardcoded password `fastapi_password`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the recipe and generated `/opt/fastapi-tutorial/.env`
- **Usage context**:
  - Creates PostgreSQL role `fastapi`
  - Authenticates the application through `DATABASE_URL`
  - Provides access to database `fastapi_db`

No data bag, Chef Vault, Conjur, CyberArk, Vault, environment-variable lookup, certificate, private key, API token, or external secret-manager reference was detected. Store the password in Ansible Vault during migration and use it for both the PostgreSQL user task and the `.env` file.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- Fedora/RHEL PostgreSQL data directory: `/var/lib/pgsql/data`
- Platform-managed PostgreSQL data directory on non-Fedora/RHEL systems

**Database objects to verify**:

- PostgreSQL role `fastapi`
- PostgreSQL database `fastapi_db`
- Owner of `fastapi_db`: `fastapi`
- All privileges on `fastapi_db` granted to `fastapi`

**Service endpoints to check**:

- `fastapi-tutorial`: HTTP on `0.0.0.0:8000`
- `postgresql`: TCP on `localhost:5432`
- PostgreSQL platform-default Unix socket

**Templates rendered**:

- No templates rendered; the cookbook contains no templates.
- `/opt/fastapi-tutorial/.env`: direct file content, written once.
- `/etc/systemd/system/fastapi-tutorial.service`: direct file content, written once.

## Pre-flight checks

```bash
# Verify required tools and application checkout
python3 --version
python3 -m pip --version
git --version
test -d /opt/fastapi-tutorial
git -C /opt/fastapi-tutorial rev-parse --is-inside-work-tree
git -C /opt/fastapi-tutorial branch --show-current
git -C /opt/fastapi-tutorial rev-parse HEAD
test -f /opt/fastapi-tutorial/requirements.txt
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip

# Verify the postgresql instance
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
ss -ltnp | grep ':5432'
pg_isready -h localhost -p 5432
sudo -u postgres psql -tAc "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"
sudo -u postgres psql -tAc "SELECT datname FROM pg_database WHERE datname = 'fastapi_db';"
sudo -u postgres psql -tAc \
  "SELECT datname, pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"
sudo -u postgres psql -c "\l+ fastapi_db"
PGPASSWORD='fastapi_password' \
  psql -h localhost -U fastapi -d fastapi_db -c "SELECT current_user, current_database();"

# Verify the fastapi-tutorial instance
test -f /opt/fastapi-tutorial/.env
grep '^PROJECT_NAME=' /opt/fastapi-tutorial/.env
grep '^API_VERSION=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env | sed 's/:fastapi_password@/:REDACTED@/'

test -f /etc/systemd/system/fastapi-tutorial.service
systemctl cat fastapi-tutorial.service
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl show fastapi-tutorial \
  -p LoadState -p ActiveState -p SubState -p UnitFileState \
  -p User -p WorkingDirectory -p ExecStart -p Restart

grep '^ExecStart=' /etc/systemd/system/fastapi-tutorial.service
grep -- '--host 0.0.0.0 --port 8000' \
  /etc/systemd/system/fastapi-tutorial.service
pgrep -af '/opt/fastapi-tutorial/venv/bin/uvicorn'
ss -ltnp | grep ':8000'
curl -i http://127.0.0.1:8000/
curl -i http://127.0.0.1:8000/docs
curl -i http://127.0.0.1:8000/openapi.json

# Verify application database connectivity
cd /opt/fastapi-tutorial
PGPASSWORD='fastapi_password' \
  psql -h localhost -U fastapi -d fastapi_db -c "SELECT 1;"

# Review service logs and restart policy
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u postgresql --no-pager -n 100
systemctl show fastapi-tutorial -p Restart
```

Expected results:

- `postgresql` is enabled, active, and accepting connections on port `5432`.
- Role `fastapi` and database `fastapi_db` exist, with `fastapi` as the database owner.
- `/opt/fastapi-tutorial/venv/bin/uvicorn` is running for instance `fastapi-tutorial`.
- `fastapi-tutorial` is enabled, active, and listening on port `8000`.
- The service uses `/opt/fastapi-tutorial` as its working directory, runs as `root`, and has `Restart=always`.
- FastAPI endpoints return HTTP responses.
- The application can connect to `fastapi_db`.
- No recent import, dependency, database, or permission errors appear in the logs.