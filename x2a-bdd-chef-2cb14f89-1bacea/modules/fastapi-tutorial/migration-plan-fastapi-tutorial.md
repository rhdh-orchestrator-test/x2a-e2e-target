---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, and PostgreSQL development dependencies; creates a Python virtual environment; installs application requirements; creates the PostgreSQL user and database; writes an environment file; and manages the application with the `fastapi-tutorial` systemd service. The FastAPI/Uvicorn service listens on port `8000` and depends on the locally managed PostgreSQL service.

## Service Type and Instances

**Service Type**: Application Server with PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application managed by systemd
  - Location/Path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Git revision: `main`
  - Python virtual environment: `/opt/fastapi-tutorial/venv`
  - Port/Socket: `0.0.0.0:8000`
  - Startup command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Service user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Restart policy: `Restart=always`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Key configuration: Starts after `network.target` and `postgresql.service`; uses `/opt/fastapi-tutorial/venv/bin` in `PATH`; is enabled at boot.

- **postgresql**: Local PostgreSQL database service
  - Location/Path: Platform-managed PostgreSQL data directory
    - RHEL/Fedora: `/var/lib/pgsql/data/`
    - Non-RHEL/Fedora: Distribution-managed PostgreSQL data directory
  - Port/Socket: `localhost:5432` and the platform-managed local Unix socket
  - Database user: `fastapi`
  - Database password: `fastapi_password`
  - Database name: `fastapi_db`
  - Database owner: `fastapi`
  - Connection string: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
  - Key configuration: Enabled at boot and started immediately.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

```text
cookbooks/fastapi-tutorial/
├── attributes/
│   └── default.rb
└── recipes/
    └── default.rb
```

**Recipes:**
```text
cookbooks/fastapi-tutorial/recipes/default.rb
```

**Providers:**
```text
```

**Templates:**
```text
```

**Attributes:**
```text
cookbooks/fastapi-tutorial/attributes/default.rb
```

**Files:**
```text
```

## Module Explanation

The cookbook performs operations in this order. There are no `.each` loops, collection attributes, custom resources, providers, templates, or static files.

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs platform-specific system packages.
   - On Fedora/RHEL, installs `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, and `libpq-devel`.
   - On non-Fedora/RHEL platforms, installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev` — seven packages.
   - On Fedora/RHEL, runs `postgresql-setup --initdb` through `execute[initialize_postgresql]` only when `/var/lib/pgsql/data/PG_VERSION` does not exist.
   - Creates `/opt/fastapi-tutorial` as `root:root` with mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates `/opt/fastapi-tutorial/venv` with:
     ```bash
     python3 -m venv /opt/fastapi-tutorial/venv
     ```
     The command runs only when the virtual environment does not already exist.
   - Installs Python dependencies from `/opt/fastapi-tutorial/requirements.txt` using:
     ```bash
     /opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt
     ```
   - Enables and starts the `postgresql` service.
   - Creates PostgreSQL user `fastapi` with password `fastapi_password`.
   - Creates database `fastapi_db` owned by `fastapi`.
   - Grants all privileges on `fastapi_db` to `fastapi`.
   - The original Chef commands tolerate existing database objects with `|| true`; the Ansible migration should prefer `community.postgresql.postgresql_user`, `community.postgresql.postgresql_db`, and, if needed, `community.postgresql.postgresql_privs` for declarative idempotency.
   - Writes `/opt/fastapi-tutorial/.env` as `root:root` with mode `0644`:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Writes `/etc/systemd/system/fastapi-tutorial.service` as `root:root` with mode `0644`:
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
   - Notifies `execute[systemd_reload]` immediately when the systemd unit changes.
   - Runs `systemctl daemon-reload` through `execute[systemd_reload]`; this resource has action `nothing` and runs only when notified.
   - Enables and starts the `fastapi-tutorial` service after the unit has been created and systemd has been reloaded.

## Dependencies

**External cookbook dependencies**: None identified.

**System package dependencies**:

- **Fedora/RHEL**:
  - `python3`
  - `python3-pip`
  - `git`
  - `postgresql-server`
  - `postgresql-contrib`
  - `libpq-devel`
- **Non-Fedora/RHEL**:
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

The FastAPI unit declares `After=network.target postgresql.service`.

## Credentials

**Detection Summary**: 1 hardcoded database credential detected in 2 recipe locations.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: Not applicable
- **Path**: Not applicable
- **Storage locations**: PostgreSQL creation command and `/opt/fastapi-tutorial/.env`

### PostgreSQL `fastapi` database password

- **Variable(s)**: No Chef attribute variable; literal value is `fastapi_password`.
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb:49`
  - `cookbooks/fastapi-tutorial/recipes/default.rb:61`
- **Current storage**: Hardcoded in the recipe and written in plaintext to `/opt/fastapi-tutorial/.env`.
- **Usage context**:
  - Sets the password for PostgreSQL user `fastapi`.
  - Appears in the `DATABASE_URL` value for database `fastapi_db`.
- **Migration guidance**: Store the password in Ansible Vault or an AAP credential, use the vaulted value for the PostgreSQL user task, and render it into `.env`. Consider mode `0600` for `.env` instead of the cookbook’s `0644`, subject to application requirements.

No Chef data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, AWS Secrets Manager, environment-variable secret references, TLS certificate paths, API keys, or tokens were detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/fastapi-tutorial/recipes/default.rb`
- `cookbooks/fastapi-tutorial/attributes/default.rb`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/.env`
- `/opt/fastapi-tutorial/venv/`
- `/opt/fastapi-tutorial/app/main.py`
- `/etc/systemd/system/fastapi-tutorial.service`
- RHEL/Fedora PostgreSQL data directory: `/var/lib/pgsql/data/`
- Non-RHEL/Fedora PostgreSQL distribution-managed data directory

**Service endpoints to check**:

- FastAPI/Uvicorn: `0.0.0.0:8000`
- PostgreSQL: `localhost:5432`
- PostgreSQL platform-managed local Unix socket

**Templates rendered**: None. The cookbook uses inline `file` resources.

**Rendered or deployed inline files**:

- `/opt/fastapi-tutorial/.env`: written once
- `/etc/systemd/system/fastapi-tutorial.service`: written once

## Pre-flight checks

```bash
# Verify the postgresql instance individually
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql

# Verify the fastapi-tutorial instance individually
systemctl status fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial

# Verify the PostgreSQL user
sudo -u postgres psql -tAc \
  "SELECT usename FROM pg_user WHERE usename = 'fastapi';"

# Verify the PostgreSQL database
sudo -u postgres psql -tAc \
  "SELECT datname FROM pg_database WHERE datname = 'fastapi_db';"

# Verify the database owner
sudo -u postgres psql -tAc \
  "SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"

# Verify PostgreSQL connectivity using the configured credentials
PGPASSWORD='fastapi_password' \
psql -h localhost -U fastapi -d fastapi_db -c "SELECT version();"

PGPASSWORD='fastapi_password' \
psql -h localhost -U fastapi -d fastapi_db \
  -c "SELECT current_user, current_database();"

# Verify the application directory, requirements, and virtual environment
test -d /opt/fastapi-tutorial
test -f /opt/fastapi-tutorial/requirements.txt
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn

/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip list

# Verify the FastAPI application import
cd /opt/fastapi-tutorial
/opt/fastapi-tutorial/venv/bin/python \
  -c "from app.main import app; print(app)"

# Verify the environment file
cat /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' \
  /opt/fastapi-tutorial/.env
stat -c '%U:%G %a %n' /opt/fastapi-tutorial/.env

# Verify and reload the fastapi-tutorial unit
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl daemon-reload
systemctl show fastapi-tutorial \
  --property=User,WorkingDirectory,ExecStart,Restart,Environment

# Verify the exact fastapi-tutorial unit settings
grep -E '^(After|User|WorkingDirectory|Environment|ExecStart|Restart|WantedBy)=' \
  /etc/systemd/system/fastapi-tutorial.service

# Verify the FastAPI listener individually
ss -tlnp | grep ':8000'
curl -i http://127.0.0.1:8000/
curl -i http://127.0.0.1:8000/openapi.json
ps aux | grep '[u]vicorn app.main:app'

# Review logs for both named services
journalctl -u postgresql --no-pager -n 100
journalctl -u fastapi-tutorial --no-pager -n 100
systemctl --failed
systemctl show fastapi-tutorial \
  --property=ActiveState,SubState,Result,ExecMainStatus
```

Expected results:

- `postgresql` is enabled and active.
- `fastapi-tutorial` is enabled and active.
- PostgreSQL contains user `fastapi` and database `fastapi_db`, with `fastapi` as the database owner.
- The configured credentials connect successfully to `localhost:5432`.
- The application imports successfully from `app.main`.
- Uvicorn listens on `0.0.0.0:8000`.
- The FastAPI root and OpenAPI endpoints return HTTP responses.
- The systemd unit contains `After=network.target postgresql.service`, runs as `root`, uses `/opt/fastapi-tutorial` as its working directory, invokes the configured virtual-environment Uvicorn binary, and uses `Restart=always`.
