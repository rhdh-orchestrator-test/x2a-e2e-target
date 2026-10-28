---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI application from the `main` branch of `https://github.com/dibanez/fastapi_tutorial.git` into `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, and PostgreSQL development packages; creates a Python virtual environment; installs application dependencies; enables and starts PostgreSQL; creates the `fastapi` PostgreSQL role and `fastapi_db` database; writes the application environment file; and manages a systemd service running Uvicorn on `0.0.0.0:8000`.

## Service Type and Instances

**Service Type**: Application Server

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application served by Uvicorn
  - Location/Path: `/opt/fastapi-tutorial`
  - Source repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Git revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Port/Socket: `0.0.0.0:8000`
  - Process command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Run user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Restart policy: `Restart=always`
  - Key configuration: `PATH=/opt/fastapi-tutorial/venv/bin`; starts after `network.target` and `postgresql.service`

- **postgresql**: PostgreSQL database service required by the FastAPI application
  - Location/Path: PostgreSQL system installation
  - Port/Socket: The cookbook does not explicitly configure the PostgreSQL port or Unix socket
  - Service name: `postgresql`
  - State: Enabled and started
  - Database role: `fastapi`
  - Database: `fastapi_db`
  - Database owner: `fastapi`
  - Privileges: All privileges on `fastapi_db` granted to `fastapi`

There are no collection attributes or `.each` iterations in the analyzed cookbook.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**
```text
recipes/default.rb
```

**Providers:**
```text
```

No custom resources or provider files are used.

**Templates:**
```text
```

No Chef templates are rendered. The environment file and systemd unit are created using inline `file` resources.

**Attributes:**
```text
```

No attribute files are present or used.

**Files:**
```text
```

No static files are deployed with `cookbook_file` or `remote_file`.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev` system packages in one `package` resource.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates the virtual environment with `python3 -m venv /opt/fastapi-tutorial/venv`, guarded so it is not recreated when the path already exists.
   - Installs `/opt/fastapi-tutorial/requirements.txt` using `/opt/fastapi-tutorial/venv/bin/pip` with `/opt/fastapi-tutorial` as the working directory.
   - Enables and starts the `postgresql` service.
   - Runs database initialization as the `postgres` operating-system user:
     - Creates the PostgreSQL role `fastapi` with password `fastapi_password`.
     - Creates the `fastapi_db` database owned by `fastapi`.
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
   - Immediately runs `systemctl daemon-reload` when `/etc/systemd/system/fastapi-tutorial.service` changes.
   - Enables and starts the `fastapi-tutorial` service after the application source, virtual environment, dependencies, PostgreSQL service, database objects, `.env` file, systemd unit, and systemd reload are available.
   - Resource sequence:
     - `package`: 1 resource containing 7 package names
     - `directory`: 1 resource
     - `git`: 1 resource
     - `execute[create_venv]`
     - `execute[install_dependencies]`
     - `service[postgresql]`
     - `execute[create_db_user]`
     - `file[/opt/fastapi-tutorial/.env]`
     - `file[/etc/systemd/system/fastapi-tutorial.service]`
     - `execute[systemd_reload]`, action `nothing`, immediately notified by the systemd unit file
     - `service[fastapi-tutorial]`
   - Iterations: None; no `.each` loops are present.

## Dependencies

**External cookbook dependencies**: None declared.

**System package dependencies**:

- `python3`
- `python3-pip`
- `python3-venv`
- `git`
- `postgresql`
- `postgresql-contrib`
- `libpq-dev`

**Application dependency source**: `/opt/fastapi-tutorial/requirements.txt`, installed using `/opt/fastapi-tutorial/venv/bin/pip`.

**Service dependencies**:

- `postgresql`
- `fastapi-tutorial`

The FastAPI systemd unit declares `After=network.target postgresql.service`.

For the Ansible migration, PostgreSQL objects should preferably be managed with `community.postgresql.postgresql_user`, `community.postgresql.postgresql_db`, and, if required, `community.postgresql.postgresql_privs`, executed as the `postgres` operating-system user.

## Credentials

**Detection Summary**: One hardcoded database credential is detected in one recipe file and written into two generated configuration locations: the PostgreSQL creation command and the application `.env` database URL.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None
- **Path**: Embedded directly in `cookbooks/fastapi-tutorial/recipes/default.rb`

### PostgreSQL `fastapi` Database Password

- **Variable(s)**:
  - SQL password literal: `fastapi_password`
  - Generated connection string: `DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the recipe and written to `/opt/fastapi-tutorial/.env`
- **Usage context**:
  - Creates the PostgreSQL role `fastapi`
  - Authenticates the FastAPI application to PostgreSQL
  - Connects to the local `fastapi_db` database

No Chef data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, HashiCorp Vault, AWS Secrets Manager, environment-variable secret lookups, certificate files, or private-key references were detected.

The Ansible migration should store the password in Ansible Vault and use the vaulted value in both the PostgreSQL user task and the generated `.env` file. The existing `.env` mode is `0644`; tightening it to `0600` should be considered.

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
- All privileges on `fastapi_db` granted to `fastapi`

**Service endpoints to check**:

- FastAPI: `0.0.0.0:8000`
- PostgreSQL: `localhost`; the exact port is not explicitly configured by the cookbook

**Unix sockets**: No explicit Unix socket path is configured.

**Templates rendered**:

- No `.erb` templates are rendered.
- `/opt/fastapi-tutorial/.env`: 1 inline file resource
- `/etc/systemd/system/fastapi-tutorial.service`: 1 inline file resource

## Pre-flight checks

### fastapi-tutorial application instance

```bash
# Confirm required packages are installed
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

# Confirm the application directory and ownership
stat -c '%A %U:%G %n' /opt/fastapi-tutorial

# Confirm the repository content and revision
git -C /opt/fastapi-tutorial status --short
git -C /opt/fastapi-tutorial branch --show-current
git -C /opt/fastapi-tutorial rev-parse HEAD

# Confirm the requirements file and virtual environment
test -f /opt/fastapi-tutorial/requirements.txt
test -x /opt/fastapi-tutorial/venv/bin/python
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip --version
/opt/fastapi-tutorial/venv/bin/pip list

# Confirm environment configuration
stat -c '%A %U:%G %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION)=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env

# Confirm the systemd unit
stat -c '%A %U:%G %n' /etc/systemd/system/fastapi-tutorial.service
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl daemon-reload
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl status fastapi-tutorial --no-pager

# Confirm configured service values
grep -E '^(Description|After|Type|User|WorkingDirectory|Environment|ExecStart|Restart|WantedBy)=' \
  /etc/systemd/system/fastapi-tutorial.service

# Confirm the application is listening on port 8000
ss -tlnp | grep ':8000'
lsof -iTCP:8000 -sTCP:LISTEN

# Test application endpoints
curl -i http://127.0.0.1:8000/
curl -i http://127.0.0.1:8000/openapi.json

# Confirm the Uvicorn process
ps aux | grep '[u]vicorn app.main:app'

# Review application logs
journalctl -u fastapi-tutorial --no-pager -n 100
systemctl show fastapi-tutorial \
  --property=ActiveState,SubState,ExecMainStatus,ExecMainCode,NRestarts
```

Expected service configuration:

- `User=root`
- `WorkingDirectory=/opt/fastapi-tutorial`
- `ExecStart=/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
- `Restart=always`

The application should accept connections on port `8000`. The exact response from `/` depends on the repository application; `/openapi.json` should normally return a successful response for a functioning FastAPI application.

### postgresql database instance

```bash
# Confirm the PostgreSQL service is enabled and active
systemctl status postgresql --no-pager
systemctl is-enabled postgresql
systemctl is-active postgresql

# Confirm the PostgreSQL role exists
sudo -u postgres psql -tAc \
  "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"

# Confirm the database exists and has the correct owner
sudo -u postgres psql -tAc \
  "SELECT datname, pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"

# Confirm privileges on the database
sudo -u postgres psql -d fastapi_db -c "\l+ fastapi_db"

# Test application database credentials
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_user, current_database();"

# Test a basic database query
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT 1;"

# Review PostgreSQL logs
journalctl -u postgresql --no-pager -n 100
```

Expected database state:

- PostgreSQL is enabled and active.
- Role `fastapi` exists.
- Database `fastapi_db` exists and is owned by `fastapi`.
- `fastapi` has all privileges on `fastapi_db`.
- The application credentials connect successfully.
- `SELECT 1` returns one row.

### Network and service dependency checks

```bash
# Confirm the application port
ss -tlnp | grep ':8000'

# Confirm PostgreSQL service dependency
systemctl is-active postgresql
systemctl is-active fastapi-tutorial

# Follow application logs when diagnosing failures
journalctl -u fastapi-tutorial -f
```