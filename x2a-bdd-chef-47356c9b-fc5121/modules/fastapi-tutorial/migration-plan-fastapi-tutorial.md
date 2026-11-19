---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys one FastAPI application instance named `fastapi-tutorial` from the `main` revision of `https://github.com/dibanez/fastapi_tutorial.git` into `/opt/fastapi-tutorial`. It installs the platform-specific Python, Git, and PostgreSQL dependencies, initializes and starts PostgreSQL, creates the `fastapi` PostgreSQL role and `fastapi_db` database, creates a Python virtual environment, installs application requirements, writes `/opt/fastapi-tutorial/.env`, and manages a systemd service listening on TCP port `8000`. Repository contents such as `requirements.txt` and `app/main.py` must be verified after checkout because they are not established by the supplied Chef execution analysis.

## Service Type and Instances

**Service Type**: Application Server with PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application served by Uvicorn
  - Application path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Python virtual environment: `/opt/fastapi-tutorial/venv`
  - Systemd service: `fastapi-tutorial`
  - Service unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Process command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Bind address: `0.0.0.0`
  - Port: `8000`
  - Service user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Restart policy: `always`

**Database dependency**:

- PostgreSQL service: `postgresql`
- PostgreSQL role: `fastapi`
- PostgreSQL database: `fastapi_db`
- Database owner: `fastapi`
- Database host: `localhost`
- Database connection URL: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`

## File Structure

The following files are the cookbook files used by the execution flow.

**Recipes:**
```text
cookbooks/fastapi-tutorial/recipes/default.rb
```

**Providers:**
```text
```

No custom Chef resources or provider files are used.

**Templates:**
```text
```

No `.erb` templates are rendered. Configuration files are written using inline Chef `file` resources.

**Attributes:**
```text
cookbooks/fastapi-tutorial/attributes/default.rb
```

**Files:**
```text
```

No static files are deployed by `cookbook_file` or `remote_file`.

## Attributes

**Source file**: `cookbooks/fastapi-tutorial/attributes/default.rb`

The migration plan references these scalar attributes:

| Chef attribute | Value used by the plan | Ansible equivalent |
|---|---|---|
| `node['fastapi_tutorial']['app_path']` | `/opt/fastapi-tutorial` | `fastapi_tutorial_app_path` |
| `node['fastapi_tutorial']['repository']` | `https://github.com/dibanez/fastapi_tutorial.git` | `fastapi_tutorial_repository` |
| `node['fastapi_tutorial']['revision']` | `main` | `fastapi_tutorial_revision` |
| `node['fastapi_tutorial']['service_port']` | `8000` | `fastapi_tutorial_service_port` |

The supplied validation confirms the `app_path` reference in `cookbooks/fastapi-tutorial/recipes/default.rb`, but does not independently provide a complete attributes-file analysis. Verify the contents of `cookbooks/fastapi-tutorial/attributes/default.rb` before migration. No collection attributes or `.each` iterations are present.

## Module Explanation

The cookbook performs operations in this order:

1. **`default` recipe** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Detects whether the platform family is Fedora or RHEL.
   - On Fedora/RHEL, installs:
     - `python3`
     - `python3-pip`
     - `git`
     - `postgresql-server`
     - `postgresql-contrib`
     - `libpq-devel`
   - On non-Fedora/RHEL platforms, installs:
     - `python3`
     - `python3-pip`
     - `python3-venv`
     - `git`
     - `postgresql`
     - `postgresql-contrib`
     - `libpq-dev`
   - On Fedora/RHEL, runs `execute[initialize_postgresql]` with `postgresql-setup --initdb` unless `/var/lib/pgsql/data/PG_VERSION` already exists.
   - Creates `/opt/fastapi-tutorial` as a recursive `root:root` directory with mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Runs `python3 -m venv /opt/fastapi-tutorial/venv` unless `/opt/fastapi-tutorial/venv` already exists.
   - Runs `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt` from `/opt/fastapi-tutorial`.
   - Enables and starts the `postgresql` service.
   - Executes PostgreSQL commands as operating-system user `postgres` to:
     - Create role `fastapi` with password `fastapi_password`.
     - Create database `fastapi_db` owned by `fastapi`.
     - Grant all privileges on `fastapi_db` to `fastapi`.
   - Writes `/opt/fastapi-tutorial/.env` as `root:root` with mode `0644`, containing:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Writes `/etc/systemd/system/fastapi-tutorial.service` as `root:root` with mode `0644`.
   - The service unit:
     - Uses `Type=simple`.
     - Runs as `root`.
     - Uses `/opt/fastapi-tutorial` as its working directory.
     - Sets `PATH=/opt/fastapi-tutorial/venv/bin`.
     - Starts `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`.
     - Restarts with policy `always`.
     - Starts after `network.target` and is ordered after `postgresql.service`.
     - Is enabled through `multi-user.target`.
   - Runs `systemctl daemon-reload` through `execute[systemd_reload]` when the systemd unit file changes.
   - Enables and starts the `fastapi-tutorial` service.

   **Repository-content validation**:
   - The Chef analysis confirms the Git destination but does not analyze the contents of the cloned repository.
   - After checkout, verify `/opt/fastapi-tutorial/requirements.txt`.
   - Verify that the Uvicorn import target `app.main:app` corresponds to `/opt/fastapi-tutorial/app/main.py` or the repository’s actual equivalent layout.

There are no `.each` loops or collection-based instance iterations to expand.

## Dependencies

**External cookbook dependencies**: None listed in the provided metadata or execution tree.

**System package dependencies**:

- **Fedora/RHEL**:
  - `python3`
  - `python3-pip`
  - `git`
  - `postgresql-server`
  - `postgresql-contrib`
  - `libpq-devel`
- **Non-Fedora/RHEL**:
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

## Credentials

**Detection Summary**: 1 database credential detected in 1 source file.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None
- **Path**: None
- **Sensitive value**: `fastapi_password`

### PostgreSQL `fastapi` role password

- **Variable(s)**: No Chef attribute variable; the literal password is `fastapi_password`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded plaintext in an `execute` resource and inline `.env` content
- **Usage context**:
  - PostgreSQL role creation:
    ```sql
    CREATE USER fastapi WITH PASSWORD 'fastapi_password';
    ```
  - Database connection URL:
    ```text
    postgresql://fastapi:fastapi_password@localhost/fastapi_db
    ```
  - Written to:
    ```text
    /opt/fastapi-tutorial/.env
    ```

No Chef data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, certificate files, private keys, API tokens, or external secret-manager URLs were detected. Store the migrated password in Ansible Vault or an approved AAP credential source rather than embedding it in a playbook or role default.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/opt/fastapi-tutorial/app/main.py`, or the repository-specific module implementing `app.main:app`
- `/etc/systemd/system/fastapi-tutorial.service`
- Fedora/RHEL PostgreSQL data directory: `/var/lib/pgsql/data`
- Distribution-managed PostgreSQL data directory on non-Fedora/RHEL systems
- PostgreSQL role: `fastapi`
- PostgreSQL database: `fastapi_db`

**Service endpoints to check**:

- FastAPI instance `fastapi-tutorial`: `0.0.0.0:8000`
- PostgreSQL: local service, normally TCP port `5432` when TCP listening is enabled
- PostgreSQL local Unix socket: distribution-managed path; no custom socket path is configured

**Templates rendered**:

- None; template render count: `0`

**Files written by inline Chef resources**:

- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

## Pre-flight checks

### Platform and package checks

```bash
python3 --version
python3 -m pip --version
git --version
```

On Fedora/RHEL:

```bash
rpm -q python3 python3-pip git postgresql-server postgresql-contrib libpq-devel
test -f /var/lib/pgsql/data/PG_VERSION
```

On Debian/Ubuntu-style systems:

```bash
dpkg -s python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev
```

### `fastapi-tutorial` instance checks

Verify the application directory and checkout:

```bash
test -d /opt/fastapi-tutorial
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
test -f /opt/fastapi-tutorial/requirements.txt
```

Verify the virtual environment and application executable:

```bash
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn
test -f /opt/fastapi-tutorial/app/main.py
```

If the repository layout differs, verify the actual module corresponding to:

```text
app.main:app
```

Validate Python dependencies:

```bash
/opt/fastapi-tutorial/venv/bin/pip check
/opt/fastapi-tutorial/venv/bin/pip list
```

Verify the PostgreSQL dependency:

```bash
systemctl status postgresql --no-pager
systemctl is-enabled postgresql
systemctl is-active postgresql
ps aux | grep '[p]ostgres'
ss -ltnp | grep ':5432'
```

On Fedora/RHEL:

```bash
test -f /var/lib/pgsql/data/PG_VERSION
```

Verify the PostgreSQL role and database:

```bash
sudo -u postgres psql -tAc "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"
sudo -u postgres psql -tAc "SELECT datname, pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"
```

Expected values:

```text
fastapi
fastapi_db | fastapi
```

Verify application-role connectivity without placing the password directly in migration code:

```bash
PGPASSWORD='fastapi_password' psql -h localhost -U fastapi -d fastapi_db -c "SELECT current_user, current_database();"
```

Expected values:

- `current_user`: `fastapi`
- `current_database`: `fastapi_db`

Verify the environment file:

```bash
stat -c '%U %G %a %n' /opt/fastapi-tutorial/.env
grep '^PROJECT_NAME="FastAPI Tutorial"$' /opt/fastapi-tutorial/.env
grep '^API_VERSION=1.0.0$' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env | sed -E 's#://[^:]+:[^@]+@#://REDACTED:REDACTED@#'
```

Verify the systemd unit:

```bash
test -f /etc/systemd/system/fastapi-tutorial.service
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl daemon-reload
systemctl cat fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl show fastapi-tutorial --property=User,WorkingDirectory,ExecStart,Restart
```

Expected unit properties:

- User: `root`
- Working directory: `/opt/fastapi-tutorial`
- Restart policy: `always`
- Uvicorn executable: `/opt/fastapi-tutorial/venv/bin/uvicorn`
- Port: `8000`

Verify the application process and endpoint:

```bash
systemctl status fastapi-tutorial --no-pager
ps aux | grep '[u]vicorn'
ss -ltnp | grep ':8000'
curl -i http://127.0.0.1:8000/
```

The listener must be bound to `0.0.0.0` or an equivalent all-interface address. If supported by the repository, also test:

```bash
curl -i http://127.0.0.1:8000/docs
curl -i http://127.0.0.1:8000/openapi.json
```

Review service logs:

```bash
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u postgresql --no-pager -n 100
journalctl -u fastapi-tutorial --no-pager | grep -Ei 'error|failed|traceback|exception'
```

If `fastapi-tutorial` fails, verify:

- `/opt/fastapi-tutorial/venv/bin/uvicorn` exists.
- The repository provides the `app.main:app` import target.
- `/opt/fastapi-tutorial/.env` exists.
- PostgreSQL is active.
- `fastapi_db` exists and is owned by `fastapi`.
- The password matches the protected value used in `.env`.
- TCP port `8000` is available.

Verify systemd reload behavior after changing the unit through the Ansible role:

```bash
systemctl daemon-reload
systemctl restart fastapi-tutorial
systemctl is-active fastapi-tutorial
```

The Ansible role should notify `systemctl daemon-reload` whenever `/etc/systemd/system/fastapi-tutorial.service` changes, then ensure `fastapi-tutorial` is enabled and started.