---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI Tutorial application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` under `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, and PostgreSQL development packages; creates a Python virtual environment; installs dependencies from `requirements.txt`; provisions the `fastapi` PostgreSQL user and `fastapi_db` database; writes an application `.env` file; and manages a systemd service listening on `0.0.0.0:8000`. The cookbook contains one recipe, no templates, no providers, no static cookbook files, and no collection iterations.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application managed by systemd
  - Location/Path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Python virtual environment: `/opt/fastapi-tutorial/venv`
  - Dependency file: `/opt/fastapi-tutorial/requirements.txt`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Run user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Executable: `/opt/fastapi-tutorial/venv/bin/uvicorn`
  - Application target: `app.main:app`
  - Bind address: `0.0.0.0`
  - Port: `8000`
  - Restart policy: `Restart=always`
  - Environment: `PATH=/opt/fastapi-tutorial/venv/bin`

- **postgresql**: PostgreSQL database dependency
  - Service name: `postgresql`
  - Database user: `fastapi`
  - Database password: `fastapi_password`
  - Database name: `fastapi_db`
  - Database owner: `fastapi`
  - Privileges: `fastapi` receives all privileges on `fastapi_db`
  - Connection host: `localhost`
  - Connection string: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
  - Port: `5432` is expected unless the platform PostgreSQL configuration changes it
  - Socket: PostgreSQL platform-default local Unix socket
  - Initialization: Fedora/RHEL uses `postgresql-setup --initdb`

No `.each` loops or collection-based resource iterations are present.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**
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

The cookbook writes `/opt/fastapi-tutorial/.env` and `/etc/systemd/system/fastapi-tutorial.service` using inline Chef `file` resources. These are generated files, not cookbook static files or templates.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Detects whether the platform family is Fedora/RHEL using `platform_family?('fedora', 'rhel')`.
   - On Fedora/RHEL, installs `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, and `libpq-devel`.
   - On Fedora/RHEL, initializes PostgreSQL with `postgresql-setup --initdb`, guarded by `/var/lib/pgsql/data/PG_VERSION`.
   - On non-Fedora/RHEL platforms, installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates `/opt/fastapi-tutorial/venv` using `python3 -m venv`, guarded by the directory’s existence.
   - Installs Python dependencies from `/opt/fastapi-tutorial/requirements.txt` using the virtual environment.
   - Enables and starts the `postgresql` service.
   - Creates the PostgreSQL role `fastapi` with password `fastapi_password`.
   - Creates the PostgreSQL database `fastapi_db` owned by `fastapi`.
   - Grants all privileges on `fastapi_db` to `fastapi`.
   - Writes `/opt/fastapi-tutorial/.env` with owner `root`, group `root`, and mode `0644`.
   - Writes `/etc/systemd/system/fastapi-tutorial.service` with owner `root`, group `root`, and mode `0644`.
   - The `.env` file contains:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - The systemd unit runs:
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
   - Notifies `systemd_reload` when the systemd unit changes.
   - Reloads systemd with `systemctl daemon-reload` only when notified.
   - Enables and starts the `fastapi-tutorial` service.
   - The original recipe does not explicitly restart `fastapi-tutorial` after a unit-file change. The Ansible migration should normally reload systemd and restart the application service through handlers when the unit changes.

## Dependencies

**External cookbook dependencies**: None specified in the supplied metadata analysis.

**System package dependencies**:

Fedora/RHEL:

- `python3`
- `python3-pip`
- `git`
- `postgresql-server`
- `postgresql-contrib`
- `libpq-devel`

Non-Fedora/RHEL:

- `python3`
- `python3-pip`
- `python3-venv`
- `git`
- `postgresql`
- `postgresql-contrib`
- `libpq-dev`

**Python dependency source**: `/opt/fastapi-tutorial/requirements.txt`

The individual Python packages are supplied by the cloned repository.

**Ansible collection dependencies**:

- `community.postgresql`

The PostgreSQL Ansible modules also require the PostgreSQL Python driver.

**Service dependencies**:

- `postgresql`
- `fastapi-tutorial`

The `fastapi-tutorial` systemd unit declares `After=network.target postgresql.service`.

## Credentials

**Detection Summary**: One database credential detected in one recipe file. The same password is repeated in the PostgreSQL user creation command and the application connection string.

**Source**:
  - **Provider**: Hardcoded in the Chef recipe
  - **URL**: None detected
  - **Path**: None detected

### PostgreSQL database password

- **Variable(s)**:
  - No Chef attribute variable is used.
  - Literal password: `fastapi_password`
  - Connection string: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded plaintext
- **Usage context**:
  - PostgreSQL command: `CREATE USER fastapi WITH PASSWORD 'fastapi_password'`
  - Application `DATABASE_URL` in `/opt/fastapi-tutorial/.env`
- **Migration requirement**:
  - Store the password in Ansible Vault or an approved external secrets manager.
  - Use the same protected variable when creating the PostgreSQL user and rendering `.env`.
  - Apply `no_log: true` to credential-bearing Ansible tasks.
  - Do not expose the password in shell history, logs, or terminal recordings.

No Chef data bags, encrypted data bags, Chef Vault calls, CyberArk or Conjur integrations, environment-variable secret references, TLS certificates, `.pem` files, `.key` files, or API tokens were detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/app/main.py` or the corresponding application source path from the cloned repository

**Database objects to verify**:

- PostgreSQL role: `fastapi`
- PostgreSQL database: `fastapi_db`
- Database owner: `fastapi`
- Database privileges: `ALL` for `fastapi` on `fastapi_db`

**Service endpoints to check**:

- **fastapi-tutorial**: HTTP endpoint at `0.0.0.0:8000`
- **postgresql**: Local PostgreSQL endpoint at `localhost:5432`, when TCP listening is enabled
- **postgresql**: Platform-default local Unix socket

**Templates rendered**:

- None. The cookbook uses inline `file` resources.

**Generated files and render counts**:

- `/opt/fastapi-tutorial/.env`: rendered once
- `/etc/systemd/system/fastapi-tutorial.service`: rendered once

## Pre-flight checks

### fastapi-tutorial instance

```bash
# Verify application directory and deployed files
ls -ld /opt/fastapi-tutorial
ls -l /opt/fastapi-tutorial/requirements.txt
ls -l /opt/fastapi-tutorial/.env
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn

# Verify application configuration without exposing the password
grep -E '^(PROJECT_NAME|API_VERSION)=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env | sed -E 's#(postgresql://[^:]+:)[^@]+#\1***#'

# Verify systemd unit and service state
systemctl cat fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl show fastapi-tutorial \
  -p ActiveState -p SubState -p ExecStart -p User -p WorkingDirectory

# Verify the application process and port
pgrep -af '/opt/fastapi-tutorial/venv/bin/uvicorn'
ss -tlnp | grep ':8000'
lsof -iTCP:8000 -sTCP:LISTEN

# Verify HTTP response
curl -I http://127.0.0.1:8000/
curl -sS http://127.0.0.1:8000/ | head

# Verify application logs
journalctl -u fastapi-tutorial --no-pager -n 100
```

Verify:

- The service is enabled and active.
- `User=root`.
- `WorkingDirectory=/opt/fastapi-tutorial`.
- `ExecStart` uses `/opt/fastapi-tutorial/venv/bin/uvicorn`.
- The application target is `app.main:app`.
- The bind address is `0.0.0.0`.
- The port is `8000`.
- The TCP connection succeeds and the endpoint returns an HTTP response.
- Logs contain no import errors, dependency errors, database authentication failures, or restart loops.

If the repository exposes a health endpoint, validate it after confirming its route:

```bash
curl -i http://127.0.0.1:8000/health
```

### postgresql instance

```bash
# Verify service state
systemctl status postgresql --no-pager
systemctl is-enabled postgresql
systemctl is-active postgresql

# Verify the PostgreSQL role
sudo -u postgres psql -tAc \
  "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"

# Verify the database and owner
sudo -u postgres psql -tAc \
  "SELECT datname, pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"

# Verify database privileges
sudo -u postgres psql -d fastapi_db -tAc \
  "SELECT has_database_privilege('fastapi', 'fastapi_db', 'CONNECT');"

# Verify the PostgreSQL listener when TCP access is configured
ss -tlnp | grep ':5432'

# Review PostgreSQL logs
journalctl -u postgresql --no-pager -n 100
```

Expected results:

- PostgreSQL is enabled and active.
- The role query returns `fastapi`.
- The database query identifies `fastapi_db | fastapi`.
- The privilege query returns `t`.
- Absence of a TCP listener is not necessarily a failure when local Unix-socket access is configured.

Test authenticated database connectivity without placing the real password in shell history:

```bash
PGPASSWORD='RETRIEVE_FROM_AN_APPROVED_SECRET_SOURCE' \
psql -h localhost -U fastapi -d fastapi_db -c "SELECT 1;"
```

Expected output contains:

```text
1
```

### Platform and deployment checks

```bash
# Confirm required executables
python3 --version
python3 -m pip --version
git --version

# Verify generated files
ls -l /etc/systemd/system/fastapi-tutorial.service
du -sh /opt/fastapi-tutorial
```

Expected ownership and permissions:

- `/opt/fastapi-tutorial`: `root:root`, mode `0755`
- `/opt/fastapi-tutorial/.env`: `root:root`, mode `0644` unless intentionally hardened
- `/etc/systemd/system/fastapi-tutorial.service`: `root:root`, mode `0644`

