---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI tutorial application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` under `/opt/fastapi-tutorial`, creates a Python virtual environment, installs application dependencies, installs and starts PostgreSQL, creates the `fastapi` PostgreSQL user and `fastapi_db` database, writes a plaintext `.env` file containing the database connection string, and manages the application with the `fastapi-tutorial` systemd service on TCP port `8000`.

## Service Type and Instances

**Service Type**: Application Server with PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application served by Uvicorn
  - Location/Path: `/opt/fastapi-tutorial`
  - Source repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Git revision: `main`
  - Python virtual environment: `/opt/fastapi-tutorial/venv`
  - Application entry point: `app.main:app`
  - Port/Socket: `0.0.0.0:8000`
  - Process command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Working directory: `/opt/fastapi-tutorial`
  - Runtime user: `root`
  - Restart behavior: `Restart=always`
  - Environment PATH: `/opt/fastapi-tutorial/venv/bin`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Environment file: `/opt/fastapi-tutorial/.env`

- **postgresql**: PostgreSQL database service used by the FastAPI application
  - Service name: `postgresql`
  - Location/Path: System PostgreSQL installation
  - Port/Socket: PostgreSQL local connection at `localhost`; no explicit TCP port is configured by the cookbook
  - Actions: enabled and started
  - Database user: `fastapi`
  - Database password: `fastapi_password`
  - Database name: `fastapi_db`
  - Database owner: `fastapi`
  - Database connection URL: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`

No collection iterations or `.each` loops are present. The package resource contains these explicit package names: `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

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

No Chef templates are rendered. Configuration is written using inline `file` resources.

**Attributes:**
```text
```

No attribute files are shown or used.

**Files:**
```text
```

No cookbook static files are deployed using `cookbook_file` or `remote_file`.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the seven system packages: `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates `/opt/fastapi-tutorial/venv` by running `python3 -m venv /opt/fastapi-tutorial/venv`, guarded by the existence of that path.
   - Installs Python dependencies from `/opt/fastapi-tutorial/requirements.txt` using `/opt/fastapi-tutorial/venv/bin/pip`.
   - Enables and starts the `postgresql` service.
   - Runs PostgreSQL setup commands as the `postgres` operating-system user:
     - Creates PostgreSQL user `fastapi` with password `fastapi_password`.
     - Creates database `fastapi_db` owned by `fastapi`.
     - Grants all privileges on `fastapi_db` to `fastapi`.
   - Each PostgreSQL command ends with `|| true`, making existing objects tolerated while also suppressing unrelated PostgreSQL errors.
   - Creates `/opt/fastapi-tutorial/.env` with:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Sets the `.env` owner and group to `root` and mode to `0644`.
   - Creates `/etc/systemd/system/fastapi-tutorial.service` with:
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
   - Sets the systemd unit owner and group to `root` and mode to `0644`.
   - Immediately notifies `execute[systemd_reload]` when `/etc/systemd/system/fastapi-tutorial.service` changes.
   - Defines `execute[systemd_reload]` to run `systemctl daemon-reload`; its action is `:nothing` unless notified.
   - Enables and starts the `fastapi-tutorial` systemd service.
   - Resource execution order:
     1. `package`: one resource containing seven packages
     2. `directory`: one resource
     3. `git`: one resource
     4. `execute`: Python virtual environment creation
     5. `execute`: Python dependency installation
     6. `service`: PostgreSQL enable and start
     7. `execute`: PostgreSQL user, database, and privilege commands
     8. `file`: application `.env`
     9. `file`: systemd unit
     10. `execute[systemd_reload]`: notification-only systemd reload
     11. `service`: FastAPI service enable and start

## Dependencies

**External cookbook dependencies**: None listed in `metadata.rb`.

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

**Application dependencies**:
- Python packages listed in `/opt/fastapi-tutorial/requirements.txt`

## Credentials

**Detection Summary**: 2 sensitive references detected in 1 recipe file. Both references contain the same PostgreSQL password.

**Source**:
  - **Provider**: Hardcoded in the Chef recipe
  - **URL**: None
  - **Path**: None
  - **Current storage**: Plaintext recipe content and plaintext `.env` output

### PostgreSQL database password

- **Variable(s)**: `fastapi_password`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in `execute[create_db_user]`
- **Usage context**: Sets the password for PostgreSQL user `fastapi`
- **Command context**:
  ```bash
  CREATE USER fastapi WITH PASSWORD 'fastapi_password';
  ```

### PostgreSQL password in `DATABASE_URL`

- **Variable(s)**: `DATABASE_URL`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in generated plaintext file `/opt/fastapi-tutorial/.env`
- **Usage context**: Application database connection
- **Value**:
  ```text
  postgresql://fastapi:fastapi_password@localhost/fastapi_db
  ```

No Chef data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, AWS Secrets Manager, HashiCorp Vault, environment-variable secret lookups, TLS certificates, private keys, or API tokens were detected.

For the migration, store the PostgreSQL password in Ansible Vault and construct `DATABASE_URL` from the vaulted value. Consider changing `.env` permissions from `0644` to `0600`.

## Checks for the Migration

**Files to verify**:
- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Database objects to verify**:
- PostgreSQL service: `postgresql`
- PostgreSQL user: `fastapi`
- PostgreSQL database: `fastapi_db`
- Database owner: `fastapi`

**Service endpoints to check**:
- `fastapi-tutorial`: TCP `0.0.0.0:8000`
- `postgresql`: local connection at `localhost`
- Unix sockets: none specified by the cookbook

**Templates rendered**: None. No Chef templates are present or rendered.

**Inline files rendered**:
- `/opt/fastapi-tutorial/.env`: 1 `file` resource
- `/etc/systemd/system/fastapi-tutorial.service`: 1 `file` resource

The systemd reload executes only when `/etc/systemd/system/fastapi-tutorial.service` changes.

## Pre-flight checks

```bash
# Verify all required system packages
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev 2>/dev/null || \
rpm -q python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

# Verify the fastapi-tutorial application instance
ls -ld /opt/fastapi-tutorial
ls -ld /opt/fastapi-tutorial/venv
ls -l /opt/fastapi-tutorial/requirements.txt
git -C /opt/fastapi-tutorial remote -v
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
git -C /opt/fastapi-tutorial status --short

# Verify the fastapi-tutorial Python environment and dependencies
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip --version
/opt/fastapi-tutorial/venv/bin/pip list
test -x /opt/fastapi-tutorial/venv/bin/uvicorn

# Verify the postgresql service instance
systemctl status postgresql --no-pager
systemctl is-enabled postgresql
systemctl is-active postgresql

# Verify the fastapi PostgreSQL user
sudo -u postgres psql -tAc \
  "SELECT usename FROM pg_catalog.pg_user WHERE usename = 'fastapi';"

# Verify the fastapi_db database and owner
sudo -u postgres psql -tAc \
  "SELECT datname FROM pg_database WHERE datname = 'fastapi_db';"
sudo -u postgres psql -tAc \
  "SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"

# Verify the fastapi_db connection
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

# Verify the application environment file
stat -c '%U %G %a %n' /opt/fastapi-tutorial/.env
grep '^PROJECT_NAME=' /opt/fastapi-tutorial/.env
grep '^API_VERSION=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env

# Verify the fastapi-tutorial systemd unit
systemctl cat fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl show fastapi-tutorial \
  --property=User,WorkingDirectory,ExecStart,Restart

# Verify the fastapi-tutorial HTTP endpoints
curl -i http://127.0.0.1:8000/
curl -i http://127.0.0.1:8000/docs
curl -i http://127.0.0.1:8000/openapi.json

# Verify the fastapi-tutorial listener and process
ss -tlnp | grep ':8000'
lsof -iTCP:8000 -sTCP:LISTEN
ps aux | grep '[u]vicorn'

# Review service logs and restart state
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u postgresql --no-pager -n 100
systemctl show fastapi-tutorial \
  --property=ExecMainStatus,ExecMainCode,NRestarts

# Verify systemd reload behavior after changing the unit
systemctl daemon-reload
systemctl restart fastapi-tutorial
systemctl status fastapi-tutorial --no-pager
```

Expected results:

- All seven system packages are installed.
- `/opt/fastapi-tutorial` is owned by `root:root` with mode `0755`.
- The repository remote is `https://github.com/dibanez/fastapi_tutorial.git` and revision `main` is checked out.
- `/opt/fastapi-tutorial/venv` and `/opt/fastapi-tutorial/requirements.txt` exist.
- The virtual environment contains the installed requirements and an executable `uvicorn`.
- The `postgresql` instance is enabled and active.
- PostgreSQL user `fastapi` exists.
- Database `fastapi_db` exists and is owned by `fastapi`.
- A connection to `fastapi_db` succeeds as user `fastapi`.
- `/opt/fastapi-tutorial/.env` contains `PROJECT_NAME`, `API_VERSION`, and `DATABASE_URL`.
- The `fastapi-tutorial` instance is enabled and active.
- The service runs as `root`, uses `/opt/fastapi-tutorial` as its working directory, and executes Uvicorn from the virtual environment.
- Uvicorn listens on `0.0.0.0:8000`.
- The FastAPI application returns an HTTP response from `/`; `/docs` and `/openapi.json` respond when exposed by the application.
- The application and PostgreSQL logs contain no startup failures or traceback loops.
- `ExecMainStatus` is `0`, and the FastAPI service is not repeatedly restarting.
- A systemd daemon reload occurs when `/etc/systemd/system/fastapi-tutorial.service` changes.

Avoid exposing `fastapi_password` in shell history in production. Use an Ansible Vault-backed mechanism or another protected secret source.