---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI Tutorial application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` under `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, and platform-specific development dependencies; creates a Python virtual environment; installs application requirements; initializes and configures PostgreSQL with database `fastapi_db` and user `fastapi`; writes the application `.env` file; and manages the `fastapi-tutorial.service` systemd unit listening on `0.0.0.0:8000`. The cookbook supports Debian/Ubuntu and RHEL/Fedora package layouts.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application served by Uvicorn
  - Location/Path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Python virtual environment: `/opt/fastapi-tutorial/venv`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Service user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Start command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Listening address: `0.0.0.0`
  - Port: `8000`
  - Restart policy: `Restart=always`
  - Database: `fastapi_db`
  - Database user: `fastapi`
  - Database host: `localhost`

- **postgresql**: Local PostgreSQL database service
  - Service name: `postgresql`
  - Port: `5432` by default
  - Enabled at boot: Yes
  - Started by Chef: Yes
  - Database: `fastapi_db`
  - Database owner: `fastapi`
  - Database user: `fastapi`
  - Database password: `fastapi_password`

The cookbook has no collection attributes and no `.each` iterations.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

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

No ERB templates are rendered. The `.env` file and systemd unit are created using inline `file` resources.

**Attributes:**
```text
cookbooks/fastapi-tutorial/attributes/default.rb
```

**Files:**
```text
```

No static files are deployed by `cookbook_file` or `remote_file`.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Reads the attributes from `cookbooks/fastapi-tutorial/attributes/default.rb`:
     - `node['fastapi_tutorial']['app_path']`: `/opt/fastapi-tutorial`
     - `node['fastapi_tutorial']['repository']`: `https://github.com/dibanez/fastapi_tutorial.git`
     - `node['fastapi_tutorial']['revision']`: `main`
     - `node['fastapi_tutorial']['service_port']`: `8000`
   - On RHEL/Fedora platforms, installs `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, and `libpq-devel`.
   - On non-RHEL/Fedora platforms, installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - On RHEL/Fedora platforms, runs `execute[initialize_postgresql]` with `postgresql-setup --initdb` when `/var/lib/pgsql/data/PG_VERSION` does not exist.
   - Creates `/opt/fastapi-tutorial` using `directory[node['fastapi_tutorial']['app_path']]` with owner `root`, group `root`, mode `0755`, and recursive creation enabled.
   - Synchronizes the Git repository using `git[node['fastapi_tutorial']['app_path']]`:
     - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
     - Revision: `main`
     - Action: `sync`
   - Creates `/opt/fastapi-tutorial/venv` with `execute[create_venv]` using `python3 -m venv /opt/fastapi-tutorial/venv`.
   - Guards virtual-environment creation with `/opt/fastapi-tutorial/venv`.
   - Installs `/opt/fastapi-tutorial/requirements.txt` with `execute[install_dependencies]` using `/opt/fastapi-tutorial/venv/bin/pip`.
   - Runs dependency installation from `/opt/fastapi-tutorial` without a `creates` guard.
   - Enables and starts `service[postgresql]`.
   - Runs `execute[create_db_user]` as the PostgreSQL system user with the following commands:
     - Creates PostgreSQL user `fastapi` with password `fastapi_password`.
     - Creates database `fastapi_db` owned by `fastapi`.
     - Grants all privileges on `fastapi_db` to `fastapi`.
   - Uses `|| true` on the PostgreSQL commands, allowing existing objects and other command errors to be ignored.
   - Creates `/opt/fastapi-tutorial/.env` with `file[#{node['fastapi_tutorial']['app_path']}/.env]`, owned by `root:root` with mode `0644`.
   - Writes `PROJECT_NAME="FastAPI Tutorial"`, `API_VERSION=1.0.0`, and `DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db` to the `.env` file.
   - Creates `/etc/systemd/system/fastapi-tutorial.service` using `file[/etc/systemd/system/#{service_name}.service]`.
   - Configures the `fastapi-tutorial.service` unit to run as `root`, use `/opt/fastapi-tutorial` as its working directory, execute Uvicorn on `0.0.0.0:8000`, restart always, and start after `network.target` and `postgresql.service`.
   - Notifies `execute[systemd_reload]` immediately when the systemd unit changes.
   - Runs `execute[systemd_reload]` with `systemctl daemon-reload` only when notified.
   - Enables and starts `service[service_name]`, resolving to `service[fastapi-tutorial]`.
   - Does not explicitly restart the application when repository content, dependencies, or `.env` content changes.

**Expanded iterations**: None. No `.each` loops are present.

## Dependencies

**External cookbook dependencies**: None listed in `metadata.rb`.

**System package dependencies**:

RHEL/Fedora:
- `python3`
- `python3-pip`
- `git`
- `postgresql-server`
- `postgresql-contrib`
- `libpq-devel`

Debian/Ubuntu and other non-RHEL/Fedora systems:
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
- `/opt/fastapi-tutorial/requirements.txt`

## Credentials

**Detection Summary**: 1 database credential detected in `cookbooks/fastapi-tutorial/recipes/default.rb`. The credential is used in the PostgreSQL user creation command and the generated `.env` file.

**Source**:
- **Provider**: Hardcoded in the Chef recipe
- **URL**: None detected
- **Path**: None detected

### PostgreSQL application password

- **Variable(s)**:
  - No Chef attribute variable
  - Literal password: `fastapi_password`
  - Connection string: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Plaintext in an `execute` resource and an inline `.env` file
- **Usage context**:
  - Password for PostgreSQL user `fastapi`
  - Database connection for the FastAPI application
  - Written to `/opt/fastapi-tutorial/.env`

No Chef data bag, Chef Vault, Conjur, CyberArk, environment-variable secret reference, TLS certificate, private key, API token, or external secret-manager endpoint was detected.

The Ansible migration should store the password in Ansible Vault or an AAP credential and use the protected value when creating the PostgreSQL user and rendering `DATABASE_URL`.

## Checks for the Migration

**Files to verify**:
- `cookbooks/fastapi-tutorial/attributes/default.rb`
- `cookbooks/fastapi-tutorial/recipes/default.rb`
- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/app/main.py`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/venv/bin/pip`
- `/opt/fastapi-tutorial/venv/bin/uvicorn`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- `/var/lib/pgsql/data/PG_VERSION` on RHEL/Fedora systems

**Service endpoints to check**:
- FastAPI: `http://127.0.0.1:8000`
- FastAPI listener: `0.0.0.0:8000`
- PostgreSQL host: `localhost`
- PostgreSQL port: `5432`
- PostgreSQL local Unix socket: platform-dependent and not explicitly configured

**Database objects to verify**:
- PostgreSQL role `fastapi`
- PostgreSQL database `fastapi_db`
- Database owner `fastapi`
- All privileges on `fastapi_db` granted to `fastapi`

**Templates rendered**:
- None; 0 ERB templates
- Inline file `/opt/fastapi-tutorial/.env`: 1 file
- Inline file `/etc/systemd/system/fastapi-tutorial.service`: 1 file

## Pre-flight checks

```bash
# Verify cookbook attribute definitions
grep -nE 'app_path|repository|revision|service_port' \
  cookbooks/fastapi-tutorial/attributes/default.rb

# Verify cookbook recipe
test -f cookbooks/fastapi-tutorial/recipes/default.rb
```

### fastapi-tutorial instance

```bash
# Verify application directory and repository
ls -ld /opt/fastapi-tutorial
git -C /opt/fastapi-tutorial status --short
git -C /opt/fastapi-tutorial branch --show-current
test -f /opt/fastapi-tutorial/requirements.txt
test -f /opt/fastapi-tutorial/app/main.py

# Verify virtual environment and executables
test -d /opt/fastapi-tutorial/venv
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn
/opt/fastapi-tutorial/venv/bin/pip check
/opt/fastapi-tutorial/venv/bin/uvicorn --version

# Verify application import
cd /opt/fastapi-tutorial
/opt/fastapi-tutorial/venv/bin/python -c "from app.main import app; print(app)"

# Verify environment file without exposing its contents
stat -c '%U %G %a %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' /opt/fastapi-tutorial/.env

# Verify systemd unit
test -f /etc/systemd/system/fastapi-tutorial.service
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl daemon-reload
systemctl is-enabled fastapi-tutorial.service
systemctl is-active fastapi-tutorial.service
systemctl status fastapi-tutorial.service --no-pager

# Verify service process and port
ps aux | grep '[u]vicorn app.main:app'
ss -tlnp | grep ':8000'

# Verify HTTP response
curl -i http://127.0.0.1:8000/
curl -sS http://127.0.0.1:8000/ | head -c 1000
```

Expected application settings:
- Working directory: `/opt/fastapi-tutorial`
- User: `root`
- Host: `0.0.0.0`
- Port: `8000`
- Restart policy: `always`

### postgresql instance

```bash
# Verify package installation
systemctl is-enabled postgresql
systemctl is-active postgresql
systemctl status postgresql --no-pager

# RHEL/Fedora initialization check
test -f /var/lib/pgsql/data/PG_VERSION

# Debian/Ubuntu package check
dpkg -s python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

# RHEL/Fedora package check
rpm -q python3 python3-pip git postgresql-server postgresql-contrib libpq-devel

# Verify PostgreSQL role
sudo -u postgres psql -tAc \
  "SELECT 1 FROM pg_roles WHERE rolname='fastapi';"

# Verify PostgreSQL database and owner
sudo -u postgres psql -tAc \
  "SELECT 1 FROM pg_database WHERE datname='fastapi_db';"
sudo -u postgres psql -tAc \
  "SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname='fastapi_db';"

# Verify application credentials and connectivity
PGPASSWORD='[retrieve from Ansible Vault or AAP credential]' \
psql -h localhost -U fastapi -d fastapi_db -c \
  "SELECT current_database(), current_user;"
```

Expected PostgreSQL values:
- Service: `postgresql`
- Database: `fastapi_db`
- User: `fastapi`
- Owner: `fastapi`
- Port: `5432`

### Logs and connectivity

```bash
# FastAPI logs
journalctl -u fastapi-tutorial.service --no-pager -n 100

# PostgreSQL logs
journalctl -u postgresql --no-pager -n 100

# Follow application logs during an HTTP request
journalctl -u fastapi-tutorial.service -f

# Verify database URL key without printing the complete .env file
grep -E '^DATABASE_URL=' /opt/fastapi-tutorial/.env
```

Check for missing Python modules, application import failures, database authentication errors, port `8000` binding errors, PostgreSQL startup failures, and permission errors involving `/opt/fastapi-tutorial` or `/opt/fastapi-tutorial/.env`.