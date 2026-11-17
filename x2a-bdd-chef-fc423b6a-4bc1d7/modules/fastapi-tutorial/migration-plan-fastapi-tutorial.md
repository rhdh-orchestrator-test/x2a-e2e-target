---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI tutorial application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, PostgreSQL development libraries, and application dependencies; initializes and starts PostgreSQL; creates the `fastapi` PostgreSQL role and `fastapi_db` database; writes an environment file containing the database connection string; and manages a systemd service named `fastapi-tutorial` listening on port `8000`. The cookbook contains one entry recipe, no collection iterations, no custom resources, no templates, and one hardcoded database credential. Resource properties and attribute values should be confirmed against the source files during migration review.

## Service Type and Instances

**Service Type**: Application Server with PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application served by Uvicorn
  - Location/Path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Dependency file: `/opt/fastapi-tutorial/requirements.txt`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Service user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Executable: `/opt/fastapi-tutorial/venv/bin/uvicorn`
  - Application target: `app.main:app`
  - Port/Socket: `0.0.0.0:8000`
  - Restart policy: `always`
  - Startup dependencies: `network.target` and `postgresql.service`

- **postgresql**: Local PostgreSQL database service used by the FastAPI application
  - Service name: `postgresql`
  - Database role: `fastapi`
  - Database name: `fastapi_db`
  - Database owner: `fastapi`
  - Database password: `fastapi_password`
  - Connection host: `localhost`
  - Port/Socket: Platform default, normally TCP port `5432` and the local PostgreSQL Unix socket
  - Connection string: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`

No `.each` loops or collection iterations are present. The cookbook configures exactly one FastAPI service and one PostgreSQL service.

## File Structure

Only files used by the cookbook are listed below.

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

No ERB templates are rendered. Configuration is written using inline Chef `file` resources.

**Attributes:**
```text
cookbooks/fastapi-tutorial/attributes/default.rb
```

**Files:**
```text
```

No static files from `files/` are deployed.

## Module Explanation

The cookbook performs operations in the following order. The resource sequence is consistent with the supplied execution analysis. Attribute values, resource properties, and the systemd notification relationship should be confirmed against `cookbooks/fastapi-tutorial/recipes/default.rb` and `cookbooks/fastapi-tutorial/attributes/default.rb`.

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Detects whether the platform family is Fedora or RHEL.
   - On Fedora/RHEL, installs `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, and `libpq-devel`.
   - On other supported platforms, installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - The two package lists are conditional alternatives, not cumulative installations.
   - On Fedora/RHEL, runs `postgresql-setup --initdb` through `execute[initialize_postgresql]` when `/var/lib/pgsql/data/PG_VERSION` does not exist.
   - Creates `/opt/fastapi-tutorial` with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates `/opt/fastapi-tutorial/venv` with:
     ```bash
     python3 -m venv /opt/fastapi-tutorial/venv
     ```
   - Installs Python dependencies from `/opt/fastapi-tutorial/requirements.txt` using `/opt/fastapi-tutorial/venv/bin/pip`.
   - Starts and enables the `postgresql` service.
   - Creates the PostgreSQL role `fastapi` with password `fastapi_password`.
   - Creates the `fastapi_db` database owned by `fastapi`.
   - Grants all privileges on `fastapi_db` to `fastapi`.
   - The original Chef implementation uses `|| true` for the database commands. The Ansible migration should use idempotent PostgreSQL modules instead.
   - Writes `/opt/fastapi-tutorial/.env` with:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Sets the `.env` owner and group to `root` and mode to `0644`; Ansible Vault and mode `0600` are recommended for the migrated credential.
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
   - Sets the systemd unit owner and group to `root` and mode to `0644`.
   - Runs `systemctl daemon-reload` through `execute[systemd_reload]`, whose default action is `nothing`.
   - The original plan states that changes to the systemd unit immediately notify `execute[systemd_reload]`; this notification relationship requires confirmation in the recipe source.
   - Enables and starts the `fastapi-tutorial` service.
   - The recipe uses no `.each` loops, custom resources, or templates.

### Attribute values

The attributes file is:

```text
cookbooks/fastapi-tutorial/attributes/default.rb
```

The listed defaults are:

- `node['fastapi_tutorial']['app_path']`: `/opt/fastapi-tutorial`
- `node['fastapi_tutorial']['repository']`: `https://github.com/dibanez/fastapi_tutorial.git`
- `node['fastapi_tutorial']['revision']`: `main`
- `node['fastapi_tutorial']['service_port']`: `8000`

These are scalar attributes. No hash or list attributes are iterated by the recipe. The presence and exact values of all four attributes should be confirmed against the attributes file before migration sign-off.

## Dependencies

**External cookbook dependencies**: None listed in `metadata.rb`.

**System package dependencies**:

- **Fedora/RHEL**:
  - `python3`
  - `python3-pip`
  - `git`
  - `postgresql-server`
  - `postgresql-contrib`
  - `libpq-devel`
- **Other supported platforms**:
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

**Supported platforms from metadata**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

The recipe uses Fedora/RHEL detection for the package and PostgreSQL initialization branches. The Ansible role must map the supported operating systems to the appropriate package lists and initialization behavior.

## Credentials

**Detection Summary**: 1 database credential detected across 1 source recipe and written into the generated `.env` file.

**Source**:
  - **Provider**: Hardcoded in the Chef recipe
  - **URL**: None
  - **Path**: None

### FastAPI PostgreSQL password

- **Variable(s)**: PostgreSQL password literal `fastapi_password`; `DATABASE_URL`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the recipe and embedded in `/opt/fastapi-tutorial/.env`
- **Usage context**:
  - Creates PostgreSQL role `fastapi`
  - Connects through `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
  - Provides the FastAPI application database connection
  - Is written to `/opt/fastapi-tutorial/.env`

No Chef data bags, Chef Vault, Conjur, CyberArk, HashiCorp Vault, AWS Secrets Manager, environment-variable password references, TLS certificate files, or private-key files were detected. Store the migrated PostgreSQL password in Ansible Vault.

## Checks for the Migration

**Files to verify**:

- `cookbooks/fastapi-tutorial/recipes/default.rb`
- `cookbooks/fastapi-tutorial/attributes/default.rb`
- `/opt/fastapi-tutorial/`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv/`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- PostgreSQL data directory:
  - `/var/lib/pgsql/data/` on Fedora/RHEL
  - Distribution-specific PostgreSQL data path on other platforms
- PostgreSQL database `fastapi_db`
- PostgreSQL role `fastapi`

No application log file is explicitly configured. Service output is expected in the systemd journal.

**Service endpoints to check**:

- FastAPI: `0.0.0.0:8000`
- PostgreSQL: TCP `5432`, unless the target distribution changes the default
- PostgreSQL local Unix socket: platform-managed default location

**Templates rendered**: None.

**Inline files created**:

- `/opt/fastapi-tutorial/.env`: 1 file resource
- `/etc/systemd/system/fastapi-tutorial.service`: 1 file resource

## Pre-flight checks:

```bash
# Validate the PostgreSQL instance
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
sudo -u postgres psql -d postgres -c "SELECT version();"
sudo -u postgres psql -d postgres -c "\du fastapi"
sudo -u postgres psql -d postgres -c "\l fastapi_db"
ss -tlnp | grep ':5432' || true
sudo -u postgres psql -d fastapi_db -c "SELECT current_database();"

# Validate the PostgreSQL role and database credentials
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_user, current_database();"

# Validate the FastAPI service instance
systemctl status fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl show fastapi-tutorial --property=ExecMainStatus,ActiveState,SubState
ps aux | grep '[u]vicorn app.main:app'

# Validate the FastAPI listener
ss -tlnp | grep ':8000'
curl -I http://127.0.0.1:8000/
curl -sS http://127.0.0.1:8000/

# Validate the FastAPI application files and virtual environment
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip check
test -f /opt/fastapi-tutorial/requirements.txt
test -f /opt/fastapi-tutorial/app/main.py

# Validate the repository
git -C /opt/fastapi-tutorial remote -v
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD

# Validate application configuration without exposing the password in logs
stat -c '%U %G %a %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' /opt/fastapi-tutorial/.env

# Validate the systemd unit
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl cat fastapi-tutorial
systemctl show fastapi-tutorial \
  --property=User,WorkingDirectory,ExecStart,Environment,Restart

# Validate service logs
journalctl -u postgresql --no-pager -n 50
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u fastapi-tutorial -p err --no-pager
```

Expected results:

- `postgresql` is enabled and active.
- Role `fastapi` and database `fastapi_db` exist, with `fastapi` as the database owner.
- The PostgreSQL credential test succeeds.
- `fastapi-tutorial` is enabled and active.
- Uvicorn runs `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`.
- TCP port `8000` accepts connections.
- The virtual environment exists and `pip check` reports no broken requirements.
- The repository remote is `https://github.com/dibanez/fastapi_tutorial.git` and the checkout uses revision or branch `main`.
- The systemd unit contains:
  - `User=root`
  - `WorkingDirectory=/opt/fastapi-tutorial`
  - `Environment="PATH=/opt/fastapi-tutorial/venv/bin"`
  - `ExecStart=/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - `Restart=always`
  - `After=network.target postgresql.service`
- PostgreSQL and FastAPI logs contain no initialization, permission, database connection, missing-module, import, or repeated-restart errors.