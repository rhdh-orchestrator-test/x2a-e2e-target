---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI tutorial application from `https://github.com/dibanez/fastapi_tutorial.git` into `/opt/fastapi-tutorial`, installs Python, Git, PostgreSQL, and PostgreSQL development packages, creates a Python virtual environment, installs application requirements, provisions the `fastapi` PostgreSQL role and `fastapi_db` database, writes an environment file containing the database connection URL, and manages the application with the `fastapi-tutorial.service` systemd unit listening on `0.0.0.0:8000`. The cookbook defines one application instance, `fastapi-tutorial`, and contains no recipe iteration or collection-based configuration.

## Service Type and Instances

**Service Type**: Application Server with PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application served by Uvicorn
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Location/Path: `/opt/fastapi-tutorial`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Application entry point: `app.main:app`
  - Process command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Port/Socket: `0.0.0.0:8000`
  - Systemd unit: `fastapi-tutorial.service`
  - Systemd user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Restart policy: `always`
  - Key configuration: systemd service starts after `network.target` and `postgresql.service`, uses `/opt/fastapi-tutorial/venv/bin` in `PATH`, and is enabled for `multi-user.target`

- **postgresql**: PostgreSQL database service for the FastAPI application
  - Service name: `postgresql`
  - Database: `fastapi_db`
  - Database owner: `fastapi`
  - Database user: `fastapi`
  - Host: `localhost`
  - Port/Socket: PostgreSQL default listener; no explicit port or Unix socket is configured
  - Connection URL: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`

There are no collection attributes or `.each` loops in the analyzed recipe.

## File Structure

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

No Chef templates are rendered. The application environment file and systemd unit are created using inline `file` resources.

**Attributes:**

```text
```

No attribute files are shown or used.

**Files:**

```text
```

No static files are deployed using `cookbook_file` or `remote_file`.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the system packages `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev` with one `package` resource.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates the virtual environment with `python3 -m venv /opt/fastapi-tutorial/venv`, guarded by `creates: /opt/fastapi-tutorial/venv`.
   - Installs `/opt/fastapi-tutorial/requirements.txt` using `/opt/fastapi-tutorial/venv/bin/pip` with `/opt/fastapi-tutorial` as the working directory.
   - Enables and starts the `postgresql` service.
   - Executes PostgreSQL provisioning as the `postgres` operating-system user:
     - Creates the role `fastapi` with password `fastapi_password`.
     - Creates the database `fastapi_db` owned by `fastapi`.
     - Grants all privileges on `fastapi_db` to `fastapi`.
     - Each provisioning command ends with `|| true`, so existing-object or command errors do not fail the Chef resource.
   - Creates `/opt/fastapi-tutorial/.env` once with owner `root`, group `root`, and mode `0644`, containing:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Creates `/etc/systemd/system/fastapi-tutorial.service` once with owner `root`, group `root`, and mode `0644`, containing:
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
   - Immediately notifies `execute[systemd_reload]` when the systemd unit changes.
   - Runs `systemctl daemon-reload` through `execute[systemd_reload]`, whose default action is `nothing`.
   - Enables and starts the `fastapi-tutorial` service.
   - Iterations: none; there are no `.each` loops.

## Dependencies

**External cookbook dependencies**: None listed in the metadata or execution tree.

**System package dependencies**:

- `python3`
- `python3-pip`
- `python3-venv`
- `git`
- `postgresql`
- `postgresql-contrib`
- `libpq-dev`

**Application dependency source**: `/opt/fastapi-tutorial/requirements.txt`, supplied by the synchronized Git repository and installed into `/opt/fastapi-tutorial/venv`.

**Service dependencies**:

- `postgresql`
- `fastapi-tutorial`
- `fastapi-tutorial.service` starts after `network.target` and `postgresql.service`

## Credentials

**Detection Summary**: 2 credential references detected in `cookbooks/fastapi-tutorial/recipes/default.rb`. Both reference the same hardcoded PostgreSQL password and are used during database provisioning and application connection configuration.

**Source**:
  - **Provider**: Hardcoded in the Chef recipe
  - **URL**: None
  - **Path**: None; no data bag, vault, CyberArk, Conjur, or external secret-manager path is used

### PostgreSQL password used during database creation

- **Variable(s)**: No variable; literal value `fastapi_password`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded plaintext in the `execute[create_db_user]` command
- **Usage context**: Creates the PostgreSQL role with `CREATE USER fastapi WITH PASSWORD 'fastapi_password';`

### PostgreSQL password embedded in the application connection URL

- **Variable(s)**: `DATABASE_URL`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded plaintext in the generated `/opt/fastapi-tutorial/.env` file
- **Usage context**: Connects the application to `fastapi_db` using `fastapi` at `localhost`

No data bags, encrypted data bags, Chef Vault, Conjur, CyberArk, HashiCorp Vault, AWS Secrets Manager, TLS certificates, private keys, PEM credentials, or environment-variable password lookups were detected.

For the Ansible migration, store the PostgreSQL password in Ansible Vault, reference it in both the PostgreSQL user task and `.env` deployment, and use `no_log: true` for secret-bearing tasks.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Database objects to verify**:

- PostgreSQL role `fastapi`
- PostgreSQL database `fastapi_db`
- Database owner `fastapi`
- All database privileges granted to `fastapi`

**Service endpoints to check**:

- `fastapi-tutorial`: `0.0.0.0:8000`
- `postgresql`: default PostgreSQL listener on `localhost`; no explicit port is configured

**Templates rendered**: None.

**Inline files rendered**:

- `/opt/fastapi-tutorial/.env` — 1 render
- `/etc/systemd/system/fastapi-tutorial.service` — 1 render

## Pre-flight checks:

```bash
# Package checks on Debian/Ubuntu
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

# Use the equivalent package-query command on CentOS-compatible systems.

# Application directory, repository, and virtual environment
test -d /opt/fastapi-tutorial
git -C /opt/fastapi-tutorial rev-parse --is-inside-work-tree
git -C /opt/fastapi-tutorial branch --show-current
git -C /opt/fastapi-tutorial rev-parse --verify HEAD
test -f /opt/fastapi-tutorial/requirements.txt
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip

# PostgreSQL instance: postgresql
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
sudo -u postgres psql -tAc "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"
sudo -u postgres psql -tAc "SELECT datname FROM pg_database WHERE datname = 'fastapi_db';"
sudo -u postgres psql -tAc "SELECT pg_catalog.pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"
sudo -u postgres psql -tAc \
  "SELECT has_database_privilege('fastapi', 'fastapi_db', 'CONNECT');"

# Application database connectivity
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT 1;"

# Environment file
stat -c '%U %G %a %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' /opt/fastapi-tutorial/.env

# Systemd unit and daemon configuration
stat -c '%U %G %a %n' /etc/systemd/system/fastapi-tutorial.service
systemctl cat fastapi-tutorial
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service

# FastAPI instance: fastapi-tutorial
systemctl status fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
ps aux | grep '[u]vicorn'
ss -tlnp | grep ':8000'
lsof -iTCP:8000 -sTCP:LISTEN

# FastAPI HTTP endpoint
curl -I http://127.0.0.1:8000/
curl -sS http://127.0.0.1:8000/

# Service logs
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u postgresql --no-pager -n 100

# Restart behavior for fastapi-tutorial
systemctl restart fastapi-tutorial
systemctl is-active fastapi-tutorial
curl -I http://127.0.0.1:8000/
```

Expected results include:

- The `postgresql` instance is enabled and active.
- The `fastapi` role and `fastapi_db` database exist.
- `fastapi_db` is owned by `fastapi`, and the role has `CONNECT` privileges.
- The `fastapi-tutorial` instance is enabled and active.
- Uvicorn runs from `/opt/fastapi-tutorial/venv/bin/uvicorn`.
- The application listens on `0.0.0.0:8000`.
- The systemd unit contains `WorkingDirectory=/opt/fastapi-tutorial`, `Environment="PATH=/opt/fastapi-tutorial/venv/bin"`, the configured Uvicorn `ExecStart`, `Restart=always`, and `After=network.target postgresql.service`.
- The FastAPI endpoint accepts TCP connections. The exact HTTP status for `/` depends on the routes in the Git repository.
- The application returns to the active state and accepts connections after restart.