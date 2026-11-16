---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI Tutorial application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main`. It installs Python, Git, and PostgreSQL dependencies, initializes PostgreSQL where required, creates the application directory and Python virtual environment, installs the repository requirements, creates PostgreSQL database `fastapi_db` and user `fastapi`, writes the application environment configuration, and manages the application with the `fastapi-tutorial.service` systemd unit listening on port `8000`. The database password is currently hardcoded as `fastapi_password` and must be migrated to Ansible Vault or an approved secret manager.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application server
  - Application path: `/opt/fastapi-tutorial`
  - Python virtual environment: `/opt/fastapi-tutorial/venv`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Application command: `uvicorn app.main:app`
  - Bind address: `0.0.0.0`
  - Port: `8000`
  - Service user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Restart policy: `always`

- **fastapi_db**: PostgreSQL application database
  - Database owner/user: `fastapi`
  - Database host: `localhost`
  - Database port: PostgreSQL default port; no explicit port is configured by the cookbook
  - Database connection: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
  - PostgreSQL service: `postgresql`

## File Structure

**MANDATORY: Preserve this section from the original plan.**

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

The `.env` file and systemd unit are created using inline Chef `file` resources. They are not static cookbook files.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Evaluates `platform_family?('fedora', 'rhel')` to select the platform-specific package branch.
   - On RHEL/Fedora systems, installs `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, and `libpq-devel`.
   - On RHEL/Fedora systems, runs `postgresql-setup --initdb` with `/var/lib/pgsql/data/PG_VERSION` as the creation guard.
   - On non-RHEL/Fedora systems, installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` to `/opt/fastapi-tutorial` at revision `main`.
   - Creates the Python virtual environment with:
     ```bash
     python3 -m venv /opt/fastapi-tutorial/venv
     ```
     using `/opt/fastapi-tutorial/venv` as the creation guard.
   - Installs Python dependencies with:
     ```bash
     /opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt
     ```
     from working directory `/opt/fastapi-tutorial`.
   - Enables and starts the `postgresql` service.
   - Creates PostgreSQL role `fastapi`, database `fastapi_db`, and grants all privileges on `fastapi_db` to `fastapi`.
   - Creates `/opt/fastapi-tutorial/.env` with:
     - `PROJECT_NAME="FastAPI Tutorial"`
     - `API_VERSION=1.0.0`
     - `DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db`
   - Creates `/etc/systemd/system/fastapi-tutorial.service` with:
     - `User=root`
     - `WorkingDirectory=/opt/fastapi-tutorial`
     - `Environment="PATH=/opt/fastapi-tutorial/venv/bin"`
     - `ExecStart=/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
     - `Restart=always`
     - `After=network.target postgresql.service`
   - Runs `systemctl daemon-reload` when the systemd unit changes.
   - Enables and starts the `fastapi-tutorial` service.
   - The recipe has no `.each` loops or collection-based iterations.
   - The dependency installation, `.env` file, and repository changes do not automatically restart the application service.

The Ansible implementation should preserve the execution order. It should use idempotent PostgreSQL modules instead of reproducing the Chef commands that suppress errors with `|| true`. The database password should be sourced from Ansible Vault or an approved secret manager. The systemd unit should continue running as `root` unless an approved hardening change introduces a dedicated application user and updates ownership and permissions consistently.

## Dependencies

**External cookbook dependencies**: None declared in the supplied metadata or execution tree.

**System package dependencies**:

RHEL/Fedora:
- `python3`
- `python3-pip`
- `git`
- `postgresql-server`
- `postgresql-contrib`
- `libpq-devel`

Non-RHEL/Fedora:
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
- `network.target`

The FastAPI systemd unit declares:
```ini
After=network.target postgresql.service
```

## Credentials

**Detection Summary**: 1 credential detected in 1 source file.

**Source**:
  - **Provider**: Hardcoded in the Chef recipe
  - **URL**: None
  - **Path**: None

### PostgreSQL database password

- **Variable(s)**:
  - No Chef attribute variable is used.
  - Hardcoded password: `fastapi_password`
  - Embedded in `DATABASE_URL`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**:
  - Hardcoded in the `execute[create_db_user]` command
  - Hardcoded in the inline `/opt/fastapi-tutorial/.env` content
- **Usage context**:
  - Sets the PostgreSQL password for user `fastapi`
  - Authenticates the FastAPI application to database `fastapi_db`
- **Migration requirement**:
  - Store the password in Ansible Vault or an approved secret manager.
  - Use the vaulted value in the PostgreSQL user task.
  - Use the same value when constructing `DATABASE_URL`.
  - Do not expose the password in task output or normal logs.

No data bags, Chef Vault references, CyberArk, Conjur, Vault attributes, environment-based secret references, TLS certificate references, or API tokens were detected.

## Checks for the Migration

**Files to verify**:
- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/app/main.py`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/venv/bin/python`
- `/opt/fastapi-tutorial/venv/bin/pip`
- `/opt/fastapi-tutorial/venv/bin/uvicorn`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- PostgreSQL data directory created by the platform-specific installation
- `/var/lib/pgsql/data/PG_VERSION` on RHEL/Fedora systems

**Database objects to verify**:
- PostgreSQL role: `fastapi`
- PostgreSQL database: `fastapi_db`
- Database owner: `fastapi`
- All privileges on `fastapi_db` granted to `fastapi`

**Service endpoints to check**:
- `fastapi-tutorial`: `0.0.0.0:8000`
- `fastapi_db`: local PostgreSQL listener using the platform default port

**Templates rendered**:
- None; 0 templates rendered

**Inline configuration files created**:
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

## Pre-flight checks:

### `fastapi-tutorial` application instance

```bash
# Confirm application packages and tools
python3 --version
python3 -m pip --version
git --version

# Confirm repository and revision
git -C /opt/fastapi-tutorial status
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
git -C /opt/fastapi-tutorial rev-parse HEAD

# Confirm required application files
test -f /opt/fastapi-tutorial/requirements.txt
test -f /opt/fastapi-tutorial/app/main.py

# Confirm virtual environment executables
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn

# Confirm installed Python dependencies
/opt/fastapi-tutorial/venv/bin/pip list

# Validate the environment file without exposing the password
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' /opt/fastapi-tutorial/.env
stat -c '%U:%G %a %n' /opt/fastapi-tutorial/.env

# Validate the systemd unit
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl daemon-reload
systemctl cat fastapi-tutorial

# Confirm application service state
systemctl status fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial

# Confirm the expected application process
ps aux | grep '[u]vicorn app.main:app'

# Verify the FastAPI endpoint and listener
curl -i http://127.0.0.1:8000/
ss -tlnp | grep ':8000'
lsof -iTCP:8000 -sTCP:LISTEN

# Review application logs
journalctl -u fastapi-tutorial --no-pager -n 100
```

The application listener should be bound to `0.0.0.0:8000` or an equivalent IPv4 wildcard address. The root endpoint should return an HTTP response.

### `fastapi_db` database instance

```bash
# Confirm PostgreSQL client
psql --version

# Confirm PostgreSQL service state
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql

# Confirm the PostgreSQL role exists
sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='fastapi';"

# Confirm the database and owner
sudo -u postgres psql -tAc "SELECT datname, pg_catalog.pg_get_userbyid(datdba) FROM pg_database WHERE datname='fastapi_db';"

# Confirm application-role connectivity
PGPASSWORD='REDACTED' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_database(), current_user;"

# Confirm database privileges
sudo -u postgres psql -d fastapi_db -c "\dp"

# Review PostgreSQL logs
journalctl -u postgresql --no-pager -n 100
```

The connectivity check should report database `fastapi_db` and user `fastapi`. On RHEL/Fedora systems, also verify PostgreSQL initialization:

```bash
test -f /var/lib/pgsql/data/PG_VERSION
```

On non-RHEL/Fedora systems, verify virtual-environment support:

```bash
python3 -m venv --help
```

Check for successful PostgreSQL startup, successful FastAPI database connectivity, no authentication failures, no missing Python dependencies, no import errors from `app.main`, and no repeated service restart loop.