---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook installs the system dependencies for a FastAPI application, synchronizes the `main` branch of `https://github.com/dibanez/fastapi_tutorial.git` into `/opt/fastapi-tutorial`, creates a Python virtual environment, installs `requirements.txt`, enables and starts PostgreSQL, creates the `fastapi` PostgreSQL role and `fastapi_db` database, writes the application environment configuration, and manages a systemd service listening on TCP port `8000`. The application runs as `root` with an inline plaintext database password that should be migrated to Ansible Vault or an AAP secret-management integration.

## Service Type and Instances

**Service Type**: Application Server

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application server
  - Location/Path: `/opt/fastapi-tutorial`
  - Source repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Git revision: `main`
  - Python virtual environment: `/opt/fastapi-tutorial/venv`
  - Port/Socket: TCP `8000`, bound to `0.0.0.0`
  - Application command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - System user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Restart policy: `Restart=always`
  - Environment configuration: `/opt/fastapi-tutorial/.env`

- **PostgreSQL**: Local database service for the FastAPI application
  - Service name: `postgresql`
  - State: Enabled and started
  - Database role: `fastapi`
  - Database: `fastapi_db`
  - Database owner: `fastapi`
  - Database host: `localhost`
  - Port/Socket: Cookbook does not specify a TCP port or Unix socket path
  - Connection string: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**
```text
cookbooks/fastapi-tutorial/recipes/default.rb
```

**Providers:**

None detected.

**Templates:**

None detected. The cookbook uses inline content in Chef `file` resources rather than `.erb` templates.

**Attributes:**

None detected.

**Files:**

None detected. No `cookbook_file` or `remote_file` resource is present.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the seven required system packages:
     - `python3`
     - `python3-pip`
     - `python3-venv`
     - `git`
     - `postgresql`
     - `postgresql-contrib`
     - `libpq-dev`
   - No package versions are pinned.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates the Python virtual environment with:
     ```bash
     python3 -m venv /opt/fastapi-tutorial/venv
     ```
   - Runs virtual-environment creation only when `/opt/fastapi-tutorial/venv` does not exist.
   - Installs dependencies from `/opt/fastapi-tutorial/requirements.txt` into `/opt/fastapi-tutorial/venv`.
   - Enables and starts the `postgresql` service.
   - Executes the following database setup commands:
     ```bash
     sudo -u postgres psql -c "CREATE USER fastapi WITH PASSWORD 'fastapi_password';" || true
     sudo -u postgres psql -c "CREATE DATABASE fastapi_db OWNER fastapi;" || true
     sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE fastapi_db TO fastapi;" || true
     ```
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
   - Notifies `execute['systemd_reload']` when the systemd unit changes.
   - Runs `systemctl daemon-reload` through `execute['systemd_reload']`, with action `nothing`.
   - Enables and starts the `fastapi-tutorial` systemd service.
   - No `.each` loops or collection iterations are present.

For the Ansible migration:

- Use `ansible.builtin.package` for the seven system packages.
- Use `ansible.builtin.file` for `/opt/fastapi-tutorial`.
- Use `ansible.builtin.git` with `repo`, `dest`, `version: main`, and `update: true`.
- Use `ansible.builtin.command` with `creates: /opt/fastapi-tutorial/venv` to create the virtual environment.
- Use `ansible.builtin.pip` with the requirements file and virtual environment.
- Use `ansible.builtin.service` or `ansible.builtin.systemd_service` for PostgreSQL.
- Use `community.postgresql.postgresql_user`, `community.postgresql.postgresql_db`, and, if needed, `community.postgresql.postgresql_privs` instead of shell commands for database management.
- Use `ansible.builtin.copy` for the inline `.env` and systemd unit content, or a role template if templating is required.
- Store the database password in Ansible Vault or an AAP credential integration.
- Use `ansible.builtin.systemd_service` with `daemon_reload: true` in a handler when `/etc/systemd/system/fastapi-tutorial.service` changes.
- Enable and start `fastapi-tutorial` after the systemd daemon reload.

## Dependencies

**External cookbook dependencies**: None declared in the supplied metadata.

**System package dependencies**:

- `python3`
- `python3-pip`
- `python3-venv`
- `git`
- `postgresql`
- `postgresql-contrib`
- `libpq-dev`

**External source dependencies**:

- Repository: `https://github.com/dibanez/fastapi_tutorial.git`
- Revision: `main`

**Service dependencies**:

- `postgresql`
- `fastapi-tutorial`

The FastAPI systemd unit declares:

```ini
After=network.target postgresql.service
```

## Credentials

**Detection Summary**: 1 credential detected in 1 recipe file. The same hardcoded password is used by the database creation command and the generated connection string.

**Source**:

- **Provider**: Hardcoded
- **URL**: None
- **Path**: None

### PostgreSQL `fastapi` Password

- **Variable(s)**: No named Chef attribute; literal value is `fastapi_password`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded plaintext in an `execute` resource and the inline `/opt/fastapi-tutorial/.env` file
- **Usage context**:
  - PostgreSQL role creation:
    ```sql
    CREATE USER fastapi WITH PASSWORD 'fastapi_password';
    ```
  - Application connection:
    ```text
    DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
    ```

The migration should store this password in Ansible Vault or an AAP credential/secret-management integration. The literal password should not be committed to role tasks or variable files.

No data bag, Chef Vault, Conjur, CyberArk, environment-variable secret lookup, TLS certificate, private key, API token, or external vault URL was detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/app.main` source location as supplied by the cloned repository

The cookbook explicitly creates `.env`, the virtual-environment directory, and the systemd unit. The cloned repository supplies `requirements.txt` and the application source.

**Database objects to verify**:

- PostgreSQL role `fastapi`
- PostgreSQL database `fastapi_db`
- Owner of `fastapi_db`: `fastapi`
- Privileges granted to `fastapi`

**Service endpoints to check**:

- **fastapi-tutorial**: HTTP on TCP port `8000`
- **PostgreSQL**: Local PostgreSQL service; no cookbook-specified TCP port or Unix socket path

**Templates rendered**:

- None; no templates are used.
- Inline Chef file content writes `/opt/fastapi-tutorial/.env` once.
- Inline Chef file content writes `/etc/systemd/system/fastapi-tutorial.service` once.

## Pre-flight checks

### fastapi-tutorial application checks

```bash
# Verify required packages
dpkg -s python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

# Verify Python and the virtual environment
python3 --version
test -x /opt/fastapi-tutorial/venv/bin/python
/opt/fastapi-tutorial/venv/bin/python --version

# Verify the repository and dependency file
git -C /opt/fastapi-tutorial remote -v
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
test -f /opt/fastapi-tutorial/requirements.txt

# Verify installed Python dependencies
/opt/fastapi-tutorial/venv/bin/pip check

# Verify the application environment file
stat -c '%U %G %a %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION)=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env | \
  sed -E 's#(postgresql://[^:]+:)[^@]+#\1********#'

# Verify the systemd unit
systemctl cat fastapi-tutorial.service
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl status fastapi-tutorial
grep '^ExecStart=' /etc/systemd/system/fastapi-tutorial.service
grep -- '--port 8000' /etc/systemd/system/fastapi-tutorial.service

# Verify the process and listening endpoint
ps aux | grep '[u]vicorn app.main:app'
ss -tlnp | grep ':8000'
curl -i http://127.0.0.1:8000/
curl -i http://localhost:8000/
```

Expected application properties:

- The `fastapi-tutorial` service is enabled and active.
- Uvicorn runs from `/opt/fastapi-tutorial/venv/bin/uvicorn`.
- The application runs as `root`.
- The working directory is `/opt/fastapi-tutorial`.
- The application listens on TCP port `8000` on all IPv4 interfaces.
- The service uses `Restart=always`.
- The application returns an HTTP response. No dedicated `/health` or `/ready` endpoint is defined.

### PostgreSQL checks

```bash
# Verify service state
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql

# Verify the PostgreSQL role
sudo -u postgres psql -tAc \
  "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"

# Verify the database
sudo -u postgres psql -tAc \
  "SELECT datname FROM pg_database WHERE datname = 'fastapi_db';"

# Verify database ownership
sudo -u postgres psql -tAc \
  "SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"

# Verify application-user connectivity
PGPASSWORD='fastapi_password' \
psql -h localhost -U fastapi -d fastapi_db -c "SELECT version();"

# Verify a query against the application database
PGPASSWORD='fastapi_password' \
psql -h localhost -U fastapi -d fastapi_db -c "SELECT current_database();"
```

Supply the password securely during actual validation rather than committing it to shell history. Verify that:

- The `postgresql` service is enabled and active.
- Role `fastapi` exists.
- Database `fastapi_db` exists and is owned by `fastapi`.
- The `fastapi` role can connect to `fastapi_db`.
- The role has the required database privileges.

### Systemd and failure checks

```bash
# Validate the systemd unit
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service

# Confirm systemd has loaded the unit
systemctl show fastapi-tutorial.service \
  --property=FragmentPath,ExecStart,User,WorkingDirectory

# Inspect FastAPI logs
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u fastapi-tutorial -f

# Inspect PostgreSQL logs
journalctl -u postgresql --no-pager -n 100

# Check for failed services
systemctl --failed
```

The Ansible migration must notify a systemd daemon reload when `/etc/systemd/system/fastapi-tutorial.service` changes, then ensure `fastapi-tutorial` is enabled and started.