---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI Tutorial application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` under `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, and PostgreSQL development packages; creates a Python virtual environment; installs application dependencies; creates the PostgreSQL user `fastapi` and database `fastapi_db`; generates an environment file containing a hardcoded database password; and runs the application as the `fastapi-tutorial.service` systemd unit on port `8000`. The cookbook configures one application instance, `fastapi-tutorial`, and one PostgreSQL service instance, `postgresql`.

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
  - systemd unit: `fastapi-tutorial.service`
  - Environment file: `/opt/fastapi-tutorial/.env`
  - Restart policy: `Restart=always`
  - Key configuration: Uvicorn listens on all interfaces; the virtual environment is placed first in `PATH`; the service starts after `network.target` and `postgresql.service`.

- **postgresql**: PostgreSQL database service
  - Service name: `postgresql`
  - Database user: `fastapi`
  - Database name: `fastapi_db`
  - Database owner: `fastapi`
  - Location/Path: Platform-default PostgreSQL data directory
  - Port/Socket: `localhost:5432`; the cookbook does not explicitly configure a port or Unix socket
  - Key configuration: The service is enabled and started. User `fastapi` is created with ownership and privileges on database `fastapi_db`.

## File Structure

Only the recipe file shown in the execution tree is used by this cookbook.

**Recipes:**

```text
recipes/default.rb
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

The `.env` file and systemd unit are generated with inline Chef `file` resources. They are not static cookbook files.

## Module Explanation

The cookbook performs operations in this order. It contains one recipe and has no `include_recipe` calls.

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs platform-specific system packages.
   - On Fedora/RHEL, installs `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, and `libpq-devel`, then runs `postgresql-setup --initdb` when `/var/lib/pgsql/data/PG_VERSION` does not exist.
   - On non-Fedora/RHEL platforms, installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Creates `/opt/fastapi-tutorial` with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` into `/opt/fastapi-tutorial` at revision `main`.
   - Expects `/opt/fastapi-tutorial/requirements.txt` and the application module `app.main:app` to be provided by the repository.
   - Creates `/opt/fastapi-tutorial/venv` with:
     ```bash
     python3 -m venv /opt/fastapi-tutorial/venv
     ```
     The command is guarded so the virtual environment is not recreated when the directory exists.
   - Installs Python dependencies from `/opt/fastapi-tutorial/requirements.txt` using `/opt/fastapi-tutorial/venv/bin/pip`.
   - Enables and starts the `postgresql` service.
   - Creates PostgreSQL user `fastapi` with password `fastapi_password`.
   - Creates database `fastapi_db` owned by `fastapi`.
   - Grants all privileges on `fastapi_db` to `fastapi`.
   - Implements database creation idempotently in Ansible using PostgreSQL modules or explicit existence checks rather than reproducing the Chef `|| true` error suppression.
   - Creates `/opt/fastapi-tutorial/.env` with owner `root`, group `root`, and mode `0644` in the original cookbook:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Migrates the database password to Ansible Vault or an approved external secret manager and generates `DATABASE_URL` from variables. A restrictive mode such as `0600` should be used unless broader access is explicitly required.
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
   - Notifies `execute[systemd_reload]` when the systemd unit changes.
   - Reloads systemd with:
     ```bash
     systemctl daemon-reload
     ```
     The reload runs only when notified.
   - Enables and starts `fastapi-tutorial.service`.
   - Iterations: None. The recipe contains no `.each` loops or iterable instance collections.
   - Common execution resources: one `directory`, one `git`, four `execute` resources (`create_venv`, `install_dependencies`, `create_db_user`, and `systemd_reload`), two `service` resources (`postgresql` and `fastapi-tutorial`), and two inline `file` resources (`.env` and the systemd unit). Fedora/RHEL additionally uses one package resource and one PostgreSQL initialization execute resource.

## Dependencies

**External cookbook dependencies**: None declared in the analyzed metadata.

**Supported operating systems**:
- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**System package dependencies**:

- Fedora/RHEL:
  - `python3`
  - `python3-pip`
  - `git`
  - `postgresql-server`
  - `postgresql-contrib`
  - `libpq-devel`
- Non-Fedora/RHEL:
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

**Application dependency source**: `/opt/fastapi-tutorial/requirements.txt`

**Python dependency installation target**: `/opt/fastapi-tutorial/venv`

## Credentials

**Detection Summary**: One hardcoded database credential was detected in one recipe file. The credential is used in both the PostgreSQL creation command and the generated `.env` file. The database connection string is also hardcoded in the generated environment file.

**Source**:
- **Provider**: Hardcoded in the Chef recipe
- **URL**: None
- **Path**: None
- **Secret value detected**: `fastapi_password`

### PostgreSQL database password

- **Variable(s)**:
  - PostgreSQL password for user `fastapi`
  - Password component of `DATABASE_URL`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded
- **Usage context**:
  - PostgreSQL command:
    ```bash
    CREATE USER fastapi WITH PASSWORD 'fastapi_password';
    ```
  - Application connection string:
    ```text
    DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
    ```
- **Migration requirement**: Store the password in Ansible Vault or an approved external secret manager. Do not place it in a normal variables file, expose it in task output, include it in visible command arguments, or commit it to source control.

### Database connection string

- **Variable**: `DATABASE_URL`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in generated `.env` content
- **Usage context**: Application PostgreSQL connection configuration
- **Embedded values**:
  - Username: `fastapi`
  - Password: `fastapi_password`
  - Host: `localhost`
  - Database: `fastapi_db`
- **Migration requirement**: Generate the connection string from vaulted or externally managed variables.

No Chef data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, Vault attributes, environment-variable lookups, TLS certificate references, or API tokens were detected.

## Checks for the Migration

**Files to verify**:
- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Database objects to verify**:
- PostgreSQL role `fastapi`
- PostgreSQL database `fastapi_db`
- Owner `fastapi`
- Privilege grant for `fastapi` on `fastapi_db`

**Service endpoints to check**:
- FastAPI: `0.0.0.0:8000`
- PostgreSQL: `localhost:5432`
- No cookbook-managed Unix socket path; any socket is platform default.

**Templates rendered**: None

**Inline files generated**:
- `/opt/fastapi-tutorial/.env`: rendered once
- `/etc/systemd/system/fastapi-tutorial.service`: rendered once

## Pre-flight checks:

```bash
# Platform and package checks
python3 --version
python3 -m pip --version
git --version

# Fedora/RHEL package checks
rpm -q postgresql-server
rpm -q postgresql-contrib
rpm -q libpq-devel

# Non-Fedora/RHEL package checks
dpkg -s postgresql
dpkg -s postgresql-contrib
dpkg -s libpq-dev
dpkg -s python3-venv

# Application instance: fastapi-tutorial
stat -c '%A %U:%G %n' /opt/fastapi-tutorial
git -C /opt/fastapi-tutorial status
git -C /opt/fastapi-tutorial branch --show-current
test -f /opt/fastapi-tutorial/requirements.txt
test -d /opt/fastapi-tutorial/venv
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip list
/opt/fastapi-tutorial/venv/bin/python -c "import fastapi; print(fastapi.__version__)"
/opt/fastapi-tutorial/venv/bin/python -c "import uvicorn; print(uvicorn.__version__)"

# PostgreSQL instance: postgresql
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
sudo -u postgres pg_isready
sudo -u postgres psql -tAc "SELECT usename FROM pg_user WHERE usename = 'fastapi';"
sudo -u postgres psql -tAc "SELECT datname, pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"
sudo -u postgres psql -tAc "\l+ fastapi_db"
PGPASSWORD='<vault-supplied-password>' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT version();"
ss -tlnp | grep ':5432'

# Environment file
stat -c '%A %U:%G %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION)=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env \
  | sed -E 's#(postgresql://[^:]+:)[^@]+#\1REDACTED#'

# systemd unit
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
grep -E '^(Description|After|Type|User|WorkingDirectory|Environment|ExecStart|Restart|WantedBy)=' \
  /etc/systemd/system/fastapi-tutorial.service
systemctl daemon-reload
systemctl cat fastapi-tutorial.service

# FastAPI service instance: fastapi-tutorial
systemctl status fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
ps aux | grep '[u]vicorn app.main:app'
curl -i http://127.0.0.1:8000/
ss -tlnp | grep ':8000'

# Logs
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u postgresql --no-pager -n 100

# Restart behavior
systemctl restart fastapi-tutorial
systemctl is-active fastapi-tutorial
curl -i http://127.0.0.1:8000/
systemctl show fastapi-tutorial --property=LoadState,ActiveState,SubState
```

The repository must be checked out at revision `main`. The expected final FastAPI service state is `LoadState=loaded`, `ActiveState=active`, and `SubState=running`.