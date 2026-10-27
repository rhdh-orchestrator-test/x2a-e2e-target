---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys one FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` on Ubuntu or CentOS. It installs Python, PostgreSQL, Git, and PostgreSQL development packages; creates a Python virtual environment; installs application dependencies; configures the PostgreSQL database `fastapi_db` and user `fastapi`; writes an environment file and systemd unit; and starts Uvicorn on TCP port `8000`. The PostgreSQL password is hardcoded in the Chef recipe and must be replaced with an Ansible-managed secret. The systemd daemon-reload notification relationship should be verified in the Chef source; if it is not confirmed, implement it explicitly as an Ansible handler.

## Service Type and Instances

**Service Type**: Application Server with PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI/Uvicorn application service
  - Location/Path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Git revision: `main`
  - Python virtual environment: `/opt/fastapi-tutorial/venv`
  - Application command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app`
  - Bind address: `0.0.0.0`
  - Port/Socket: TCP `8000`; no Unix socket
  - Working directory: `/opt/fastapi-tutorial`
  - Service user: `root`
  - Restart policy: `always`
  - systemd unit: `/etc/systemd/system/fastapi-tutorial.service`

- **postgresql**: Local PostgreSQL database service
  - Service name: `postgresql`
  - Database: `fastapi_db`
  - Database owner: `fastapi`
  - Database user: `fastapi`
  - Database host: `localhost`
  - Port/Socket: Platform-default PostgreSQL port and local Unix socket; no explicit socket path configured
  - Connection URL: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`

- **fastapi_db**: PostgreSQL database used by the FastAPI application
  - Location/Path: Local PostgreSQL instance
  - Owner: `fastapi`
  - Access: User `fastapi`
  - Connection host: `localhost`

- **fastapi**: PostgreSQL database role used by the application
  - Location/Path: Local PostgreSQL instance
  - Database access: `fastapi_db`
  - Password: Hardcoded as `fastapi_password` in the Chef source; replace with an Ansible-managed secret

There are no collection attributes or `.each` iterations in the supplied execution tree.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

The execution tree contains one executed recipe file. No providers, templates, attributes, or static files are shown as used.

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

The `.env` file and systemd unit are generated directly by Chef `file` resources, not from template files. The application `requirements.txt` file is supplied by the Git repository and is not a cookbook static file.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the seven required system packages: `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` to `/opt/fastapi-tutorial` at revision `main`.
   - Creates the virtual environment with `python3 -m venv /opt/fastapi-tutorial/venv`, guarded by `creates: /opt/fastapi-tutorial/venv`.
   - Installs Python dependencies with `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt` using `/opt/fastapi-tutorial` as the working directory.
   - Enables and starts the `postgresql` service.
   - Executes PostgreSQL initialization commands as the `postgres` operating-system user:
     - Creates the role `fastapi` with password `fastapi_password`.
     - Creates the database `fastapi_db` owned by `fastapi`.
     - Grants all privileges on `fastapi_db` to `fastapi`.
   - Uses `|| true` on the PostgreSQL commands, which provides weak idempotency and can hide genuine database errors. Replace these commands with PostgreSQL-specific Ansible modules.
   - Creates `/opt/fastapi-tutorial/.env` with owner `root`, group `root`, and mode `0644`.
   - Writes the following environment settings:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Creates `/etc/systemd/system/fastapi-tutorial.service` with owner `root`, group `root`, and mode `0644`.
   - Defines the systemd unit with:
     - Description `FastAPI Tutorial Service`
     - Ordering after `network.target` and `postgresql.service`
     - `Type=simple`
     - `User=root`
     - Working directory `/opt/fastapi-tutorial`
     - Virtual-environment path in `PATH`
     - Uvicorn target `app.main:app`
     - Bind address `0.0.0.0`
     - Port `8000`
     - `Restart=always`
     - Enablement through `multi-user.target`
   - Defines `execute['systemd_reload']` with the command `systemctl daemon-reload` and action `nothing`.
   - The source analysis does not verify a notification relationship from the systemd unit file resource to `execute['systemd_reload']`. Confirm that relationship in the Chef source. The Ansible migration must use a handler that reloads systemd when `/etc/systemd/system/fastapi-tutorial.service` changes.
   - Enables and starts the `fastapi-tutorial` service.
   - Iterations: None; no `.each` loops are present.

## Dependencies

**External cookbook dependencies**: None listed in the supplied metadata.

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

**Application dependency source**:

- `/opt/fastapi-tutorial/requirements.txt`, obtained from the Git repository

**Recommended Ansible collection dependencies**:

- `community.postgresql` for PostgreSQL user, database, and privilege management

## Credentials

**Detection Summary**: 1 database credential detected in `cookbooks/fastapi-tutorial/recipes/default.rb`. The same credential is written to the PostgreSQL creation command and the application `.env` file.

**Source**:
  - **Provider**: Hardcoded in Chef source
  - **URL**: None
  - **Path**: None
  - **Recommended replacement**: Ansible Vault, AAP credential injection, HashiCorp Vault, CyberArk, or another approved secret backend

### PostgreSQL database password

- **Variable(s)**:
  - No Chef attribute variable is used
  - Literal password: `fastapi_password`
  - Environment variable field: `DATABASE_URL`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**:
  - Hardcoded in `execute['create_db_user']`
  - Hardcoded again in `/opt/fastapi-tutorial/.env`
- **Usage context**:
  - Password for PostgreSQL user `fastapi`
  - Embedded in `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Migration action**:
  - Replace the literal with a protected variable such as `fastapi_db_password`.
  - Encrypt the variable with Ansible Vault or retrieve it from an approved external secret provider.
  - Do not expose the password in command-line arguments.
  - Change `.env` permissions to mode `0600` unless application requirements require otherwise.
  - Prevent the password from appearing in shell history or validation output.

No Chef data bags, encrypted data bags, Chef Vault calls, CyberArk integrations, Conjur calls, environment-variable secret lookups, TLS certificates, private keys, API tokens, or additional credential namespaces were detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Service endpoints to check**:

- `fastapi-tutorial`: TCP `8000` on `0.0.0.0`
- `postgresql`: `localhost` database connectivity through the platform-default PostgreSQL port and Unix socket

**Database objects to verify**:

- PostgreSQL role `fastapi`
- PostgreSQL database `fastapi_db`
- Owner of `fastapi_db`: `fastapi`
- All required privileges for `fastapi` on `fastapi_db`

**Templates rendered**:

- None
- `/opt/fastapi-tutorial/.env` is created by an inline Chef `file` resource.
- `/etc/systemd/system/fastapi-tutorial.service` is created by an inline Chef `file` resource.

## Pre-flight checks:

```bash
# Verify required packages on Ubuntu/Debian
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

# Verify required packages on CentOS/RHEL
rpm -q python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

# Verify the fastapi-tutorial application directory
stat -c '%A %U:%G %n' /opt/fastapi-tutorial
test -d /opt/fastapi-tutorial
test -d /opt/fastapi-tutorial/venv

# Verify the fastapi-tutorial repository
git -C /opt/fastapi-tutorial remote -v
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
git -C /opt/fastapi-tutorial status --short
test -f /opt/fastapi-tutorial/requirements.txt

# Verify the fastapi-tutorial virtual environment
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn

# Verify the PostgreSQL service instance
systemctl status postgresql --no-pager
systemctl is-enabled postgresql
systemctl is-active postgresql

# Verify the fastapi PostgreSQL role
sudo -u postgres psql -tAc \
  "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"

# Verify the fastapi_db database and owner
sudo -u postgres psql -tAc \
  "SELECT datname, pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"

# Verify fastapi_db connectivity as the PostgreSQL administrator
sudo -u postgres psql -d fastapi_db \
  -c "SELECT current_database(), current_user;"

# Verify fastapi connectivity without exposing the real password
PGPASSWORD='<retrieve-from-secret-store>' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT version();"

# Verify fastapi_db privileges
sudo -u postgres psql -d fastapi_db -c "\l+ fastapi_db"

# Verify the application environment file
test -f /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION)=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env | \
  sed -E 's#(postgresql://[^:]+:)[^@]+#\1REDACTED#'
stat -c '%A %U:%G %n' /opt/fastapi-tutorial/.env

# Verify the fastapi-tutorial systemd unit
test -f /etc/systemd/system/fastapi-tutorial.service
systemctl cat fastapi-tutorial
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl daemon-reload
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl status fastapi-tutorial --no-pager

# Verify the fastapi-tutorial process and endpoint
ps aux | grep '[u]vicorn app.main:app'
ss -tlnp | grep ':8000'
lsof -iTCP:8000 -sTCP:LISTEN
curl -i http://127.0.0.1:8000/
curl -i http://localhost:8000/

# Inspect fastapi-tutorial logs
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u fastapi-tutorial -f

# Verify fastapi-tutorial restart behavior
systemctl restart fastapi-tutorial
systemctl is-active fastapi-tutorial
ss -tlnp | grep ':8000'
journalctl -u fastapi-tutorial --since "5 minutes ago" --no-pager
```

The `fastapi-tutorial` service must be active, Uvicorn must listen on TCP port `8000`, and HTTP requests must return an application response rather than a connection-refused error. The migrated systemd unit must preserve `Restart=always`.

The Ansible implementation order is:

1. Install the seven system packages.
2. Create `/opt/fastapi-tutorial` with root ownership and mode `0755`.
3. Synchronize the Git repository at revision `main`.
4. Create `/opt/fastapi-tutorial/venv`.
5. Install requirements from `/opt/fastapi-tutorial/requirements.txt`.
6. Enable and start `postgresql`.
7. Create PostgreSQL role `fastapi` with a protected password.
8. Create database `fastapi_db` owned by `fastapi`.
9. Grant required privileges on `fastapi_db` to `fastapi`.
10. Deploy `/opt/fastapi-tutorial/.env` without a hardcoded password.
11. Deploy `/etc/systemd/system/fastapi-tutorial.service`.
12. Notify a systemd daemon-reload handler when the unit changes.
13. Enable and start `fastapi-tutorial`.
14. Validate `fastapi_db`, `fastapi`, PostgreSQL connectivity, and FastAPI availability on port `8000`.