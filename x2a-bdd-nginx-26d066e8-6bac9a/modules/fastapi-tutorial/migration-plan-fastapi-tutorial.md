---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI tutorial application from `https://github.com/dibanez/fastapi_tutorial.git` into `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, PostgreSQL development dependencies, and application requirements; creates a Python virtual environment; configures the local `fastapi_db` PostgreSQL database and `fastapi` user; writes an environment file containing the database connection string; and manages a systemd service running Uvicorn on port `8000`. The cookbook configures one FastAPI application instance and one PostgreSQL database instance.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application served by Uvicorn
  - Location/Path: `/opt/fastapi-tutorial`
  - Source repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Git revision: `main`
  - Python virtual environment: `/opt/fastapi-tutorial/venv`
  - Service user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Application command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Listening address: `0.0.0.0`
  - Port: `8000`
  - Restart policy: `Restart=always`
  - Startup dependency: `postgresql.service`
  - Service unit: `/etc/systemd/system/fastapi-tutorial.service`

- **postgresql.service**: Local PostgreSQL service used by the FastAPI application
  - Service name: `postgresql`
  - Connection host: `localhost`
  - Port: `5432` by default, unless configured differently by the host distribution
  - Configured database: `fastapi_db`
  - Configured user: `fastapi`
  - Database owner: `fastapi`
  - Database privileges: `fastapi` receives all privileges on `fastapi_db`
  - Connection string: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**
```text
cookbooks/fastapi-tutorial/recipes/default.rb
```

**Providers:**
```text
```

No custom Chef resources or provider files are used.

**Templates:**
```text
```

No ERB templates are rendered. Configuration files are created directly with inline content in the recipe.

**Attributes:**
```text
```

No attribute files were identified or used.

**Files:**
```text
```

No static files from `files/default/` or `files/` are deployed by the cookbook.

## Module Explanation

The cookbook performs operations in this order. There are no collection attributes or `.each` loops in the recipe.

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the following seven system packages with one `package` resource:
     - `python3`
     - `python3-pip`
     - `python3-venv`
     - `git`
     - `postgresql`
     - `postgresql-contrib`
     - `libpq-dev`
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` into `/opt/fastapi-tutorial` at revision `main`.
   - Creates the virtual environment with `execute[create_venv]`:
     ```bash
     python3 -m venv /opt/fastapi-tutorial/venv
     ```
     guarded by `creates: /opt/fastapi-tutorial/venv`.
   - Installs Python dependencies with `execute[install_dependencies]`:
     ```bash
     /opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt
     ```
     using `/opt/fastapi-tutorial` as the working directory.
   - Enables and starts `postgresql.service`.
   - Creates the PostgreSQL user and database with `execute[create_db_user]`:
     ```bash
     sudo -u postgres psql -c "CREATE USER fastapi WITH PASSWORD 'fastapi_password';" || true
     sudo -u postgres psql -c "CREATE DATABASE fastapi_db OWNER fastapi;" || true
     sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE fastapi_db TO fastapi;" || true
     ```
     The commands create the `fastapi` user, assign password `fastapi_password`, create `fastapi_db`, assign ownership to `fastapi`, and grant all database privileges. Each command suppresses failures with `|| true`.
   - Creates `/opt/fastapi-tutorial/.env` with owner `root`, group `root`, and mode `0644`:
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
     The service runs as `root`, uses `/opt/fastapi-tutorial` as its working directory, places the virtual environment in `PATH`, listens on all IPv4 interfaces at port `8000`, and restarts automatically if it exits. The unit is ordered after `network.target` and `postgresql.service`.
   - Defines `execute[systemd_reload]` with `action :nothing` to run:
     ```bash
     systemctl daemon-reload
     ```
     It is triggered immediately when `/etc/systemd/system/fastapi-tutorial.service` changes.
   - Enables and starts `fastapi-tutorial.service`.
   - Does not explicitly configure `EnvironmentFile=/opt/fastapi-tutorial/.env`; the application must independently load `.env` to consume those variables.

## Dependencies

**External cookbook dependencies**: None declared in the analyzed metadata.

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
- `fastapi-tutorial.service`

The FastAPI service is ordered after `network.target` and `postgresql.service`.

## Credentials

**Detection Summary**: 1 database credential detected in `cookbooks/fastapi-tutorial/recipes/default.rb`. The credential is used to create the PostgreSQL user and is written into the application environment file as part of `DATABASE_URL`.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None detected
- **Path**: None detected
- **Data bag or vault**: None detected
- **CyberArk or Conjur integration**: None detected
- **HashiCorp Vault integration**: None detected
- **AWS Secrets Manager integration**: None detected

### PostgreSQL application password

- **Variable(s)**:
  - PostgreSQL password: `fastapi_password`
  - PostgreSQL username: `fastapi`
  - Database name: `fastapi_db`
  - Database URL: `DATABASE_URL`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in `execute[create_db_user]` and inline `.env` file content
- **Usage context**:
  - Sets the password for PostgreSQL user `fastapi`
  - Creates the connection string for `fastapi_db`
  - Is stored in `/opt/fastapi-tutorial/.env`
  - Is used by the FastAPI application to connect to local PostgreSQL

The Ansible migration should store `fastapi_password` in Ansible Vault or an approved AAP credential or secret integration. The plaintext password should not be committed to a playbook, role default, or visible task argument. The migrated `.env` file should preferably use mode `0600` rather than the current `0644`.

No TLS certificate, private key, API token, SSH credential, encrypted data bag, Chef Vault item, environment-variable secret lookup, CyberArk reference, or Conjur reference was detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Database objects to verify**:

- PostgreSQL role: `fastapi`
- PostgreSQL database: `fastapi_db`
- Database owner: `fastapi`
- `ALL` privileges for `fastapi` on `fastapi_db`

**Service endpoints to check**:

- FastAPI instance `fastapi-tutorial`: `http://127.0.0.1:8000`
- FastAPI listening port: `8000`
- PostgreSQL instance `postgresql.service`: `localhost:5432`, unless the distribution uses another port
- PostgreSQL local connection target: `localhost`

**Unix sockets**:

- PostgreSQL may expose a distribution-specific local Unix socket. The cookbook does not configure a socket path, so the migrated deployment should discover the active PostgreSQL socket rather than hardcoding one.

**Templates rendered**:

- None; no ERB templates are present.
- `/opt/fastapi-tutorial/.env`: written once by an inline `file` resource.
- `/etc/systemd/system/fastapi-tutorial.service`: written once by an inline `file` resource.

## Pre-flight checks

```bash
# Verify required Debian-family packages
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

# Verify required RPM-family packages when applicable
rpm -q python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

# Verify the application directory and repository
stat -c '%A %U:%G %n' /opt/fastapi-tutorial
git -C /opt/fastapi-tutorial status --short
git -C /opt/fastapi-tutorial branch --show-current
test -f /opt/fastapi-tutorial/requirements.txt

# Verify the Python virtual environment and dependencies
test -x /opt/fastapi-tutorial/venv/bin/python
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip --version
/opt/fastapi-tutorial/venv/bin/pip list
test -x /opt/fastapi-tutorial/venv/bin/uvicorn
/opt/fastapi-tutorial/venv/bin/uvicorn --version
```

### PostgreSQL instance: `postgresql.service`

```bash
systemctl status postgresql --no-pager
systemctl is-enabled postgresql
systemctl is-active postgresql

sudo -u postgres psql -c "SELECT version();"
sudo -u postgres psql -tAc "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"
sudo -u postgres psql -tAc "SELECT datname, pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"
sudo -u postgres psql -d fastapi_db -c "\dp"

# Use the migrated secret rather than exposing it in shell history where possible
PGPASSWORD='fastapi_password' \
psql -h localhost -U fastapi -d fastapi_db -c "SELECT current_user, current_database();"
```

Expected database results are:

- `current_user` is `fastapi`.
- `current_database` is `fastapi_db`.
- The `fastapi` role exists.
- `fastapi_db` exists and is owned by `fastapi`.
- `fastapi` has all required privileges.

### FastAPI instance: `fastapi-tutorial`

```bash
# Verify environment file ownership and mode
stat -c '%A %U:%G %n' /opt/fastapi-tutorial/.env

# Verify non-secret environment values
grep -E '^(PROJECT_NAME|API_VERSION)=' /opt/fastapi-tutorial/.env

# Verify DATABASE_URL without printing its password
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env | \
  sed -E 's#(postgresql://[^:]+:)[^@]+#\1REDACTED#'

# Verify the systemd unit
stat -c '%A %U:%G %n' /etc/systemd/system/fastapi-tutorial.service
systemctl cat fastapi-tutorial.service
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl daemon-reload

# Verify the FastAPI service state
systemctl status fastapi-tutorial --no-pager
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl show fastapi-tutorial \
  --property=User,WorkingDirectory,ExecStart,Restart,After

# Verify port 8000 and HTTP responses
ss -tlnp | grep ':8000'
curl -i http://127.0.0.1:8000/
curl -i http://localhost:8000/

# Verify the Uvicorn process and service logs
ps -ef | grep '[u]vicorn app.main:app'
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u postgresql --no-pager -n 100
```

Expected FastAPI service properties are:

- `User=root`
- `WorkingDirectory=/opt/fastapi-tutorial`
- `Restart=always`
- `ExecStart` invokes `/opt/fastapi-tutorial/venv/bin/uvicorn`
- The service is ordered after PostgreSQL.
- Uvicorn is listening on TCP port `8000`.
- The application responds to an HTTP request.

### Application and database integration

```bash
systemctl is-active fastapi-tutorial

PGPASSWORD='fastapi_password' \
psql -h localhost -U fastapi -d fastapi_db -c "SELECT 1;"

journalctl -u fastapi-tutorial -f
```

A successful migration must show PostgreSQL active and enabled, the `fastapi` role present, `fastapi_db` owned by `fastapi`, the `fastapi-tutorial` service active and enabled, Uvicorn listening on port `8000`, successful HTTP connectivity, and no repeated startup failures in the service logs.