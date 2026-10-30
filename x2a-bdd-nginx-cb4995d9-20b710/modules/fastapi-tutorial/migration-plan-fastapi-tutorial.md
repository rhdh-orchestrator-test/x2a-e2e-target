---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys one FastAPI application from the `main` branch of `https://github.com/dibanez/fastapi_tutorial.git`. It installs Python, virtual-environment, Git, PostgreSQL, and PostgreSQL development packages; creates a Python virtual environment; installs application dependencies; provisions the PostgreSQL user `fastapi` and database `fastapi_db`; writes an environment file; and manages a systemd service listening on port `8000`. The database password is hardcoded in the Chef recipe and application connection string and must be replaced with an Ansible-managed secret.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application server
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Location/Path: `/opt/fastapi-tutorial`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Working directory: `/opt/fastapi-tutorial`
  - Port/Socket: `0.0.0.0:8000`
  - Application command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Systemd unit: `fastapi-tutorial.service`
  - Service user: `root`
  - Restart behavior: `Restart=always`
  - Environment PATH: `/opt/fastapi-tutorial/venv/bin`
  - Startup dependency: `network.target` and `postgresql.service`

- **postgresql**: PostgreSQL database service
  - Service name: `postgresql`
  - Database user: `fastapi`
  - Database name: `fastapi_db`
  - Database owner: `fastapi`
  - Database privileges: `ALL` on `fastapi_db`
  - Location/Path: PostgreSQL package-managed data location
  - Port/Socket: PostgreSQL package/service default; no explicit port is configured by this cookbook
  - Connection host: `localhost`
  - Current password: `fastapi_password`

There are no collection iterations or `.each` loops in the execution tree. The cookbook configures one FastAPI service and one PostgreSQL database/user combination.

## File Structure

Only the recipe file shown in the execution tree is used.

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

The `.env` file and systemd unit are created using inline Chef `file` resources. They are not cookbook static files or ERB templates.

## Module Explanation

The cookbook performs operations in the following order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the following seven packages using a Chef package resource:
     - `python3`
     - `python3-pip`
     - `python3-venv`
     - `git`
     - `postgresql`
     - `postgresql-contrib`
     - `libpq-dev`
   - Package versions are not pinned.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes the Git repository `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Does not define a Git notification for dependency installation or service restart.
   - Creates the virtual environment with:
     ```bash
     python3 -m venv /opt/fastapi-tutorial/venv
     ```
   - Guards virtual-environment creation on `/opt/fastapi-tutorial/venv` not already existing.
   - Installs application requirements with:
     ```bash
     /opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt
     ```
   - Runs dependency installation on every Chef execution because no guard is defined.
   - Enables and starts the `postgresql` service.
   - Creates the PostgreSQL user, database, and privileges using commands executed as the `postgres` operating-system user:
     ```bash
     sudo -u postgres psql -c "CREATE USER fastapi WITH PASSWORD 'fastapi_password';" || true
     sudo -u postgres psql -c "CREATE DATABASE fastapi_db OWNER fastapi;" || true
     sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE fastapi_db TO fastapi;" || true
     ```
   - Writes `/opt/fastapi-tutorial/.env` with owner `root`, group `root`, and mode `0644`:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
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
   - Notifies `execute[systemd_reload]` immediately when the systemd unit changes.
   - Executes `systemctl daemon-reload` only when notified.
   - Enables and starts the `fastapi-tutorial` service.
   - The Ansible migration should use package, file, git, command/pip, PostgreSQL, copy/template, and systemd modules while preserving the above paths and behavior.
   - The PostgreSQL shell commands should be replaced with idempotent `community.postgresql.postgresql_user`, `community.postgresql.postgresql_db`, and, if required, `community.postgresql.postgresql_privs` tasks.
   - The database password must be supplied from Ansible Vault, AAP credentials, or an approved external secret provider.
   - A systemd handler should run `daemon_reload: true` when the unit changes before the application service is enabled or started.

## Dependencies

**External cookbook dependencies**: None listed in the provided metadata.

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

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

**Application dependency source**: `/opt/fastapi-tutorial/requirements.txt`

The requirements file is obtained from the Git repository and installed into `/opt/fastapi-tutorial/venv`.

## Credentials

**Detection Summary**: One database credential detected in one recipe file. The same password appears in both the PostgreSQL creation command and the application connection string.

**Source**:
  - **Provider**: Hardcoded in the Chef recipe
  - **URL**: None
  - **Path**: None
  - **Secret storage**: No Chef Vault, encrypted data bag, data bag, CyberArk, Conjur, or external secret manager usage detected

### PostgreSQL database password

- **Variable(s)**:
  - No Chef attribute variable is used
  - Hardcoded literal: `fastapi_password`
  - Embedded in `DATABASE_URL`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded plaintext
- **Usage context**:
  - PostgreSQL user creation:
    ```sql
    CREATE USER fastapi WITH PASSWORD 'fastapi_password';
    ```
  - Application connection string:
    ```text
    DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
    ```
- **Migration handling**:
  - Store the password in Ansible Vault, AAP credentials, or an approved external secret provider.
  - Pass the managed secret to both the PostgreSQL user task and the `.env` template.
  - Do not commit the plaintext value to playbooks, role defaults, templates, or source code.
  - Consider changing `.env` permissions from `0644` to `0600` as a security improvement.

No TLS certificate, private key, API key, token, environment-based secret, data bag, or vault reference was detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Database objects to verify**:

- PostgreSQL role: `fastapi`
- PostgreSQL database: `fastapi_db`
- Database owner: `fastapi`
- Database privileges: `ALL`

**Service endpoints to check**:

- FastAPI: `0.0.0.0:8000`
- PostgreSQL: `localhost`, using the PostgreSQL package/service default port because no explicit port is configured

**Templates rendered**:

- ERB templates: `0`
- Inline file resources rendered/written: `2`
  - `/opt/fastapi-tutorial/.env`
  - `/etc/systemd/system/fastapi-tutorial.service`

## Pre-flight checks

### fastapi-tutorial application instance

```bash
ls -ld /opt/fastapi-tutorial
ls -ld /opt/fastapi-tutorial/venv
ls -l /opt/fastapi-tutorial/requirements.txt

git -C /opt/fastapi-tutorial remote -v
git -C /opt/fastapi-tutorial branch --show-current
git -C /opt/fastapi-tutorial rev-parse --verify HEAD

/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip --version
/opt/fastapi-tutorial/venv/bin/pip check
/opt/fastapi-tutorial/venv/bin/python -c "import fastapi; print(fastapi.__version__)"
/opt/fastapi-tutorial/venv/bin/python -c "import uvicorn; print(uvicorn.__version__)"

stat -c '%U %G %a %n' /opt/fastapi-tutorial/.env
grep '^PROJECT_NAME=' /opt/fastapi-tutorial/.env
grep '^API_VERSION=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env

systemctl cat fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl show fastapi-tutorial --property=User,WorkingDirectory,ExecStart,Restart
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service

curl -I http://127.0.0.1:8000/
curl -sS -o /tmp/fastapi-root-response.txt -w '%{http_code}\n' http://127.0.0.1:8000/
cat /tmp/fastapi-root-response.txt

ss -tlnp | grep ':8000'
lsof -nP -iTCP:8000 -sTCP:LISTEN

journalctl -u fastapi-tutorial --no-pager -n 100
```

Verify that:

- The repository remote is `https://github.com/dibanez/fastapi_tutorial.git`.
- The checked-out branch or revision corresponds to `main`.
- `/opt/fastapi-tutorial` exists with owner `root`, group `root`, and mode `0755`.
- The virtual environment and requirements file exist.
- `pip check` reports no broken dependencies.
- `fastapi` and `uvicorn` import successfully.
- The environment file contains the expected project name, API version, and managed database connection string.
- `fastapi-tutorial` is enabled and active.
- `User=root`.
- `WorkingDirectory=/opt/fastapi-tutorial`.
- `ExecStart` uses `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app`.
- The service binds to `0.0.0.0:8000`.
- `Restart=always`.
- The systemd unit passes `systemd-analyze verify`.
- The application responds on port `8000`.

### postgresql database instance

```bash
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev 2>/dev/null || \
rpm -q python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

systemctl status postgresql --no-pager
systemctl is-enabled postgresql
systemctl is-active postgresql
sudo -u postgres psql -c "SELECT version();"

sudo -u postgres psql -tAc "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"
sudo -u postgres psql -tAc "SELECT datname FROM pg_database WHERE datname = 'fastapi_db';"
sudo -u postgres psql -tAc "SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"

PGPASSWORD='REPLACE_WITH_MANAGED_SECRET' \
psql -h localhost -U fastapi -d fastapi_db -c "SELECT version();"

PGPASSWORD='REPLACE_WITH_MANAGED_SECRET' \
psql -h localhost -U fastapi -d fastapi_db -c "SELECT current_user, current_database();"

journalctl -u postgresql --no-pager -n 100
```

Verify that:

- All seven required packages are installed.
- PostgreSQL is enabled and active.
- The PostgreSQL version query succeeds.
- The `fastapi` role exists.
- The `fastapi_db` database exists.
- `fastapi` owns `fastapi_db`.
- The managed application credentials can connect to `localhost`.
- The connected user is `fastapi`.
- The connected database is `fastapi_db`.
- PostgreSQL starts without authentication or initialization errors.
- `REPLACE_WITH_MANAGED_SECRET` is supplied securely and is not committed to migration source code or shell history.