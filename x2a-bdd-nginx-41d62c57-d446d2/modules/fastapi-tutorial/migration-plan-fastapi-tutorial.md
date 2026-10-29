---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI application from the `main` branch of `https://github.com/dibanez/fastapi_tutorial.git` into `/opt/fastapi-tutorial`. It installs Python, PostgreSQL, Git, and PostgreSQL development packages; creates a Python virtual environment; installs application dependencies; provisions the PostgreSQL `fastapi` role and `fastapi_db` database; writes an environment file and systemd unit; and enables and starts PostgreSQL and the FastAPI service. FastAPI listens on port `8000` and connects to PostgreSQL on `localhost:5432`.

## Service Type and Instances

**Service Type**: Application Server with PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application service
  - Location/Path: `/opt/fastapi-tutorial`
  - Source repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Git revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Port/Socket: `0.0.0.0:8000`
  - Application command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Working directory: `/opt/fastapi-tutorial`
  - Runtime user: `root`
  - Restart policy: `Restart=always`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Key configuration: `Environment="PATH=/opt/fastapi-tutorial/venv/bin"`

- **PostgreSQL**: Local application database service
  - Location/Path: Managed by the installed PostgreSQL packages
  - Port/Socket: `localhost:5432`; platform-default Unix socket may also be available
  - Chef service name: `postgresql`
  - Database: `fastapi_db`
  - Database owner: `fastapi`
  - Database user: `fastapi`
  - Database privileges: `ALL` on `fastapi_db`
  - Service actions: enable and start

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

The `.env` file and systemd service file are generated inline by `file` resources. They are not static cookbook files or templates.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the seven system packages `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Uses one `package` resource containing all seven packages.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial` using one `git` resource.
   - Runs `python3 -m venv /opt/fastapi-tutorial/venv` through `execute[create_venv]` only when the virtual-environment path does not exist.
   - Installs dependencies with `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt` from working directory `/opt/fastapi-tutorial` through `execute[install_dependencies]`.
   - Enables and starts `service[postgresql]`.
   - Runs PostgreSQL provisioning through `execute[create_db_user]` as the `postgres` operating-system user:
     - Creates role `fastapi` with password `fastapi_password`.
     - Creates database `fastapi_db` owned by `fastapi`.
     - Grants `ALL` privileges on `fastapi_db` to `fastapi`.
     - The original shell commands use `|| true`, which suppresses both already-exists conditions and unrelated PostgreSQL errors.
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
   - The systemd unit immediately notifies `execute[systemd_reload]`, which runs `systemctl daemon-reload`. `execute[systemd_reload]` has action `nothing` and does not run independently.
   - Enables and starts `service[fastapi-tutorial]`.
   - FastAPI starts after the repository, virtual environment, dependencies, PostgreSQL service, database objects, `.env` file, systemd unit, and daemon reload are available.

**Ansible migration requirements**:

- Use `ansible.builtin.package` or the platform-appropriate package module for the exact seven-package list.
- Use `ansible.builtin.file` for `/opt/fastapi-tutorial`.
- Use `ansible.builtin.git` with the exact repository, destination, and `main` revision.
- Use `ansible.builtin.command` for virtual-environment creation with an idempotence check for `/opt/fastapi-tutorial/venv/bin/activate` or `/opt/fastapi-tutorial/venv/bin/python`.
- Use `ansible.builtin.pip` with requirements `/opt/fastapi-tutorial/requirements.txt` and virtual environment `/opt/fastapi-tutorial/venv`.
- Use `ansible.builtin.service` to enable and start `postgresql`.
- Prefer `community.postgresql.postgresql_user`, `community.postgresql.postgresql_db`, and `community.postgresql.postgresql_privs` for PostgreSQL provisioning instead of ignoring shell failures.
- Store the database password in Ansible Vault and construct `DATABASE_URL` from the vaulted value.
- Deploy the `.env` and systemd unit with `ansible.builtin.copy` or `ansible.builtin.template`.
- Use an Ansible handler with `ansible.builtin.systemd` and `daemon_reload: true` when the systemd unit changes.
- Use `ansible.builtin.systemd` to enable and start `fastapi-tutorial`.

**Iterations**:

- Iteration count: `0`
- No `.each` loops are defined.
- No collection attributes are present.
- No additional application instances, databases, sites, workers, or service names are generated.

## Dependencies

**External cookbook dependencies**: None listed in the provided metadata.

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

**Application dependency source**: `/opt/fastapi-tutorial/requirements.txt`, supplied by the Git repository at revision `main`.

## Credentials

**Detection Summary**: 1 credential detected in 1 source file. The same hardcoded password is used for PostgreSQL provisioning and in the database connection URL.

**Source**:
  - **Provider**: Hardcoded
  - **URL**: None
  - **Path**: None
  - **Chef data bags / encrypted data bags**: None detected
  - **Chef Vault**: None detected
  - **CyberArk or Conjur**: None detected
  - **Environment-based secret lookup**: None detected

### PostgreSQL `fastapi` Password

- **Variable(s)**:
  - No Chef attribute variable is used.
  - Hardcoded literal: `fastapi_password`
  - Connection string variable: `DATABASE_URL`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded directly in the recipe and inline `.env` content
- **Usage context**:
  - PostgreSQL role creation:
    ```sql
    CREATE USER fastapi WITH PASSWORD 'fastapi_password';
    ```
  - Database connection:
    ```text
    DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
    ```
- **Migration recommendation**:
  - Store the password in Ansible Vault as `fastapi_db_password`.
  - Use the vaulted value for PostgreSQL user creation and `DATABASE_URL`.
  - Do not commit the plaintext password to the Ansible repository.
  - Prefer mode `0600` for the migrated `.env` file because it contains database credentials; the current Chef mode is `0644`.

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
- Owner `fastapi`
- `ALL` privileges on `fastapi_db`

**Service endpoints to check**:

- **fastapi-tutorial**: `0.0.0.0:8000`
- **PostgreSQL**: `localhost:5432`
- PostgreSQL platform-default Unix socket, if enabled by the installed PostgreSQL configuration

**Templates rendered**:

- None; no Chef `.erb` templates are used.

**Inline files generated**:

- `/opt/fastapi-tutorial/.env`: rendered once by `file[/opt/fastapi-tutorial/.env]`
- `/etc/systemd/system/fastapi-tutorial.service`: rendered once by `file[/etc/systemd/system/fastapi-tutorial.service]`

## Pre-flight checks

```bash
# Verify required packages for fastapi-tutorial and PostgreSQL
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

# Verify the fastapi-tutorial application directory
stat -c '%A %U:%G %n' /opt/fastapi-tutorial
test -d /opt/fastapi-tutorial
test -f /opt/fastapi-tutorial/requirements.txt

# Verify the repository and main revision
git -C /opt/fastapi-tutorial status
git -C /opt/fastapi-tutorial branch --show-current

# Verify the fastapi-tutorial virtual environment and executables
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn

# Verify the PostgreSQL instance
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
sudo -u postgres pg_isready -h localhost -p 5432

# Verify the fastapi PostgreSQL role
sudo -u postgres psql -tAc \
  "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"

# Verify fastapi_db and its owner
sudo -u postgres psql -tAc \
  "SELECT datname, pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"

# Verify fastapi database connectivity
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -p 5432 \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_database(), current_user;"

# Verify fastapi_db privileges
sudo -u postgres psql -tAc \
  "SELECT datname, has_database_privilege('fastapi', datname, 'CONNECT,CREATE,TEMPORARY') FROM pg_database WHERE datname = 'fastapi_db';"

# Verify the application environment file without exposing the password
stat -c '%A %U:%G %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION)=' /opt/fastapi-tutorial/.env
sed -E 's#(postgresql://[^:]+:)[^@]+@#\1REDACTED@#' \
  /opt/fastapi-tutorial/.env

# Verify the fastapi-tutorial systemd unit
cat /etc/systemd/system/fastapi-tutorial.service
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl daemon-reload
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl status fastapi-tutorial

# Verify the FastAPI process and endpoint
ps aux | grep '[u]vicorn'
ss -tlnp | grep ':8000'
lsof -iTCP:8000 -sTCP:LISTEN
curl -i http://127.0.0.1:8000/
curl -i http://localhost:8000/

# Verify fastapi-tutorial unit ordering and working directory
systemctl show fastapi-tutorial -p After -p Wants -p Requires
readlink -f /proc/"$(pgrep -f '/opt/fastapi-tutorial/venv/bin/uvicorn' | head -1)"/cwd

# Review logs for both named services
journalctl -u postgresql --no-pager -n 100
journalctl -u fastapi-tutorial --no-pager -n 100
systemctl is-active postgresql
systemctl is-active fastapi-tutorial
```

Expected results:

- `/opt/fastapi-tutorial` exists with root ownership and mode `0755`.
- The repository is checked out at `main`.
- The virtual environment contains executable Python, pip, and Uvicorn binaries.
- PostgreSQL is enabled and active on `localhost:5432`.
- The `fastapi` role exists and owns `fastapi_db`.
- PostgreSQL connectivity succeeds as user `fastapi`.
- The `.env` file contains `PROJECT_NAME="FastAPI Tutorial"` and `API_VERSION=1.0.0`; its password is not printed in command output.
- The systemd unit validates successfully, is enabled, and is active.
- FastAPI runs from `/opt/fastapi-tutorial/venv/bin/uvicorn`.
- `fastapi-tutorial` listens on port `8000` and responds to HTTP requests.
- Logs contain no Python import errors, missing dependency errors, database authentication failures, PostgreSQL connection failures, port binding failures, or repeated restarts.
- The cookbook does not define a health endpoint, so `/health` must not be assumed to exist.