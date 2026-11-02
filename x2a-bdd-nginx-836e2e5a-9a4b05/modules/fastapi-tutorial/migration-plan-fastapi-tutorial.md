---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI Tutorial application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main`. It installs Python, Git, PostgreSQL, and application dependencies; creates the `/opt/fastapi-tutorial` virtual environment; provisions the `fastapi` PostgreSQL role and `fastapi_db` database; writes the application environment file; and manages a systemd service running Uvicorn on TCP port `8000`. The migration should replace the hardcoded database password with the encrypted variable `fastapi_db_password`.

## Service Type and Instances

**Service Type**: Application Server backed by a PostgreSQL database

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application server
  - Application path: `/opt/fastapi-tutorial`
  - Source repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Git revision: `main`
  - Python virtual environment: `/opt/fastapi-tutorial/venv`
  - Application entry point: `app.main:app`
  - Application server: `uvicorn`
  - Bind address: `0.0.0.0`
  - Port: `8000`
  - systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - systemd user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Restart policy: `Restart=always`

- **fastapi_db**: PostgreSQL database used by the FastAPI application
  - Database user: `fastapi`
  - Database password: currently hardcoded as `fastapi_password`; migration variable: `fastapi_db_password`
  - Database host: `localhost`
  - Database owner: `fastapi`
  - Connection string: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`

There are no collection attributes or `.each` iterations in the analyzed execution flow.

## File Structure

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
```

No attribute files are used.

**Files:**
```text
```

No static cookbook files are deployed by `cookbook_file` or `remote_file`. The application source is obtained from the Git repository declared in the recipe.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the system packages `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates the virtual environment with `python3 -m venv /opt/fastapi-tutorial/venv`, guarded by the existence of `/opt/fastapi-tutorial/venv`.
   - Installs dependencies from `/opt/fastapi-tutorial/requirements.txt` using `/opt/fastapi-tutorial/venv/bin/pip`.
   - Enables and starts the `postgresql` service.
   - Runs PostgreSQL initialization commands as the `postgres` operating-system user:
     - Creates the `fastapi` role with the configured password.
     - Creates the `fastapi_db` database owned by `fastapi`.
     - Grants all privileges on `fastapi_db` to `fastapi`.
   - The original commands use `|| true`, making duplicate-object errors non-fatal but providing imprecise idempotence. The migration should use PostgreSQL-specific Ansible modules instead.
   - Creates `/opt/fastapi-tutorial/.env` with:
     - `PROJECT_NAME="FastAPI Tutorial"`
     - `API_VERSION=1.0.0`
     - `DATABASE_URL=postgresql://fastapi:fastapi_db_password@localhost/fastapi_db`
   - The Chef file mode is `0644`; the migration should preferably use mode `0600` because the file contains a database password.
   - Creates `/etc/systemd/system/fastapi-tutorial.service` with owner `root`, group `root`, and mode `0644`.
   - Configures the systemd unit to:
     - Start after `network.target` and `postgresql.service`.
     - Run as `root`.
     - Use `/opt/fastapi-tutorial` as its working directory.
     - Use `/opt/fastapi-tutorial/venv/bin` in `PATH`.
     - Execute `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`.
     - Restart automatically with `Restart=always`.
     - Be enabled through `multi-user.target`.
   - Triggers `systemctl daemon-reload` after the systemd unit changes. The reload resource has action `nothing` and does not run independently.
   - Enables and starts the `fastapi-tutorial` service after the application dependencies, PostgreSQL service, database objects, environment file, systemd unit, and systemd reload are complete.
   - Iterations: None. No `.each` loops are present.

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

**Application source dependencies**:

- Repository: `https://github.com/dibanez/fastapi_tutorial.git`
- Revision: `main`
- Python requirements file: `/opt/fastapi-tutorial/requirements.txt`

**Service dependencies**:

- `fastapi-tutorial` depends on `postgresql.service`.
- The FastAPI application depends on the packages in `/opt/fastapi-tutorial/requirements.txt`.
- The application requires the PostgreSQL role `fastapi`.
- The application requires the PostgreSQL database `fastapi_db`.
- The database `fastapi_db` is owned by `fastapi`.

**Migration module dependencies**:

- `community.postgresql.postgresql_user`
- `community.postgresql.postgresql_db`
- `community.postgresql.postgresql_privs`, if explicit privilege management is retained

**Supported platforms from metadata**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

Package names and PostgreSQL service names should be verified for the target operating system. The analyzed execution flow uses the package names and service name listed above.

## Credentials

**Detection Summary**: 1 credential detected in 1 recipe file.

**Source**:
  - **Provider**: Hardcoded plaintext; no HashiCorp Vault, CyberArk, AWS Secrets Manager, Chef Vault, data bag, encrypted data bag, or environment-variable secret lookup was detected.
  - **URL**: None detected.
  - **Path**: `cookbooks/fastapi-tutorial/recipes/default.rb`

### PostgreSQL application password

- **Variable(s)**: Current Chef implementation has no variable and hardcodes `fastapi_password`. The migration variable must be `fastapi_db_password`.
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded plaintext in an inline PostgreSQL command and the inline `.env` file.
- **Usage context**:
  - PostgreSQL role creation for the `fastapi` user.
  - `DATABASE_URL` in `/opt/fastapi-tutorial/.env`.
- **Migration storage**: Store `fastapi_db_password` in Ansible Vault and use it in both the PostgreSQL user task and the `.env` template or copy task.
- **Secret path**: None detected.
- **Security requirement**: Do not place the password directly in command arguments or unencrypted task output. Use mode `0600` for `/opt/fastapi-tutorial/.env`.

## Checks for the Migration

**Files to verify**:

- `cookbooks/fastapi-tutorial/recipes/default.rb`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Directories to verify**:

- `/opt/fastapi-tutorial`

**Database objects to verify**:

- PostgreSQL role `fastapi`
- PostgreSQL database `fastapi_db`
- Database owner `fastapi`
- All required privileges for `fastapi` on `fastapi_db`

**Service endpoints to check**:

- `fastapi-tutorial`: TCP `0.0.0.0:8000`
- `fastapi_db`: PostgreSQL on `localhost`, using the platform's configured PostgreSQL socket or local PostgreSQL endpoint

**Unix sockets**: No application Unix sockets are configured.

**Templates rendered**: 0. No templates are present or rendered. The `.env` file and systemd unit are created using inline file resources in Chef; the migration may use `ansible.builtin.copy` or `ansible.builtin.template`.

**Logs to verify**:

- `fastapi-tutorial.service` systemd journal
- `postgresql` systemd journal

## Pre-flight checks:

```bash
# Application instance: fastapi-tutorial
test -d /opt/fastapi-tutorial
test -d /opt/fastapi-tutorial/venv
test -f /opt/fastapi-tutorial/requirements.txt
test -f /opt/fastapi-tutorial/.env
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
git -C /opt/fastapi-tutorial log -1 --oneline
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip --version
/opt/fastapi-tutorial/venv/bin/pip check

# Application environment configuration
grep '^PROJECT_NAME=' /opt/fastapi-tutorial/.env
grep '^API_VERSION=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env
stat -c '%A %U:%G %n' /opt/fastapi-tutorial/.env

# PostgreSQL instance: fastapi_db
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname = 'fastapi';"
sudo -u postgres psql -tAc "SELECT datname, pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"

# Verify database access for fastapi_db using the vaulted migration credential
PGPASSWORD="$fastapi_db_password" psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_database(), current_user;"

# FastAPI systemd instance: fastapi-tutorial
systemctl cat fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
grep '^After=' /etc/systemd/system/fastapi-tutorial.service
grep '^User=' /etc/systemd/system/fastapi-tutorial.service
grep '^WorkingDirectory=' /etc/systemd/system/fastapi-tutorial.service
grep '^Environment=' /etc/systemd/system/fastapi-tutorial.service
grep '^ExecStart=' /etc/systemd/system/fastapi-tutorial.service
grep '^Restart=' /etc/systemd/system/fastapi-tutorial.service

# FastAPI endpoint and listener
curl -I http://127.0.0.1:8000/
ss -tlnp | grep ':8000'
ps aux | grep '[u]vicorn'

# Service logs
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u postgresql --no-pager -n 100

# Restart validation for fastapi-tutorial
sudo systemctl restart fastapi-tutorial
systemctl is-active fastapi-tutorial
curl -I http://127.0.0.1:8000/
```

The expected application command is:

```text
/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The expected database result is:

```text
fastapi_db|fastapi
```

The FastAPI endpoint should accept connections on port `8000`. A `404` response from `/` is acceptable if the application does not define a root route, provided the Uvicorn process is reachable and the service logs contain no startup, import, or PostgreSQL connection errors.