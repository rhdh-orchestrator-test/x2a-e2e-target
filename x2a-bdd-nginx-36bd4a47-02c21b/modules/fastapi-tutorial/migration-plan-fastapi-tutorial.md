---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI Tutorial application from the `main` branch of `https://github.com/dibanez/fastapi_tutorial.git`. It installs Python, Git, PostgreSQL, and PostgreSQL development packages; creates a Python virtual environment; installs application requirements; creates the PostgreSQL role and database; writes an environment file; and manages a systemd service running Uvicorn on `0.0.0.0:8000`. The configured application instance is `fastapi-tutorial`, and the configured PostgreSQL database is `fastapi_db`. The database password must be migrated to Ansible Vault or an approved secret-management system.

## Service Type and Instances

**Service Type**: Application Server with PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application served by Uvicorn
  - Location/Path: `/opt/fastapi-tutorial`
  - Source repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Repository revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Port/Socket: `0.0.0.0:8000`
  - Application command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Working directory: `/opt/fastapi-tutorial`
  - Service user: `root`
  - Restart policy: `Restart=always`
  - systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Unit ordering: `After=network.target postgresql.service`

- **fastapi_db**: PostgreSQL database used by the FastAPI application
  - Location/Path: Local PostgreSQL instance
  - Port/Socket: `localhost`; no explicit Unix socket path configured
  - Database user: `fastapi`
  - Database owner: `fastapi`
  - Connection URL: `postgresql://fastapi:<secret>@localhost/fastapi_db`
  - Password storage: Ansible Vault or an approved secret-management system

## File Structure

The execution tree contains one recipe file and no separate providers, templates, attribute files, or static files.

```text
cookbooks/fastapi-tutorial/
└── recipes/
    └── default.rb
```

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

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the operating-system packages `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates the virtual environment with `python3 -m venv /opt/fastapi-tutorial/venv` only when `/opt/fastapi-tutorial/venv` does not exist.
   - Installs `/opt/fastapi-tutorial/requirements.txt` into `/opt/fastapi-tutorial/venv` using the virtual environment's `pip`.
   - Enables and starts the `postgresql` service.
   - Creates the PostgreSQL role `fastapi`, database `fastapi_db`, and grants all privileges on `fastapi_db` to `fastapi`.
   - Creates `/opt/fastapi-tutorial/.env` with owner `root`, group `root`, and mode `0644`.
   - Writes the following non-secret configuration to `.env`:
     - `PROJECT_NAME="FastAPI Tutorial"`
     - `API_VERSION=1.0.0`
     - `DATABASE_URL=postgresql://fastapi:<secret>@localhost/fastapi_db`
   - Deploys `/etc/systemd/system/fastapi-tutorial.service` with owner `root`, group `root`, and mode `0644`.
   - Configures the systemd unit to run as `root`, use `/opt/fastapi-tutorial` as its working directory, set `PATH=/opt/fastapi-tutorial/venv/bin`, and execute Uvicorn on `0.0.0.0:8000`.
   - Configures `Restart=always`, `After=network.target postgresql.service`, and `WantedBy=multi-user.target`.
   - Reloads systemd immediately when the service unit changes.
   - Enables and starts the `fastapi-tutorial` service.
   - Iterations: None; no collection attributes or `.each` loops are present.

## Dependencies

**External cookbook dependencies**: None declared in `metadata.rb`.

**System package dependencies**:

- `python3`
- `python3-pip`
- `python3-venv`
- `git`
- `postgresql`
- `postgresql-contrib`
- `libpq-dev`

**Application dependency source**: `/opt/fastapi-tutorial/requirements.txt`

**Application dependency destination**: `/opt/fastapi-tutorial/venv`

**Service dependencies**:

- `postgresql`
- `fastapi-tutorial`

The `fastapi-tutorial.service` unit declares:

```ini
After=network.target postgresql.service
```

## Credentials

**Detection Summary**: 1 credential detected across 1 file. The credential is used for PostgreSQL role creation and the application database connection URL.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None
- **Path**: None
- **Recommended storage**: Ansible Vault or an approved external secret-management integration

### PostgreSQL application password

- **Variable**: `fastapi_password`
- **Source file**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded plaintext
- **Current literal**: `fastapi_password`
- **Usage context**: PostgreSQL role creation:
  ```sql
  CREATE USER fastapi WITH PASSWORD 'fastapi_password';
  ```
- **Usage context**: Application connection URL in `/opt/fastapi-tutorial/.env`:
  ```text
  DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
  ```
- **Migration requirement**: Store the password in Ansible Vault and interpolate it into both the PostgreSQL user task and the generated `.env` file.
- **Security consideration**: The original `.env` mode is `0644`, making the password-bearing connection string readable by non-root users. Use mode `0600` if application behavior permits.

No Chef data bags, encrypted data bags, Chef Vault calls, CyberArk integration, Conjur variables, TLS certificates, API keys, or environment-variable-based secret lookups were detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/fastapi-tutorial/recipes/default.rb`
- `/opt/fastapi-tutorial/`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv/`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Database objects to verify**:

- PostgreSQL role: `fastapi`
- PostgreSQL database: `fastapi_db`
- Database owner: `fastapi`
- Privileges granted to `fastapi`

**Service endpoints to check**:

- `fastapi-tutorial`: TCP listener `0.0.0.0:8000`
- `fastapi_db`: PostgreSQL through `localhost`

**Unix sockets**: No explicit Unix socket path is configured.

**Templates rendered**:

- No `.erb` templates are used.
- `/opt/fastapi-tutorial/.env`: inline file content, one render when content changes.
- `/etc/systemd/system/fastapi-tutorial.service`: inline file content, one render when content changes.

## Pre-flight checks

```bash
# Verify required packages
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev 2>/dev/null || \
rpm -q python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

# Verify the fastapi-tutorial application instance
test -d /opt/fastapi-tutorial
test -f /opt/fastapi-tutorial/requirements.txt
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -f /opt/fastapi-tutorial/.env

# Verify the fastapi_db PostgreSQL instance
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql

sudo -u postgres psql -tAc "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"
sudo -u postgres psql -tAc "SELECT datname FROM pg_database WHERE datname = 'fastapi_db';"
sudo -u postgres psql -tAc "SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"

# Verify expected PostgreSQL results:
# fastapi
# fastapi_db
# fastapi

# Verify application database connectivity without exposing the password
PGPASSWORD='<retrieve-from-approved-secret-store>' \
psql -h localhost -U fastapi -d fastapi_db -c "SELECT version();"

PGPASSWORD='<retrieve-from-approved-secret-store>' \
psql -h localhost -U fastapi -d fastapi_db -c "SELECT current_database(), current_user;"

# Verify environment file metadata and non-secret values
stat -c '%U:%G %a %n' /opt/fastapi-tutorial/.env
grep '^PROJECT_NAME=' /opt/fastapi-tutorial/.env
grep '^API_VERSION=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env

# Verify the fastapi-tutorial systemd instance
systemctl daemon-reload
systemctl cat fastapi-tutorial
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial

# Verify the systemd unit contains:
# WorkingDirectory=/opt/fastapi-tutorial
# Environment="PATH=/opt/fastapi-tutorial/venv/bin"
# ExecStart=/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
# Restart=always
# After=network.target postgresql.service

# Verify the FastAPI endpoint
curl -i http://127.0.0.1:8000/

# Verify the FastAPI process and port
systemctl status fastapi-tutorial
ps -ef | grep '[u]vicorn app.main:app'
ss -ltnp | grep ':8000'

# Review logs for both named service instances
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u postgresql --no-pager -n 100

# Verify service ordering and successful startup
systemctl show fastapi-tutorial --property=After
systemctl show fastapi-tutorial --property=ExecMainStatus
```

Expected results:

- `postgresql` is enabled and active.
- PostgreSQL contains role `fastapi`.
- PostgreSQL contains database `fastapi_db`, owned by `fastapi`.
- The `fastapi` role can connect to `fastapi_db`.
- `fastapi-tutorial.service` is enabled and active.
- Uvicorn listens on TCP port `8000`.
- The FastAPI endpoint returns an HTTP response.
- `ExecMainStatus=0`.
- Logs contain no Uvicorn startup errors, import errors, missing dependency errors, PostgreSQL authentication failures, database connection failures, or repeated service restarts.
