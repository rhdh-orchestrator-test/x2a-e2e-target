---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, and PostgreSQL development dependencies; creates a Python virtual environment; installs application requirements; initializes and starts PostgreSQL; creates the `fastapi` PostgreSQL user and `fastapi_db` database; writes an environment file containing the database connection string; and creates and enables a systemd service named `fastapi-tutorial` listening on `0.0.0.0:8000`.

## Service Type and Instances

**Service Type**: Application Server backed by a PostgreSQL database

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application service
  - Application path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Service user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Startup command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Listening address: `0.0.0.0:8000`
  - Restart policy: `Restart=always`
  - Dependency: `postgresql.service`

- **fastapi**: PostgreSQL application user
  - Password: `fastapi_password`
  - Database privileges: All privileges on `fastapi_db`

- **fastapi_db**: PostgreSQL application database
  - Owner: `fastapi`
  - Connection host: `localhost`
  - Connection URL: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`

There are no collection attributes or `.each` iterations in this cookbook.

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

No ERB templates are used. Configuration files are created using inline Chef `file` resources.

**Attributes:**
```text
cookbooks/fastapi-tutorial/attributes/default.rb
```

**Files:**
```text
```

No static files are deployed with `cookbook_file` or `remote_file`.

## Module Explanation

The cookbook performs operations in this order:

1. **Platform-specific package installation** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - On Fedora/RHEL systems, install `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, and `libpq-devel`.
   - On non-Fedora/RHEL systems, install `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - On Fedora/RHEL systems, run `postgresql-setup --initdb` only when `/var/lib/pgsql/data/PG_VERSION` does not exist.
   - Resources: conditional `package` resources and `execute[initialize_postgresql]`.

2. **Application directory creation** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Create `/opt/fastapi-tutorial` recursively.
   - Set owner and group to `root` and mode to `0755`.
   - Resource: `directory[/opt/fastapi-tutorial]`.

3. **Git repository synchronization** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Synchronize `https://github.com/dibanez/fastapi_tutorial.git`.
   - Check out revision `main` into `/opt/fastapi-tutorial`.
   - Resource: `git[/opt/fastapi-tutorial]`.

4. **Python virtual environment creation** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Run `python3 -m venv /opt/fastapi-tutorial/venv`.
   - Skip execution when `/opt/fastapi-tutorial/venv` already exists.
   - Resource: `execute[create_venv]`.

5. **Python dependency installation** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Install `/opt/fastapi-tutorial/requirements.txt`.
   - Use `/opt/fastapi-tutorial/venv/bin/pip`.
   - Run from `/opt/fastapi-tutorial`.
   - Resource: `execute[install_dependencies]`.

6. **PostgreSQL service enablement and startup** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Enable and start the `postgresql` service.
   - Resource: `service[postgresql]`.
   - Account for versioned PostgreSQL service names on distributions that require them.

7. **PostgreSQL user and database creation** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Create PostgreSQL user `fastapi` with password `fastapi_password`.
   - Create database `fastapi_db` owned by `fastapi`.
   - Grant all privileges on `fastapi_db` to `fastapi`.
   - Original resource: `execute[create_db_user]`, using PostgreSQL commands with `|| true` idempotency handling.
   - Migration should use PostgreSQL-specific Ansible modules where available.
   - This step runs after PostgreSQL starts.

8. **Environment file creation** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Create `/opt/fastapi-tutorial/.env`.
   - Write:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Set owner and group to `root` and mode to `0644`.
   - Resource: `file[/opt/fastapi-tutorial/.env]`.
   - The password should preferably be supplied through Ansible Vault and stored with mode `0600`.

9. **Systemd unit deployment** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Create `/etc/systemd/system/fastapi-tutorial.service`.
   - Configure `User=root`, `WorkingDirectory=/opt/fastapi-tutorial`, `Restart=always`, and `WantedBy=multi-user.target`.
   - Configure `PATH=/opt/fastapi-tutorial/venv/bin`.
   - Run `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`.
   - Start after `network.target` and `postgresql.service`.
   - Set owner and group to `root` and mode to `0644`.
   - Resource: `file[/etc/systemd/system/fastapi-tutorial.service]`.
   - Notify `execute[systemd_reload]` immediately when changed.

10. **Systemd daemon reload** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
    - Run `systemctl daemon-reload`.
    - Resource: `execute[systemd_reload]`.
    - Default action is `nothing`; trigger only when the service unit changes.
    - Migration equivalent: an Ansible handler.

11. **FastAPI service enablement and startup** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
    - Enable and start the `fastapi-tutorial` service.
    - Resource: `service[fastapi-tutorial]`.
    - Run after the unit is installed and systemd has reloaded.

## Dependencies

**External cookbook dependencies**: None listed in `metadata.rb`.

**System package dependencies**:

Fedora/RHEL systems:

- `python3`
- `python3-pip`
- `git`
- `postgresql-server`
- `postgresql-contrib`
- `libpq-devel`

Non-Fedora/RHEL systems:

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

**Runtime dependency relationship**:

- `fastapi-tutorial.service` declares `After=network.target postgresql.service`.
- PostgreSQL must be running before `fastapi-tutorial` starts.

## Credentials

**Detection Summary**: 1 credential detected across 1 file.

**Source**:
  - **Provider**: Hardcoded in the Chef recipe
  - **URL**: None
  - **Path**: None

### PostgreSQL `fastapi` User Password

- **Variable(s)**:
  - No Chef attribute variable is used.
  - Hardcoded password: `fastapi_password`
  - Connection string: `DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the PostgreSQL `execute` resource and inline `.env` file.
- **Usage context**:
  - Creates PostgreSQL user `fastapi`.
  - Authenticates the FastAPI application to `fastapi_db`.
- **Migration guidance**:
  - Store the password in Ansible Vault or an AAP-supported secret mechanism.
  - Use the vaulted value for both PostgreSQL user creation and `/opt/fastapi-tutorial/.env`.
  - Do not commit the literal password to the Ansible repository.

No Chef data bags, encrypted data bags, Chef Vault calls, CyberArk/Conjur integrations, environment-variable lookups, TLS certificate references, or external secret-manager URLs were detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- `/var/lib/pgsql/data/PG_VERSION` on Fedora/RHEL systems

**Service endpoints to check**:

- `fastapi-tutorial`: `0.0.0.0:8000`
- PostgreSQL: `localhost:5432` by default
- PostgreSQL local Unix socket used by `sudo -u postgres psql`

**Database objects to verify**:

- PostgreSQL role: `fastapi`
- PostgreSQL database: `fastapi_db`
- Database owner: `fastapi`
- All privileges on `fastapi_db` granted to `fastapi`

**Templates rendered**:

- No templates are rendered.

**Inline files created**:

- `/opt/fastapi-tutorial/.env` — rendered once by the inline `file` resource
- `/etc/systemd/system/fastapi-tutorial.service` — rendered once by the inline `file` resource

## Pre-flight checks

```bash
# Verify required packages and tools
python3 --version
pip3 --version
git --version

# Verify the PostgreSQL instance
systemctl status postgresql --no-pager
systemctl is-enabled postgresql
systemctl is-active postgresql
sudo -u postgres psql -c "SELECT version();"

# Fedora/RHEL PostgreSQL initialization check
test -f /var/lib/pgsql/data/PG_VERSION

# Verify the fastapi-tutorial application instance
ls -ld /opt/fastapi-tutorial
stat -c '%U:%G %a %n' /opt/fastapi-tutorial
git -C /opt/fastapi-tutorial remote -v
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
test -f /opt/fastapi-tutorial/requirements.txt
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip list
cd /opt/fastapi-tutorial
/opt/fastapi-tutorial/venv/bin/python -c "from app.main import app; print(app)"

# Verify the fastapi PostgreSQL user and fastapi_db database
sudo -u postgres psql -tAc "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"
sudo -u postgres psql -tAc "SELECT datname FROM pg_database WHERE datname = 'fastapi_db';"
sudo -u postgres psql -tAc \
  "SELECT pg_catalog.pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"

# Verify database connectivity for the fastapi user
PGPASSWORD='fastapi_password' psql -h localhost -U fastapi -d fastapi_db \
  -c "SELECT current_user, current_database();"
PGPASSWORD='fastapi_password' psql -h localhost -U fastapi -d fastapi_db \
  -c "SELECT 1;"

# Verify the environment file without exposing the password
test -f /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION)=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env | \
  sed -E 's#://[^:]+:[^@]+@#://<redacted>:<redacted>@#'

# Verify the fastapi-tutorial systemd instance
test -f /etc/systemd/system/fastapi-tutorial.service
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl cat fastapi-tutorial.service
systemctl show fastapi-tutorial \
  -p User -p WorkingDirectory -p ExecStart -p Restart -p After
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl status fastapi-tutorial --no-pager

# Verify the FastAPI process and endpoint
test -x /opt/fastapi-tutorial/venv/bin/uvicorn
test -f /opt/fastapi-tutorial/app/main.py
ps aux | grep '[u]vicorn app.main:app'
ss -tlnp | grep ':8000'
curl -I http://127.0.0.1:8000/
curl -sS http://127.0.0.1:8000/

# Review service logs
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u postgresql --no-pager -n 100
```

Expected application values:

- `PROJECT_NAME="FastAPI Tutorial"`
- `API_VERSION=1.0.0`
- `DATABASE_URL` points to `fastapi_db` on `localhost`
- `fastapi-tutorial` listens on `0.0.0.0:8000`
- `fastapi-tutorial` remains active after startup