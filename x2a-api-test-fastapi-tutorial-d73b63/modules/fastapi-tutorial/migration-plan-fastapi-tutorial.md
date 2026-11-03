---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook installs the system dependencies for a FastAPI application, clones the `main` branch of `https://github.com/dibanez/fastapi_tutorial.git` into `/opt/fastapi-tutorial`, creates a Python virtual environment, installs the repository requirements, enables and starts PostgreSQL, creates the `fastapi` PostgreSQL user and `fastapi_db` database, writes an environment file containing the database connection string, and manages a systemd service listening on `0.0.0.0:8000`. The application runs as `root`, and the database password is hardcoded in the Chef recipe.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application server
  - Location/Path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Git revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Port/Socket: `0.0.0.0:8000`
  - Application command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Run user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Restart policy: `Restart=always`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Environment path: `/opt/fastapi-tutorial/venv/bin`

- **postgresql**: PostgreSQL database service
  - Location/Path: Platform-specific PostgreSQL data directory
  - Port/Socket: `localhost`; port is not explicitly configured and must be verified from the active PostgreSQL configuration
  - Service actions: enabled and started
  - Database user: `fastapi`
  - Database: `fastapi_db`
  - Database owner: `fastapi`
  - Connection URL: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`

No Chef collection attributes or `.each` iterations are present. There are no repeated application instances or site collections to expand.

## File Structure

Only the files shown in the execution tree and directory listing are included.

```text
cookbooks/fastapi-tutorial/
└── recipes/
    └── default.rb
```

**Recipes:**
```text
recipes/default.rb
```

**Providers:**

No provider files are used.

**Templates:**

No Chef templates are rendered. The `.env` file and systemd unit are generated directly with `file` resources.

**Attributes:**

No attribute files are listed or used.

**Files:**

No static files from `files/default/*` or `files/*` are deployed.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the seven system packages `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates the virtual environment with `python3 -m venv /opt/fastapi-tutorial/venv`, guarded by `creates: /opt/fastapi-tutorial/venv`.
   - Installs Python dependencies with `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt` from working directory `/opt/fastapi-tutorial`.
   - Enables and starts the generic `postgresql` service.
   - Runs PostgreSQL commands as the `postgres` administrative user to create role `fastapi`, database `fastapi_db`, and grant all privileges on `fastapi_db` to `fastapi`.
   - Writes `/opt/fastapi-tutorial/.env` with owner `root`, group `root`, and mode `0644`.
   - Writes `/etc/systemd/system/fastapi-tutorial.service` with owner `root`, group `root`, and mode `0644`.
   - The systemd unit starts after `network.target` and `postgresql.service`, runs Uvicorn as `root`, uses `/opt/fastapi-tutorial` as its working directory, and listens on `0.0.0.0:8000`.
   - Reloads systemd through `execute[systemd_reload]` only when the systemd unit file changes; the reload command is declared with action `nothing` and notified immediately by the file resource.
   - Enables and starts the `fastapi-tutorial` service.
   - Resources used, in execution order:
     - `package` resource containing seven package names
     - `directory[/opt/fastapi-tutorial]`
     - `git[/opt/fastapi-tutorial]`
     - `execute[create_venv]`
     - `execute[install_dependencies]`
     - `service[postgresql]`
     - `execute[create_db_user]`
     - `file[/opt/fastapi-tutorial/.env]`
     - `file[/etc/systemd/system/fastapi-tutorial.service]`
     - `execute[systemd_reload]`
     - `service[fastapi-tutorial]`
   - No separate `group[root]` resources are used; `root` is specified as the owner and group on applicable resources.

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

**Application dependency source**: `/opt/fastapi-tutorial/requirements.txt`, supplied by the cloned Git repository.

## Credentials

**Detection Summary**: 1 hardcoded database credential detected across 2 recipe contexts.

**Source**:
  - **Provider**: Hardcoded in the Chef recipe
  - **URL**: None
  - **Path**: None
  - **Secret stores**: No data bag, Chef Vault, CyberArk, Conjur, or external secret manager usage detected

### PostgreSQL password

- **Variable(s)**: Password literal `fastapi_password`; connection variable `DATABASE_URL`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`, PostgreSQL creation command
  - `cookbooks/fastapi-tutorial/recipes/default.rb`, `.env` content
- **Current storage**: Hardcoded in the recipe and generated environment file
- **Usage context**:
  - Creates PostgreSQL user `fastapi`
  - Connects the application to database `fastapi_db`
  - Appears in `DATABASE_URL`
- **Sensitive values and locations**:
  - `CREATE USER fastapi WITH PASSWORD 'fastapi_password';`
  - `DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db`

The Ansible implementation should store the password in Ansible Vault and use the vaulted variable both when creating the PostgreSQL user and when rendering `/opt/fastapi-tutorial/.env`. No TLS certificate or private-key references were detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv/`
- `/opt/fastapi-tutorial/`
- `/etc/systemd/system/`

**Service endpoints to check**:

- FastAPI HTTP endpoint: `0.0.0.0:8000`
- PostgreSQL connection endpoint: `localhost` on the active PostgreSQL default port

**Templates rendered**:

- No `.erb` templates rendered: `0`
- Direct files created:
  - `/opt/fastapi-tutorial/.env`: `1`
  - `/etc/systemd/system/fastapi-tutorial.service`: `1`

## Pre-flight checks

### FastAPI application instance: `fastapi-tutorial`

```bash
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev
ls -ld /opt/fastapi-tutorial
ls -ld /opt/fastapi-tutorial/venv
test -f /opt/fastapi-tutorial/requirements.txt

git -C /opt/fastapi-tutorial remote -v
git -C /opt/fastapi-tutorial branch --show-current
git -C /opt/fastapi-tutorial rev-parse --verify HEAD

test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip check

stat -c '%U:%G %a %n' /opt/fastapi-tutorial/.env
grep '^PROJECT_NAME=' /opt/fastapi-tutorial/.env
grep '^API_VERSION=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env

systemctl daemon-reload
systemctl status fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl cat fastapi-tutorial
systemctl show fastapi-tutorial --property=User,WorkingDirectory,ExecStart,Restart

curl -i http://127.0.0.1:8000/
ss -tlnp | grep ':8000'
lsof -iTCP:8000 -sTCP:LISTEN

journalctl -u fastapi-tutorial --no-pager -n 100
ps aux | grep '[u]vicorn'
systemctl show fastapi-tutorial --property=MainPID
```

Verify the service contains:

```text
User=root
WorkingDirectory=/opt/fastapi-tutorial
ExecStart=/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
```

Confirm the process uses `/opt/fastapi-tutorial/venv/bin/uvicorn`, starts `app.main:app`, and listens on `0.0.0.0:8000`.

### PostgreSQL instance: `postgresql`

```bash
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
journalctl -u postgresql --no-pager -n 100

sudo -u postgres psql -tAc "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"
sudo -u postgres psql -tAc "SELECT datname, pg_catalog.pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"
sudo -u postgres psql -d fastapi_db -c "SELECT current_database(), current_user;"
```

Expected results:

- PostgreSQL role `fastapi` exists.
- Database `fastapi_db` exists.
- `fastapi_db` is owned by `fastapi`.
- A connection query completes successfully.

Verify the application credentials without exposing the password in shell history:

```bash
PGPASSWORD='<retrieve-from-secure-secret-store>' \
psql -h localhost -U fastapi -d fastapi_db -c "SELECT 1;"

PGPASSWORD='<retrieve-from-secure-secret-store>' \
psql -h localhost -U fastapi -d fastapi_db -c "SELECT version();"
```

Verify the active PostgreSQL port from the target system configuration because the cookbook does not specify a port.

### Platform and configuration checks

```bash
# On Debian or Ubuntu:
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

# On CentOS or another RPM-based system:
rpm -q python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

# Verify the application dependency installation:
 /opt/fastapi-tutorial/venv/bin/pip freeze

# Verify the application process command line:
cat /proc/"$(systemctl show -p MainPID --value fastapi-tutorial)"/cmdline | tr '\0' ' '
```

Check logs for Uvicorn startup errors, Python import errors involving `app.main:app`, missing dependencies, PostgreSQL connection failures, and permission errors. Do not print the complete `.env` file in production diagnostics because it contains the database password.