---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the `fastapi-tutorial` FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` under `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, and PostgreSQL development packages; creates a Python virtual environment; installs application dependencies; creates the `fastapi` PostgreSQL user and `fastapi_db` database; writes an environment file; and manages the `fastapi-tutorial` systemd service on port `8000`. The application runs as `root`, and PostgreSQL is its database dependency.

## Service Type and Instances

**Service Type**: Application Server with PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application server
  - Application path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Git revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Service user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Listening address: `0.0.0.0`
  - Listening port: `8000`
  - Startup command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Restart policy: `always`

- **PostgreSQL**: Application database service
  - Service name: `postgresql`
  - Database: `fastapi_db`
  - Database user: `fastapi`
  - Database host: `localhost`
  - Database port: `5432`
  - Database owner: `fastapi`
  - Connection string: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`

## File Structure

```text
cookbooks/fastapi-tutorial/
├── attributes/
│   └── default.rb
├── files/
│   └── default/
├── providers/
├── recipes/
│   └── default.rb
└── templates/
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

No ERB templates are rendered. Configuration files are created using inline Chef `file` resources.

**Attributes:**
```text
cookbooks/fastapi-tutorial/attributes/default.rb
```

**Files:**
```text
```

No static files from `files/default/*` or `files/*` are deployed.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs platform-specific system packages.
   - On Fedora/RHEL, installs `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, and `libpq-devel`.
   - On non-Fedora/RHEL platforms, including Ubuntu, installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - On Fedora/RHEL, runs `postgresql-setup --initdb` with `creates: /var/lib/pgsql/data/PG_VERSION`.
   - Creates `/opt/fastapi-tutorial` owned by `root:root` with mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates `/opt/fastapi-tutorial/venv` using `python3 -m venv /opt/fastapi-tutorial/venv`, guarded by the virtual-environment path.
   - Installs dependencies with `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt` from `/opt/fastapi-tutorial`.
   - Enables and starts `service[postgresql]`.
   - Creates the PostgreSQL user `fastapi` with password `fastapi_password`.
   - Creates the PostgreSQL database `fastapi_db` owned by `fastapi`.
   - Grants all privileges on `fastapi_db` to `fastapi`.
   - Creates `/opt/fastapi-tutorial/.env` owned by `root:root` with mode `0644`, containing:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Creates `/etc/systemd/system/fastapi-tutorial.service` owned by `root:root` with mode `0644`, containing:
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
   - Defines `execute[systemd_reload]` for `systemctl daemon-reload` with action `nothing`.
   - Notifies `execute[systemd_reload]` immediately when `/etc/systemd/system/fastapi-tutorial.service` changes.
   - Enables and starts `service[fastapi-tutorial]`.
   - Resources execute in this order: platform package installation, PostgreSQL initialization when applicable, application directory creation, Git synchronization, virtual-environment creation, dependency installation, PostgreSQL service management, database-user and database creation, `.env` creation, systemd-unit creation, conditional systemd reload, and FastAPI service management.
   - No `.each` loops or collection-based iterations are present.

## Dependencies

**External cookbook dependencies**: None declared in the supplied `metadata.rb`.

**System package dependencies**:

- **Fedora/RHEL**:
  - `python3`
  - `python3-pip`
  - `git`
  - `postgresql-server`
  - `postgresql-contrib`
  - `libpq-devel`
- **Other supported platforms, including Ubuntu**:
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

The FastAPI systemd unit declares `After=network.target postgresql.service`.

## Credentials

**Detection Summary**: 1 hardcoded database credential detected in 1 file.

**Source**:
  - **Provider**: Hardcoded in the Chef recipe
  - **URL**: None detected
  - **Path**: `cookbooks/fastapi-tutorial/recipes/default.rb`

### PostgreSQL Password

- **Variable(s)**: No Chef attribute variable is used. The literal password is `fastapi_password`.
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in a PostgreSQL creation command and an inline `.env` file.
- **Usage context**:
  - PostgreSQL user creation:
    ```text
    CREATE USER fastapi WITH PASSWORD 'fastapi_password';
    ```
  - Application connection string:
    ```text
    DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
    ```
- **Migration recommendation**: Store the password in Ansible Vault, AAP credentials, or an approved secret-management system using a variable such as `fastapi_db_password`. Mark tasks that handle the password with `no_log: true`.

No Chef data bags, encrypted data bags, Chef Vault items, CyberArk/Conjur calls, environment-variable secret lookups, TLS certificate references, API keys, or tokens were detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/fastapi-tutorial/attributes/default.rb`
- `cookbooks/fastapi-tutorial/recipes/default.rb`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- `/var/lib/pgsql/data/` on Fedora/RHEL
- Distribution-managed PostgreSQL data paths on Debian/Ubuntu

**Service endpoints to check**:

- `fastapi-tutorial`: `0.0.0.0:8000`
- `postgresql`: `localhost:5432`
- PostgreSQL distribution-managed local Unix socket

**Templates rendered**:

- None; 0 templates rendered.
- `/opt/fastapi-tutorial/.env`: 1 inline file resource
- `/etc/systemd/system/fastapi-tutorial.service`: 1 inline file resource

## Pre-flight checks:

```bash
# Application instance: fastapi-tutorial
test -d /opt/fastapi-tutorial
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn
test -f /opt/fastapi-tutorial/requirements.txt
test -f /opt/fastapi-tutorial/.env
test -f /etc/systemd/system/fastapi-tutorial.service

git -C /opt/fastapi-tutorial rev-parse --is-inside-work-tree
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
git -C /opt/fastapi-tutorial status --short

# Expected application branch
test "$(git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD)" = "main"

# PostgreSQL instance
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
ss -ltnp | grep ':5432'

sudo -u postgres psql -tAc \
  "SELECT usename FROM pg_catalog.pg_user WHERE usename = 'fastapi';"

sudo -u postgres psql -tAc \
  "SELECT datname FROM pg_database WHERE datname = 'fastapi_db';"

sudo -u postgres psql -tAc \
  "SELECT datname, pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"

# Validate PostgreSQL connectivity without exposing the password in command history
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_database(), current_user;"

# Application configuration
stat -c '%U:%G %a %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' /opt/fastapi-tutorial/.env

# Systemd unit validation
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
grep -E '^(Description|After|Type|User|WorkingDirectory|Environment|ExecStart|Restart|WantedBy)=' \
  /etc/systemd/system/fastapi-tutorial.service

systemctl daemon-reload
systemctl status fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial

# FastAPI instance endpoint and process
ss -ltnp | grep ':8000'
curl -i http://127.0.0.1:8000/
ps aux | grep '[u]vicorn app.main:app'

# Logs
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u postgresql --no-pager -n 100

# Python dependencies
/opt/fastapi-tutorial/venv/bin/python -m pip list
/opt/fastapi-tutorial/venv/bin/uvicorn --version

# Port ownership
lsof -iTCP:5432 -sTCP:LISTEN
lsof -iTCP:8000 -sTCP:LISTEN

# Expected ownership:
# PostgreSQL owns port 5432.
# FastAPI/Uvicorn owns port 8000.
```