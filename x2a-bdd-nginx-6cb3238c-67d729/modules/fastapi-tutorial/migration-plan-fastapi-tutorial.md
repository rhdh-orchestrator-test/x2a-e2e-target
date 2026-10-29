---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` under `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, and PostgreSQL development packages; creates a Python virtual environment; installs application requirements; creates the PostgreSQL role `fastapi` and database `fastapi_db`; writes an environment file containing the database connection string; and manages the `fastapi-tutorial` systemd service listening on port `8000`.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application server
  - Location/Path: `/opt/fastapi-tutorial`
  - Source repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Source revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Port/Socket: `0.0.0.0:8000`
  - Startup command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Runtime user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Restart policy: `always`
  - Key configuration: `app.main:app`, PATH set to `/opt/fastapi-tutorial/venv/bin`, starts after `network.target` and `postgresql.service`

- **postgresql**: PostgreSQL database service
  - Managed service name: `postgresql`
  - Port/Socket: `localhost:5432` expected; the cookbook does not explicitly set the port
  - Database user: `fastapi`
  - Database name: `fastapi_db`
  - Database owner: `fastapi`
  - Key configuration: PostgreSQL must be enabled and started before database initialization

## File Structure

**MANDATORY: Preserve this section from the original plan.**

```text
cookbooks/fastapi-tutorial/
├── recipes/
│   └── default.rb
├── providers/
├── templates/
├── attributes/
└── files/
```

**Recipes:**

```text
cookbooks/fastapi-tutorial/recipes/default.rb
```

**Providers:**

```text
```

No custom resource providers are used.

**Templates:**

```text
```

No Chef templates are rendered. The environment file and systemd unit are created with inline `file` resources.

**Attributes:**

```text
```

No attribute files are listed or used.

**Files:**

```text
```

No static files are deployed with `cookbook_file` or `remote_file`.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the seven system packages: `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates the virtual environment with `python3 -m venv /opt/fastapi-tutorial/venv`, guarded by the existence of `/opt/fastapi-tutorial/venv`.
   - Installs Python dependencies with `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt` from `/opt/fastapi-tutorial`.
   - Enables and starts the `postgresql` service.
   - Creates PostgreSQL role `fastapi` with password `fastapi_password`, database `fastapi_db` owned by `fastapi`, and grants all privileges on `fastapi_db` to `fastapi`.
   - The original database commands use `sudo -u postgres` and `|| true`; the migration should use idempotent PostgreSQL modules instead of suppressing all errors.
   - Writes `/opt/fastapi-tutorial/.env` with mode `0644`, owner `root`, and group `root`:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Writes `/etc/systemd/system/fastapi-tutorial.service` with mode `0644`, owner `root`, and group `root`, containing:
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
   - Defines `execute[systemd_reload]` for `systemctl daemon-reload` with action `:nothing`.
   - Immediately notifies `execute[systemd_reload]` when `/etc/systemd/system/fastapi-tutorial.service` changes.
   - Enables and starts the `fastapi-tutorial` service.
   - Resources used: one `package` resource managing seven packages, one `directory`, one `git`, two `execute` resources, one PostgreSQL service, two inline `file` resources, and one FastAPI service.
   - Iterations: no `.each` loops or collection attributes are used; the configured application instance is `fastapi-tutorial`, and the configured database service is `postgresql`.

## Dependencies

**External cookbook dependencies**: None listed in the supplied metadata or execution tree.

**System package dependencies**:

- `python3`
- `python3-pip`
- `python3-venv`
- `git`
- `postgresql`
- `postgresql-contrib`
- `libpq-dev`

**Application dependency source**: `/opt/fastapi-tutorial/requirements.txt`, installed with `/opt/fastapi-tutorial/venv/bin/pip`

**Service dependencies**:

- `postgresql`
- `fastapi-tutorial`
- `fastapi-tutorial` starts after `network.target` and `postgresql.service`

## Credentials

**Detection Summary**: 1 database credential detected in `cookbooks/fastapi-tutorial/recipes/default.rb`. The credential is used during PostgreSQL initialization and in the application connection string.

**Source**:
  - **Provider**: Hardcoded in the Chef recipe
  - **URL**: None
  - **Path**: None
  - **Secret-management integration**: No data bag, encrypted data bag, Chef Vault, CyberArk, Conjur, or external secret manager usage detected

### PostgreSQL application password

- **Variable(s)**:
  - No named Chef attribute variable
  - Literal password: `fastapi_password`
  - Embedded connection string: `DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the recipe and inline `.env` content
- **Usage context**:
  - Creates PostgreSQL role `fastapi`
  - Authenticates the FastAPI application to database `fastapi_db`
- **Migration recommendation**: Store the password in Ansible Vault and use the vaulted variable both when creating the PostgreSQL role and when rendering `/opt/fastapi-tutorial/.env`. Do not commit the literal password to the role, inventory, or unencrypted variables.

No TLS certificates, private keys, API tokens, environment-based secrets, data bags, or other credential-bearing database connection strings were detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Service endpoints to check**:

- `fastapi-tutorial`: `0.0.0.0:8000`
- `postgresql`: `localhost:5432` if the standard PostgreSQL port is used

**Database objects to verify**:

- PostgreSQL role `fastapi`
- PostgreSQL database `fastapi_db`, owned by `fastapi`

**Templates rendered**:

- None; no `.erb` templates are used
- Inline environment file content: 1 file, `/opt/fastapi-tutorial/.env`
- Inline systemd unit content: 1 file, `/etc/systemd/system/fastapi-tutorial.service`

## Pre-flight checks:

```bash
# Verify installed packages
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

# Verify the fastapi-tutorial application directory
stat -c '%A %U:%G %n' /opt/fastapi-tutorial
git -C /opt/fastapi-tutorial remote -v
git -C /opt/fastapi-tutorial branch --show-current
git -C /opt/fastapi-tutorial rev-parse HEAD
test -f /opt/fastapi-tutorial/requirements.txt

# Verify the fastapi-tutorial virtual environment
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip list

# Verify the postgresql instance
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
ss -tlnp | grep ':5432'

# Verify the postgresql role and database
sudo -u postgres psql -tAc "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"
sudo -u postgres psql -tAc "SELECT datname, pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"
sudo -u postgres psql -d fastapi_db -c "\l+ fastapi_db"

# Verify PostgreSQL connectivity using the configured application credentials
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_user, current_database();"

# Verify the application environment file without exposing its password
stat -c '%A %U:%G %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION)=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env | sed -E 's#://[^:]+:[^@]+@#://REDACTED:REDACTED@#'

# Verify the fastapi-tutorial systemd unit
stat -c '%A %U:%G %n' /etc/systemd/system/fastapi-tutorial.service
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl daemon-reload
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl cat fastapi-tutorial
systemctl show fastapi-tutorial \
  --property=User,WorkingDirectory,ExecStart,Restart,Environment

# Verify the fastapi-tutorial process and listener
systemctl status fastapi-tutorial
ps aux | grep '[u]vicorn app.main:app'
ss -tlnp | grep ':8000'
curl -i http://127.0.0.1:8000/

# Verify service logs
journalctl -u fastapi-tutorial --no-pager -n 100
```

Expected migration results:

- `postgresql` is enabled and active.
- Role `fastapi` exists.
- Database `fastapi_db` exists and is owned by `fastapi`.
- `/opt/fastapi-tutorial/venv/bin/uvicorn` exists.
- `/etc/systemd/system/fastapi-tutorial.service` is valid and enabled.
- The `fastapi-tutorial` process listens on port `8000`.
- `curl -i http://127.0.0.1:8000/` returns an application response rather than a connection failure.