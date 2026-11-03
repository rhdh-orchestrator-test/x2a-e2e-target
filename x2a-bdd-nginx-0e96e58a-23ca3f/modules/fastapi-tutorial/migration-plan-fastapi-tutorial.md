---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI application from the `main` branch of `https://github.com/dibanez/fastapi_tutorial.git`, installs Python, PostgreSQL, Git, and application dependencies, creates a Python virtual environment, provisions the PostgreSQL role and database, writes the application `.env` file, and runs Uvicorn as the `fastapi-tutorial` systemd service on `0.0.0.0:8000`. The cookbook contains one application instance, no Chef attributes, no external cookbook dependencies, no templates, and no iteration loops.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application served by Uvicorn
  - Application directory: `/opt/fastapi-tutorial`
  - Python virtual environment: `/opt/fastapi-tutorial/venv`
  - Source repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Git revision: `main`
  - Application command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Listen address: `0.0.0.0`
  - Port: `8000`
  - Service user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Restart policy: `Restart=always`
  - Environment file: `/opt/fastapi-tutorial/.env`
  - systemd unit: `/etc/systemd/system/fastapi-tutorial.service`

**PostgreSQL database configuration**:

- Database user: `fastapi`
- Database password: `fastapi_password`
- Database name: `fastapi_db`
- Database owner: `fastapi`
- Database host: `localhost`
- Database connection URL: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- PostgreSQL port: Not explicitly configured; use the distribution default
- PostgreSQL socket: Not explicitly configured; use the distribution default

No collection attributes or `.each` iterations are present.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**
```text
cookbooks/fastapi-tutorial/recipes/default.rb
```

**Providers:**

None.

**Templates:**

None. The cookbook writes configuration files using inline Chef `file` resources rather than `.erb` templates.

**Attributes:**

None.

**Files:**

None. No `cookbook_file` or `remote_file` resources deploy static cookbook files.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Creates `/opt/fastapi-tutorial` as `root:root` with mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates the virtual environment with `python3 -m venv /opt/fastapi-tutorial/venv`, only when `/opt/fastapi-tutorial/venv` does not exist.
   - Installs `/opt/fastapi-tutorial/requirements.txt` using `/opt/fastapi-tutorial/venv/bin/pip`; the working directory is `/opt/fastapi-tutorial`.
   - Enables and starts the `postgresql` service.
   - Creates PostgreSQL role `fastapi` with password `fastapi_password`.
   - Creates database `fastapi_db` owned by `fastapi` and grants all privileges on it to `fastapi`.
   - The original database commands use `|| true`, making repeated execution tolerant but not precisely idempotent.
   - Writes `/opt/fastapi-tutorial/.env` as `root:root` with mode `0644`:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Writes `/etc/systemd/system/fastapi-tutorial.service` as `root:root` with mode `0644`:
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
   - Runs `systemctl daemon-reload` immediately when the systemd unit file changes; this resource otherwise has action `nothing`.
   - Enables and starts the `fastapi-tutorial` service after the source, virtual environment, Python dependencies, PostgreSQL service, database objects, `.env` file, systemd unit, and daemon reload are available.
   - No `.each` loops or collection iterations are present.

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

**Application source dependency**:

- Repository: `https://github.com/dibanez/fastapi_tutorial.git`
- Revision: `main`
- Required checkout file: `/opt/fastapi-tutorial/requirements.txt`

**Ansible collection dependency**:

- `community.postgresql` for PostgreSQL user, database, and privilege modules

**Service dependencies**:

- `postgresql`
- `fastapi-tutorial`

The application connects to PostgreSQL at `localhost` using database `fastapi_db`. The systemd unit declares `After=network.target postgresql.service`.

## Credentials

**Detection Summary**: 1 database credential detected across 1 file.

**Source**:
  - **Provider**: Hardcoded in the Chef recipe
  - **URL**: None
  - **Path**: `cookbooks/fastapi-tutorial/recipes/default.rb`

### PostgreSQL application password

- **Variable(s)**: `fastapi_password`; `DATABASE_URL`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the SQL command and written to `/opt/fastapi-tutorial/.env`
- **Usage context**:
  - Creates PostgreSQL role `fastapi`
  - Authenticates the FastAPI application to PostgreSQL
  - Appears in `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Migration handling**:
  - Store the password in Ansible Vault.
  - Use the vaulted value in the PostgreSQL user task.
  - Use the same vaulted value when rendering `/opt/fastapi-tutorial/.env`.
  - Use `no_log: true` for password-management tasks where appropriate.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, HashiCorp Vault, AWS Secrets Manager, TLS certificates, private keys, API keys, or tokens were detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/venv/bin/python`
- `/opt/fastapi-tutorial/venv/bin/pip`
- `/opt/fastapi-tutorial/venv/bin/uvicorn`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- Application module `app.main` from the repository source

**Database objects to verify**:

- PostgreSQL role `fastapi`
- PostgreSQL database `fastapi_db`
- Owner of `fastapi_db`: `fastapi`
- All privileges on `fastapi_db` granted to `fastapi`

**Service endpoints to check**:

- **fastapi-tutorial**: `0.0.0.0:8000`
- **PostgreSQL**: `localhost`, using the distribution-default port and socket

**Templates rendered**:

- No `.erb` templates are rendered.
- `/opt/fastapi-tutorial/.env`: written once by a Chef `file` resource
- `/etc/systemd/system/fastapi-tutorial.service`: written once by a Chef `file` resource

## Pre-flight checks:

```bash
# Verify required packages
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

# RPM-based systems:
rpm -q python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

# Verify the fastapi-tutorial checkout and revision
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
git -C /opt/fastapi-tutorial rev-parse --verify HEAD
test -f /opt/fastapi-tutorial/requirements.txt

# Verify the fastapi-tutorial virtual environment and executables
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn

# Verify PostgreSQL for fastapi-tutorial
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
sudo -u postgres psql -c "\du fastapi"
sudo -u postgres psql -c "\l+ fastapi_db"
sudo -u postgres psql -d fastapi_db -c "\dp"

# Verify fastapi-tutorial database connectivity
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_user, current_database();"

# Verify the fastapi-tutorial environment file without exposing its full contents
stat -c '%U %G %a %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' /opt/fastapi-tutorial/.env

# Verify the fastapi-tutorial systemd unit
stat -c '%U %G %a %n' /etc/systemd/system/fastapi-tutorial.service
systemctl daemon-reload
systemctl cat fastapi-tutorial
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
grep -E '^(Description|After|Type|User|WorkingDirectory|Environment|ExecStart|Restart|WantedBy)=' \
  /etc/systemd/system/fastapi-tutorial.service

# Verify the fastapi-tutorial service
systemctl status fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
ps aux | grep '[u]vicorn app.main:app'

# Verify the fastapi-tutorial endpoint on port 8000
ss -tlnp | grep ':8000'
netstat -tulpn | grep ':8000'
lsof -iTCP:8000 -sTCP:LISTEN
curl -i http://127.0.0.1:8000/

# Review fastapi-tutorial logs
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u fastapi-tutorial -f

# Verify restart configuration
systemctl show fastapi-tutorial | grep -E 'UnitFileState|ActiveState|SubState|Restart|ExecMainStatus'

# Run the Ansible playbook twice and verify that the second run does not:
# - Recreate the virtual environment
# - Reinstall unchanged Python dependencies unnecessarily
# - Recreate the PostgreSQL role or database
# - Rewrite unchanged configuration files
# - Reload systemd when the unit file is unchanged
# - Restart fastapi-tutorial when no relevant source or configuration changed
```

Expected application command:

```text
/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Expected environment keys:

```text
PROJECT_NAME="FastAPI Tutorial"
API_VERSION=1.0.0
DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
```

The PostgreSQL connectivity check should report `current_user` as `fastapi` and `current_database` as `fastapi_db`. The application should return an HTTP response rather than a connection-refused error. The cookbook does not define a dedicated health endpoint.