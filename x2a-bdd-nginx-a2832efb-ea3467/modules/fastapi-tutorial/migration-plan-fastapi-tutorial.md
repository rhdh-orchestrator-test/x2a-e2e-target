---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the `fastapi-tutorial` FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` under `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, and PostgreSQL development packages; creates a virtual environment; installs application requirements; creates the PostgreSQL `fastapi` user and `fastapi_db` database; writes database configuration to `.env`; and runs Uvicorn through the `fastapi-tutorial` systemd service on port `8000`.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application server
  - Source repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Location/Path: `/opt/fastapi-tutorial`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Port/Socket: `0.0.0.0:8000`
  - Startup command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Run user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Environment file: `/opt/fastapi-tutorial/.env`
  - Restart policy: `Restart=always`
  - Key configuration: `PROJECT_NAME="FastAPI Tutorial"`, `API_VERSION=1.0.0`

- **postgresql**: PostgreSQL database service
  - Service name: `postgresql`
  - Location/Path: System package-managed PostgreSQL installation
  - Port/Socket: Package-default PostgreSQL port, normally `localhost:5432`; no port override is configured
  - Database user: `fastapi`
  - Database password: `fastapi_password`
  - Database name: `fastapi_db`
  - Database owner: `fastapi`
  - Database privileges: `fastapi` receives all privileges on `fastapi_db`
  - Connection string: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
  - Service actions: enable and start

There are no collection attributes or `.each` iterations in the execution tree.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

Only the recipe file is used by the execution tree. No provider, template, attribute, or static cookbook file is referenced.

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

The repository cloned by the recipe is external application source, not a cookbook file:

```text
https://github.com/dibanez/fastapi_tutorial.git
```

## Module Explanation

The cookbook performs operations in this order. The cookbook has one entry recipe and no `include_recipe` calls.

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Package versions are not pinned.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates the virtual environment with `python3 -m venv /opt/fastapi-tutorial/venv`, guarded by the existence of `/opt/fastapi-tutorial/venv`.
   - Installs requirements using `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt` with `/opt/fastapi-tutorial` as the working directory. This command runs on every Chef execution.
   - Enables and starts `postgresql`.
   - Creates the PostgreSQL role, database, and privileges:
     - Role: `fastapi`
     - Password: `fastapi_password`
     - Database: `fastapi_db`
     - Owner: `fastapi`
     - Privileges: all privileges on `fastapi_db` for `fastapi`
   - The original shell commands run as the operating-system `postgres` user and use `|| true`; the migration should use idempotent `community.postgresql` modules instead.
   - Writes `/opt/fastapi-tutorial/.env` with:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
     The source properties are owner `root`, group `root`, and mode `0644`. Ansible should preferably use mode `0600` when compatibility permits.
   - Writes `/etc/systemd/system/fastapi-tutorial.service` with:
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
     The source properties are owner `root`, group `root`, and mode `0644`.
   - Defines `systemd_reload` with action `nothing`, executing `systemctl daemon-reload` when notified. The source-level notification from the service-unit file should be verified before treating it as confirmed migration behavior.
   - Enables and starts the `fastapi-tutorial` service.
   - Resource counts:
     - `package`: 1
     - `directory`: 1
     - `git`: 1
     - `execute`: 4 — `create_venv`, `install_dependencies`, `create_db_user`, and `systemd_reload`
     - `service`: 2 — `postgresql` and `fastapi-tutorial`
     - `file`: 2 — `/opt/fastapi-tutorial/.env` and `/etc/systemd/system/fastapi-tutorial.service`

## Dependencies

**External cookbook dependencies**: None listed in `metadata.rb`.

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

The FastAPI systemd unit declares `After=network.target postgresql.service`.

**Supported platforms from metadata**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

PostgreSQL service naming and package behavior must be checked on the target operating system, particularly on CentOS-based systems.

## Credentials

**Detection Summary**: 2 credential references detected in 1 file. Both references represent the same PostgreSQL credential.

**Source**:
  - **Provider**: Hardcoded in the Chef recipe
  - **URL**: None detected
  - **Path**: None detected
  - **Source file**: `cookbooks/fastapi-tutorial/recipes/default.rb`

### PostgreSQL database password

- **Variable(s)**: `fastapi_password`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`, PostgreSQL role creation command
  - `cookbooks/fastapi-tutorial/recipes/default.rb`, `.env` content
- **Current storage**: Hardcoded plaintext
- **Usage context**:
  - Sets the password for PostgreSQL user `fastapi`
  - Appears in the application `DATABASE_URL`

### PostgreSQL connection string

- **Variable(s)**: `DATABASE_URL`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded plaintext in `/opt/fastapi-tutorial/.env`
- **Value**: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Usage context**: Connects the application to the local `fastapi_db` PostgreSQL database

No Chef data bags, encrypted data bags, Chef Vault calls, CyberArk or Conjur integrations, environment-variable secret lookups, TLS certificates, private keys, API tokens, or external secret-manager URLs were detected.

Store the database password in Ansible Vault and render the PostgreSQL password and `DATABASE_URL` from vaulted variables.

## Checks for the Migration

**Files to verify**:

- `cookbooks/fastapi-tutorial/recipes/default.rb`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Application paths to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/venv`

**Database objects to verify**:

- PostgreSQL role: `fastapi`
- PostgreSQL database: `fastapi_db`
- Database owner: `fastapi`
- Database privileges for `fastapi`

**Service endpoints to check**:

- FastAPI: `0.0.0.0:8000`
- PostgreSQL: `localhost:5432`, normally
- PostgreSQL Unix socket: path reported by PostgreSQL configuration if TCP is unavailable

**Templates rendered**:

- None; both configuration files are created by inline Chef `file` resources.
- Render count: `0`

**Service behavior to verify**:

- `postgresql` is enabled and active.
- `fastapi-tutorial` is enabled and active.
- The FastAPI unit uses `/opt/fastapi-tutorial/venv/bin/uvicorn`.
- A daemon reload occurs when the systemd unit changes, subject to source-level notification verification.
- The dependency installation command remains unconditionally executed if exact Chef behavior is required.

## Pre-flight checks:

```bash
# Verify required packages
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev 2>/dev/null || \
rpm -q python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

# Verify FastAPI application source and virtual environment
test -d /opt/fastapi-tutorial
test -f /opt/fastapi-tutorial/requirements.txt
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
git -C /opt/fastapi-tutorial rev-parse --verify HEAD

# Verify the postgresql instance
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='fastapi';"
sudo -u postgres psql -tAc "SELECT datname FROM pg_database WHERE datname='fastapi_db';"
sudo -u postgres psql -tAc "SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname='fastapi_db';"
sudo -u postgres psql -tAc \
  "SELECT has_database_privilege('fastapi', 'fastapi_db', 'CONNECT');"

# Test PostgreSQL credentials and connectivity
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_database(), current_user;"

# Verify PostgreSQL endpoint
ss -tlnp | grep ':5432'
sudo -u postgres psql -tAc "SHOW unix_socket_directories;"

# Verify application environment
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' \
  /opt/fastapi-tutorial/.env
stat -c '%U:%G %a %n' /opt/fastapi-tutorial/.env

# Verify the fastapi-tutorial instance
systemctl cat fastapi-tutorial
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
grep -E '^(Description|After|Type|User|WorkingDirectory|Environment|ExecStart|Restart|WantedBy)=' \
  /etc/systemd/system/fastapi-tutorial.service

# Verify FastAPI HTTP endpoints
curl -i http://127.0.0.1:8000/
curl -i http://127.0.0.1:8000/docs
curl -i http://127.0.0.1:8000/openapi.json

# Verify the FastAPI process and endpoint
systemctl status fastapi-tutorial
pgrep -af 'uvicorn app.main:app'
ss -tlnp | grep ':8000'

# Review service logs
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u postgresql --no-pager -n 100

# Explicit systemd reload validation
systemctl daemon-reload
systemctl restart fastapi-tutorial
systemctl status fastapi-tutorial
```