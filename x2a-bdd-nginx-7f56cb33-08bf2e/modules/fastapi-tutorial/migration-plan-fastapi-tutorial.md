---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI Tutorial application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main`. It installs Python, PostgreSQL, Git, and PostgreSQL development dependencies; creates a Python virtual environment; installs application requirements; creates the PostgreSQL `fastapi` user and `fastapi_db` database; writes an environment file containing the database connection string; and manages a systemd service running Uvicorn on `0.0.0.0:8000`. The cookbook contains one recipe, one application instance, no custom resources, no rendered templates, and one hardcoded database credential.

## Service Type and Instances

**Service Type**: Application Server / Web Application

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application served by Uvicorn
  - Location/Path: `/opt/fastapi-tutorial`
  - Source repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Python virtual environment: `/opt/fastapi-tutorial/venv`
  - Environment file: `/opt/fastapi-tutorial/.env`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Service user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Port/Socket: `0.0.0.0:8000`
  - Restart policy: `Restart=always`
  - PATH: `/opt/fastapi-tutorial/venv/bin`
  - Dependencies: `network.target`, `postgresql.service`

- **postgresql**: Database service for the FastAPI application
  - Service name: `postgresql`
  - Database user: `fastapi`
  - Database: `fastapi_db`
  - Database owner: `fastapi`
  - Connection host: `localhost`
  - Port: `5432`, unless configured differently on the target system
  - Connection URL: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
  - Privileges: All privileges on `fastapi_db` granted to `fastapi`

There are no collection iterations or `.each` loops in the execution tree.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

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

The `.env` file and systemd unit are created using inline Chef `file` resources, not cookbook template or static-file resources.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the seven system packages `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev` in one `package` resource.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates the virtual environment with `python3 -m venv /opt/fastapi-tutorial/venv`, guarded by the existence of `/opt/fastapi-tutorial/venv`.
   - Installs application dependencies with `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt` from `/opt/fastapi-tutorial`.
   - Enables and starts `postgresql`.
   - Executes PostgreSQL commands as the `postgres` operating-system user to create the `fastapi` role, set its password to `fastapi_password`, create `fastapi_db` owned by `fastapi`, and grant all database privileges to `fastapi`.
   - Uses `|| true` after each SQL command, so existing roles or databases do not fail the resource. The operation is not fully idempotent because it executes on every run and suppresses errors.
   - Creates `/opt/fastapi-tutorial/.env` with owner `root`, group `root`, and mode `0644`, containing:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Creates `/etc/systemd/system/fastapi-tutorial.service` with owner `root`, group `root`, and mode `0644`.
   - The systemd unit runs `app.main:app` with Uvicorn on `0.0.0.0:8000`, uses `/opt/fastapi-tutorial` as its working directory, sets `PATH` to `/opt/fastapi-tutorial/venv/bin`, runs as `root`, restarts with `Restart=always`, and starts after `network.target` and `postgresql.service`.
   - Immediately notifies `execute[systemd_reload]` when the systemd unit changes.
   - Defines `execute[systemd_reload]` with action `:nothing`; when notified, it runs `systemctl daemon-reload`.
   - Enables and starts the `fastapi-tutorial` service after the repository, virtual environment, dependencies, PostgreSQL service, database objects, `.env` file, systemd unit, and systemd reload are complete.
   - Resources and execution order:
     1. `package` resource containing seven package names
     2. `directory[/opt/fastapi-tutorial]`
     3. `git` resource synchronizing the application repository
     4. `execute[create_venv]`
     5. `execute[install_dependencies]`
     6. `service[postgresql]` with actions `enable`, `start`
     7. `execute[create_db_user]` containing three PostgreSQL operations
     8. `file[/opt/fastapi-tutorial/.env]`
     9. `file[/etc/systemd/system/fastapi-tutorial.service]`
     10. `execute[systemd_reload]`, action `:nothing`, triggered immediately by the systemd unit file
     11. `service[fastapi-tutorial]` with actions `enable`, `start`

No `.each` loops or collection iterations require expansion.

## Dependencies

**External cookbook dependencies**: None declared in `metadata.rb`.

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

**Application dependency source**:

- `/opt/fastapi-tutorial/requirements.txt`
- Installed into `/opt/fastapi-tutorial/venv`

**Chef platform metadata**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

The package names in the recipe are Debian/Ubuntu-oriented. Platform-specific mappings are required if CentOS support remains in scope.

## Credentials

**Detection Summary**: 1 hardcoded credential detected in 1 recipe file. The same password is used in the PostgreSQL creation command and the application database URL.

**Source**:
  - **Provider**: Hardcoded in the Chef recipe
  - **URL**: None
  - **Path**: None
  - **Storage locations**: Inline PostgreSQL command and generated `.env` file

### PostgreSQL database password

- **Variable(s)**: `fastapi_password`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded plaintext
- **Usage context**: PostgreSQL authentication for user `fastapi` connecting to database `fastapi_db`
- **References**:
  ```bash
  CREATE USER fastapi WITH PASSWORD 'fastapi_password';
  ```
  ```text
  DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
  ```
- **Generated destination**: `/opt/fastapi-tutorial/.env`
- **Migration recommendation**: Store the password in Ansible Vault and inject it into both the PostgreSQL user task and the `.env` task. Avoid committing the plaintext value to the Ansible repository.

No Chef data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secret references, TLS certificate references, or external secret-manager integrations were detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Database objects to verify**:

- PostgreSQL role `fastapi`
- PostgreSQL database `fastapi_db`
- Owner of `fastapi_db`: `fastapi`
- All expected privileges granted to `fastapi`

**Service endpoints to check**:

- FastAPI: `0.0.0.0:8000`
- PostgreSQL: `localhost:5432`, subject to the system's PostgreSQL listener configuration

**Unix sockets**:

- No explicit Unix socket path is configured.
- PostgreSQL may create its platform-default Unix socket.

**Templates rendered**: None.

**Inline files created**:

- `/opt/fastapi-tutorial/.env`: rendered once by the Chef `file` resource
- `/etc/systemd/system/fastapi-tutorial.service`: rendered once by the Chef `file` resource

## Pre-flight checks

### fastapi-tutorial application instance

```bash
test -d /opt/fastapi-tutorial
test -d /opt/fastapi-tutorial/venv
test -f /opt/fastapi-tutorial/requirements.txt
test -f /opt/fastapi-tutorial/.env
test -f /etc/systemd/system/fastapi-tutorial.service

/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip --version
/opt/fastapi-tutorial/venv/bin/pip check
/opt/fastapi-tutorial/venv/bin/pip list

systemctl cat fastapi-tutorial
systemctl show fastapi-tutorial \
  --property=User,WorkingDirectory,ExecStart,Restart,FragmentPath
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service

pgrep -af '/opt/fastapi-tutorial/venv/bin/uvicorn'
ss -ltnp | grep ':8000'
curl -i http://127.0.0.1:8000/
```

Expected results:

- The application directory, virtual environment, requirements file, environment file, and systemd unit exist.
- `pip check` reports no dependency conflicts.
- `fastapi-tutorial` is enabled and active.
- The unit uses `User=root`, `WorkingDirectory=/opt/fastapi-tutorial`, `Restart=always`, and the virtual environment's Uvicorn binary.
- Uvicorn runs `app.main:app --host 0.0.0.0 --port 8000`.
- Port `8000` is listening.
- The HTTP request returns a response from the FastAPI application. The exact status code and body are application-defined.

Verify the environment file:

```bash
stat -c '%U:%G %a %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' /opt/fastapi-tutorial/.env
```

Expected content:

```dotenv
PROJECT_NAME="FastAPI Tutorial"
API_VERSION=1.0.0
DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
```

The Chef source specifies `root:root` and mode `0644`; mode `0600` is recommended for the migrated file because it contains a database password.

### postgresql database instance

```bash
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
ss -ltnp | grep ':5432'
```

Expected results:

- `postgresql` is enabled and active.
- PostgreSQL listens on port `5432`, unless explicitly configured otherwise.

Verify the role:

```bash
sudo -u postgres psql -tAc \
  "SELECT 1 FROM pg_roles WHERE rolname='fastapi';"
```

Expected output:

```text
1
```

Verify the database and owner:

```bash
sudo -u postgres psql -tAc \
  "SELECT datname, pg_get_userbyid(datdba) FROM pg_database WHERE datname='fastapi_db';"
```

Expected output identifies:

```text
fastapi_db | fastapi
```

Verify application credentials:

```bash
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_database(), current_user;"
```

Expected results:

- Current database: `fastapi_db`
- Current user: `fastapi`

Do not expose the password in shell history in production. Use a protected environment or temporary PostgreSQL password file for operational checks.

Verify database privileges:

```bash
sudo -u postgres psql -tAc \
  "SELECT datname, datacl FROM pg_database WHERE datname='fastapi_db';"
```

Confirm that the ACL grants the expected privileges to `fastapi`.

### Packages and service logs

On Debian/Ubuntu systems:

```bash
dpkg-query -W \
  python3 python3-pip python3-venv git \
  postgresql postgresql-contrib libpq-dev
```

On CentOS/RHEL systems, use the platform's package query command.

Review logs for both named services:

```bash
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u postgresql --no-pager -n 100
```

Check for:

- Successful Uvicorn startup
- Successful import of `app.main:app`
- No database connection errors
- No missing Python package errors
- No PostgreSQL startup failures

Verify restart behavior:

```bash
systemctl show fastapi-tutorial --property=Restart
```

Expected output:

```text
Restart=always
```