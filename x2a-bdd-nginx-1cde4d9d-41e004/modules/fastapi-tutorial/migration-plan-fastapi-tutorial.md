---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI Tutorial application from the `main` branch of `https://github.com/dibanez/fastapi_tutorial.git` to `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, and PostgreSQL development packages; creates a Python virtual environment; installs application dependencies; creates the `fastapi` PostgreSQL role and `fastapi_db` database; writes a database connection string to `.env`; and manages the `fastapi-tutorial` systemd service on TCP port `8000`.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application server
  - Location/Path: `/opt/fastapi-tutorial`
  - Source repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Git revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Application command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Port/Socket: TCP `8000`
  - systemd unit: `fastapi-tutorial.service`
  - Runtime user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Restart policy: `always`
  - Startup ordering: after `network.target` and `postgresql.service`

- **postgresql**: PostgreSQL database service
  - Database user: `fastapi`
  - Database name: `fastapi_db`
  - Database host: `localhost`
  - Port/Socket: TCP `5432` by default; local socket path is determined by the PostgreSQL installation
  - Database connection URL: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
  - Database owner: `fastapi`
  - Database privileges: all privileges on `fastapi_db` granted to `fastapi`

There are no collection attributes or `.each` iterations in the execution tree.

## File Structure

Only the recipe file is executed by this cookbook. The environment file and systemd unit are created inline by Chef `file` resources; they are not cookbook template files.

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

No `.erb` templates are rendered.

**Attributes:**
```text
```

No attribute files are used.

**Files:**
```text
```

No static files from `files/default/` or `files/` are deployed.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev` in one package resource.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates the Python virtual environment with `python3 -m venv /opt/fastapi-tutorial/venv`, guarded by the existence of `/opt/fastapi-tutorial/venv`.
   - Installs dependencies from `/opt/fastapi-tutorial/requirements.txt` using `/opt/fastapi-tutorial/venv/bin/pip` with `/opt/fastapi-tutorial` as the working directory.
   - Enables and starts the `postgresql` service.
   - Creates the PostgreSQL role `fastapi` with password `fastapi_password`.
   - Creates the PostgreSQL database `fastapi_db` owned by `fastapi`.
   - Grants all privileges on `fastapi_db` to `fastapi`.
   - Writes `/opt/fastapi-tutorial/.env` with owner `root`, group `root`, and mode `0644`, containing:
     - `PROJECT_NAME="FastAPI Tutorial"`
     - `API_VERSION=1.0.0`
     - `DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db`
   - Writes `/etc/systemd/system/fastapi-tutorial.service` with the FastAPI service definition.
   - Reloads systemd when `/etc/systemd/system/fastapi-tutorial.service` changes.
   - Enables and starts the `fastapi-tutorial` service.
   - Resources used: 1 `package`, 1 `directory`, 1 `git`, 4 `execute` resources (`create_venv`, `install_dependencies`, `create_db_user`, and `systemd_reload`), 2 `service` resources (`postgresql` and `fastapi-tutorial`), and 2 `file` resources.
   - Iterations: None.

   The systemd unit contains:
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

   The original PostgreSQL commands suppress existing-object and command errors with `|| true`. A semantic migration should use PostgreSQL-specific Ansible modules where available, or use `ansible.builtin.shell` with `become_user: postgres` when exact shell behavior is required. The package `libpq-dev` is Debian-family naming and may require a platform-specific equivalent on CentOS.

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

**Service dependencies**:
- `postgresql`
- `fastapi-tutorial`
- `fastapi-tutorial.service` starts after `network.target` and `postgresql.service`

## Credentials

**Detection Summary**: 2 credential references detected in `cookbooks/fastapi-tutorial/recipes/default.rb`. Both references contain the same hardcoded PostgreSQL password.

**Source**:
  - **Provider**: Hardcoded in the Chef recipe
  - **URL**: None
  - **Path**: None

### PostgreSQL application password

- **Variable(s)**:
  - No Chef attribute variable is used.
  - Literal password: `fastapi_password`
  - Database URL: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the recipe and written to `/opt/fastapi-tutorial/.env`
- **Usage context**: PostgreSQL role creation and FastAPI database authentication
- **Occurrences**:
  - `CREATE USER fastapi WITH PASSWORD 'fastapi_password'`
  - `DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Migration guidance**: Store the password in Ansible Vault or an AAP credential. If the `.env` file retains the credential, use mode `0600` unless application requirements require otherwise.

No data bag, Chef Vault, CyberArk, Conjur, environment-variable secret lookup, TLS certificate, private key, API token, or external secret-manager reference was detected.

## Checks for the Migration

**Files to verify**:
- `cookbooks/fastapi-tutorial/recipes/default.rb`
- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Database objects to verify**:
- PostgreSQL role `fastapi`
- PostgreSQL database `fastapi_db`
- Database owner `fastapi`
- All privileges granted to `fastapi` on `fastapi_db`

**Service endpoints to check**:
- `fastapi-tutorial`: TCP `8000`
- `postgresql`: TCP `5432` by default
- PostgreSQL local socket: installation-defined

**Templates rendered**:
- None; both `.env` and the systemd unit are created by inline Chef `file` resources.
- Render count: `0`

## Pre-flight checks:

```bash
# Package checks
if command -v dpkg >/dev/null 2>&1; then
  dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev
else
  rpm -q python3 python3-pip python3-venv git postgresql postgresql-contrib
fi

# Application instance: fastapi-tutorial
ls -ld /opt/fastapi-tutorial
ls -ld /opt/fastapi-tutorial/venv
ls -l /opt/fastapi-tutorial/requirements.txt
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn
/opt/fastapi-tutorial/venv/bin/pip list

# PostgreSQL instance: postgresql
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql

# PostgreSQL role and database
sudo -u postgres psql -tAc "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"
sudo -u postgres psql -tAc "SELECT datname FROM pg_database WHERE datname = 'fastapi_db';"
sudo -u postgres psql -tAc "SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"

# PostgreSQL connectivity for fastapi_db
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT version();"

PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_database(), current_user;"

# Environment file
grep '^PROJECT_NAME=' /opt/fastapi-tutorial/.env
grep '^API_VERSION=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env
stat -c '%U:%G %a %n' /opt/fastapi-tutorial/.env

# Expected original environment values:
# PROJECT_NAME="FastAPI Tutorial"
# API_VERSION=1.0.0
# DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
# root:root 644 /opt/fastapi-tutorial/.env

# FastAPI instance: fastapi-tutorial
systemctl daemon-reload
systemctl cat fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl show fastapi-tutorial \
  --property=ActiveState,SubState,ExecMainStartTimestamp

# FastAPI process and endpoint
systemctl status fastapi-tutorial
ps aux | grep '[u]vicorn'
curl -I http://127.0.0.1:8000/
curl -sS http://127.0.0.1:8000/

# Network checks for fastapi-tutorial
ss -tlnp | grep ':8000'
netstat -tulpn 2>/dev/null | grep ':8000'

# Network checks for postgresql
ss -tlnp | grep ':5432'

# Logs and failure checks for both instances
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u postgresql --no-pager -n 100
systemctl --failed
```

Expected results:

- The `postgresql` service is active and enabled.
- The `fastapi` PostgreSQL role exists.
- The `fastapi_db` database exists and is owned by `fastapi`.
- The application virtual environment and `uvicorn` executable exist.
- The `fastapi-tutorial` service is active and enabled.
- Uvicorn listens on `0.0.0.0:8000` or an equivalent wildcard IPv4 address.
- PostgreSQL listens on its configured port, normally `5432`.
- The FastAPI endpoint accepts connections and returns an HTTP response.
- Logs contain no application import errors, missing dependencies, PostgreSQL authentication failures, database connection failures, port conflicts, or systemd execution errors.
