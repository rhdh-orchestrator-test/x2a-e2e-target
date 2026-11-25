---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys one FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, and PostgreSQL development dependencies; creates a Python virtual environment; installs the repository requirements; initializes and manages PostgreSQL; creates the `fastapi` database user and `fastapi_db` database; writes an application `.env` file; and manages a systemd service named `fastapi-tutorial` listening on port `8000`. The cookbook supports RHEL/Fedora-style and Debian/Ubuntu-style package layouts.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application served by Uvicorn
  - Application path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Start command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Port: `0.0.0.0:8000`
  - systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - systemd user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Restart policy: `Restart=always`

- **PostgreSQL**: Local application database service
  - Service name: `postgresql`
  - Database: `fastapi_db`
  - Database owner: `fastapi`
  - Database user: `fastapi`
  - Database host: `localhost`
  - Port: normally `5432`
  - RHEL/Fedora initialization: `postgresql-setup --initdb`
  - Non-RHEL/Fedora initialization: package installation only; no explicit initialization command is executed by the recipe

## File Structure

The following are the relevant cookbook files.

**Recipes:**
```text
cookbooks/fastapi-tutorial/recipes/default.rb
```

**Providers:**
```text
```

No custom Chef providers are used.

**Templates:**
```text
```

No `.erb` templates are used. Configuration is written directly by `file` resources.

**Attributes:**
```text
cookbooks/fastapi-tutorial/attributes/default.rb
```

**Files:**
```text
```

No static files are deployed with `cookbook_file` or `remote_file`.

## Module Explanation

The cookbook performs operations in this order. The only recipe is `default.rb`; there are no `.each` loops or collection-valued attributes.

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Reads the configurable attributes `app_path`, `repository`, `revision`, and `service_port` from `cookbooks/fastapi-tutorial/attributes/default.rb`.
   - Defaults:
     - `node['fastapi_tutorial']['app_path]`: `/opt/fastapi-tutorial`
     - `node['fastapi_tutorial']['repository']`: `https://github.com/dibanez/fastapi_tutorial.git`
     - `node['fastapi_tutorial']['revision']`: `main`
     - `node['fastapi_tutorial']['service_port']`: `8000`
   - On RHEL/Fedora systems, installs:
     - `python3`
     - `python3-pip`
     - `git`
     - `postgresql-server`
     - `postgresql-contrib`
     - `libpq-devel`
   - On non-RHEL/Fedora systems, installs:
     - `python3`
     - `python3-pip`
     - `python3-venv`
     - `git`
     - `postgresql`
     - `postgresql-contrib`
     - `libpq-dev`
   - On RHEL/Fedora systems, runs `postgresql-setup --initdb` with `creates: /var/lib/pgsql/data/PG_VERSION`.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates `/opt/fastapi-tutorial/venv` with:
     ```bash
     python3 -m venv /opt/fastapi-tutorial/venv
     ```
     using `creates: /opt/fastapi-tutorial/venv`.
   - Installs Python dependencies from `/opt/fastapi-tutorial/requirements.txt` using:
     ```bash
     /opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt
     ```
     with working directory `/opt/fastapi-tutorial`.
   - Enables and starts the `postgresql` service.
   - Creates PostgreSQL user `fastapi` with password `fastapi_password`.
   - Creates PostgreSQL database `fastapi_db` owned by `fastapi`.
   - Grants all privileges on `fastapi_db` to `fastapi`.
   - The Chef database commands append `|| true`, silently ignoring duplicate-object and other command failures. The Ansible migration should use idempotent PostgreSQL modules and fail on unexpected errors.
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
   - The systemd unit notifies `execute[systemd_reload]` when changed.
   - Runs `systemctl daemon-reload` only when notified by the changed systemd unit.
   - Enables and starts the `fastapi-tutorial` service after the unit is deployed and systemd is reloaded.
   - The service intentionally runs as `root`; a dedicated unprivileged service user would be a hardening change rather than an exact behavioral translation.

## Dependencies

**External cookbook dependencies**: None listed in `metadata.rb`.

**System package dependencies**:

RHEL/Fedora branch:

- `python3`
- `python3-pip`
- `git`
- `postgresql-server`
- `postgresql-contrib`
- `libpq-devel`

Non-RHEL/Fedora branch:

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

## Credentials

**Detection Summary**: 2 credential references detected across `cookbooks/fastapi-tutorial/recipes/default.rb`. Both references use the same hardcoded PostgreSQL password.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None
- **Path**: None

### PostgreSQL database password

- **Variable(s)**:
  - No Chef attribute variable is used.
  - Hardcoded password literal: `fastapi_password`
  - Embedded connection string: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in an `execute` resource and in the generated `.env` file
- **Usage context**:
  - Sets the password for PostgreSQL user `fastapi`.
  - Authenticates the application to database `fastapi_db`.

### PostgreSQL connection string

- **Variable(s)**:
  - `DATABASE_URL`
  - Value: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Plaintext in `/opt/fastapi-tutorial/.env`
- **Usage context**: Application database connection configuration
- **Migration handling**:
  - Store the password and connection string components in Ansible Vault or an approved AAP-managed secret.
  - Render the `.env` file without exposing the secret in task output.
  - Consider changing the file mode from `0644` to `0600`; this is a security improvement and a behavior change from the cookbook.

No Chef data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, HashiCorp Vault, AWS Secrets Manager, environment-variable lookups, certificate files, private keys, API keys, or tokens were detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- `/var/lib/pgsql/data/` on RHEL/Fedora
- The distribution-managed PostgreSQL data directory on non-RHEL/Fedora systems
- Application repository contents under `/opt/fastapi-tutorial`
- PostgreSQL journal or distribution-managed PostgreSQL logs

**Service endpoints to check**:

- **fastapi-tutorial**: `0.0.0.0:8000`
- **PostgreSQL**: `localhost:5432`
- **PostgreSQL Unix socket**: distribution-managed local socket, if enabled

**Templates rendered**:

- None; the cookbook uses direct `file` resources.
- `/opt/fastapi-tutorial/.env`: written once by a `file` resource
- `/etc/systemd/system/fastapi-tutorial.service`: written once by a `file` resource

## Pre-flight checks

### Platform and package checks

```bash
cat /etc/os-release

python3 --version
python3 -m pip --version
git --version
psql --version
```

### fastapi-tutorial instance checks

```bash
test -d /opt/fastapi-tutorial
stat -c '%A %U:%G %n' /opt/fastapi-tutorial

git -C /opt/fastapi-tutorial status
git -C /opt/fastapi-tutorial branch --show-current
git -C /opt/fastapi-tutorial rev-parse HEAD

test -f /opt/fastapi-tutorial/requirements.txt
test -f /opt/fastapi-tutorial/app/main.py

test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn

/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip list
/opt/fastapi-tutorial/venv/bin/pip check

test -f /opt/fastapi-tutorial/.env
stat -c '%A %U:%G %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION)=' /opt/fastapi-tutorial/.env
sed 's#://[^:]*:[^@]*@#://<redacted>:<redacted>@#' /opt/fastapi-tutorial/.env

test -f /etc/systemd/system/fastapi-tutorial.service
systemctl daemon-reload
systemctl cat fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl status fastapi-tutorial --no-pager

ps aux | grep '[u]vicorn'
ss -tlnp | grep ':8000'
curl -I http://127.0.0.1:8000/
curl -sS http://127.0.0.1:8000/

journalctl -u fastapi-tutorial --no-pager -n 100
systemctl show fastapi-tutorial -p ActiveState -p SubState -p ExecMainStatus
```

Expected application command:

```text
/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### PostgreSQL instance checks

```bash
systemctl is-enabled postgresql
systemctl is-active postgresql
systemctl status postgresql --no-pager

sudo -u postgres psql -c "SELECT version();"

sudo -u postgres psql -tAc \
  "SELECT usename FROM pg_catalog.pg_user WHERE usename = 'fastapi';"

sudo -u postgres psql -tAc \
  "SELECT datname FROM pg_database WHERE datname = 'fastapi_db';"

sudo -u postgres psql -tAc \
  "SELECT pg_catalog.pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"

PGPASSWORD='<retrieve-from-approved-secret-source>' \
  psql -h localhost -U fastapi -d fastapi_db -c "SELECT version();"

PGPASSWORD='<retrieve-from-approved-secret-source>' \
  psql -h localhost -U fastapi -d fastapi_db \
  -c "SELECT current_database(), current_user;"

journalctl -u postgresql --no-pager -n 100
```

On RHEL/Fedora systems, also verify PostgreSQL initialization:

```bash
test -f /var/lib/pgsql/data/PG_VERSION
ls -lah /var/lib/pgsql/data/
```

On non-RHEL/Fedora systems, verify the distribution-managed PostgreSQL data directory and local database access:

```bash
sudo -u postgres psql -c "SELECT version();"
```

### Service failure and restart checks

```bash
systemctl --failed
systemctl status fastapi-tutorial --no-pager
systemctl status postgresql --no-pager
```

Because the `fastapi-tutorial` unit specifies `Restart=always`, systemd should attempt to restart the application after a stop or crash.