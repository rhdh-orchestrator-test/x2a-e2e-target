---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the `fastapi-tutorial` FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, and platform-specific PostgreSQL development packages; creates a Python virtual environment; installs application dependencies; initializes and starts PostgreSQL; creates the `fastapi` PostgreSQL user and `fastapi_db` database; writes the application environment file; and manages the `fastapi-tutorial` systemd service. The FastAPI service runs as `root`, uses Uvicorn, listens on `0.0.0.0:8000`, and starts after PostgreSQL. The cookbook contains one recipe, no Chef templates, no custom providers, and no collection iterations.

## Service Type and Instances

**Service Type**: Application server with a local PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application served by Uvicorn
  - Location/Path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Dependency file: `/opt/fastapi-tutorial/requirements.txt`
  - Application entry point: `app.main:app`
  - Service name: `fastapi-tutorial`
  - Service user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Port/Socket: `0.0.0.0:8000`
  - Startup command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Restart behavior: `Restart=always`
  - Systemd ordering: After `network.target` and `postgresql.service`
  - Environment path: `/opt/fastapi-tutorial/venv/bin`

- **postgresql**: Local application database
  - Service name: `postgresql`
  - Database user: `fastapi`
  - Database name: `fastapi_db`
  - Database owner: `fastapi`
  - Host: `localhost`
  - Port/Socket: `localhost:5432` and the distribution’s default local PostgreSQL Unix socket
  - Connection string: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`

There are no `.each` loops or collection attributes. No iterated instance names require expansion.

## File Structure

Only files used by the analyzed cookbook are listed below.

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
cookbooks/fastapi-tutorial/attributes/default.rb
```

**Files:**

```text
None
```

## Attributes

`cookbooks/fastapi-tutorial/attributes/default.rb` defines these defaults:

| Chef attribute | Default value | Ansible equivalent |
|---|---|---|
| `node['fastapi_tutorial']['app_path']` | `/opt/fastapi-tutorial` | `fastapi_app_path` |
| `node['fastapi_tutorial']['repository']` | `https://github.com/dibanez/fastapi_tutorial.git` | `fastapi_repository` |
| `node['fastapi_tutorial']['revision']` | `main` | `fastapi_revision` |
| `node['fastapi_tutorial']['service_port']` | `8000` | `fastapi_service_port` |

Suggested Ansible defaults:

```yaml
fastapi_app_path: /opt/fastapi-tutorial
fastapi_repository: https://github.com/dibanez/fastapi_tutorial.git
fastapi_revision: main
fastapi_service_port: 8000
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Detects whether the platform belongs to the Fedora or RHEL platform families.
   - On Fedora/RHEL systems, installs:
     - `python3`
     - `python3-pip`
     - `git`
     - `postgresql-server`
     - `postgresql-contrib`
     - `libpq-devel`
   - On non-Fedora/RHEL systems, installs:
     - `python3`
     - `python3-pip`
     - `python3-venv`
     - `git`
     - `postgresql`
     - `postgresql-contrib`
     - `libpq-dev`
   - On Fedora/RHEL systems, runs `postgresql-setup --initdb` through `execute[initialize_postgresql]` when `/var/lib/pgsql/data/PG_VERSION` does not exist.
   - Creates `/opt/fastapi-tutorial` with owner `root`, group `root`, mode `0755`, and recursive creation enabled.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` into `/opt/fastapi-tutorial` at revision `main`.
   - Creates `/opt/fastapi-tutorial/venv` with:
     ```bash
     python3 -m venv /opt/fastapi-tutorial/venv
     ```
     The command is guarded by the existence of `/opt/fastapi-tutorial/venv`.
   - Installs Python dependencies from `/opt/fastapi-tutorial/requirements.txt` using:
     ```bash
     /opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt
     ```
     with `/opt/fastapi-tutorial` as the working directory.
   - Enables and starts the `postgresql` service.
   - Creates the PostgreSQL user `fastapi` with password `fastapi_password`.
   - Creates the `fastapi_db` database with owner `fastapi`.
   - Grants all privileges on `fastapi_db` to `fastapi`.
   - Writes `/opt/fastapi-tutorial/.env` with:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
     The Chef file is owned by `root:root` and has mode `0644`. The migration should preferably use mode `0600` and obtain the password from Ansible Vault.
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
     The unit file is owned by `root:root` and has mode `0644`.
   - Defines `execute[systemd_reload]` with command `systemctl daemon-reload` and default action `nothing`.
   - Notifies `execute[systemd_reload]` immediately when the systemd unit file changes.
   - Enables and starts the `fastapi-tutorial` service after the repository, virtual environment, dependencies, PostgreSQL service, database objects, environment file, systemd unit, and systemd reload are complete.
   - Iterations: none; the recipe contains no `.each` loops or collection-based instances.

## Dependencies

**External cookbook dependencies**: None declared in the analyzed cookbook.

**System package dependencies:**

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

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**Ansible collection dependencies**:

- `community.postgresql` for PostgreSQL users, databases, and privileges

## Credentials

**Detection Summary**: 1 database credential detected across `cookbooks/fastapi-tutorial/recipes/default.rb`.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None detected
- **Path**: None detected

### PostgreSQL `fastapi` database password

- **Variable(s)**: No Chef attribute variable; literal value is `fastapi_password`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the recipe and application `.env` content
- **Usage context**:
  - Creates PostgreSQL user `fastapi`
  - Authenticates the application against `fastapi_db`
  - Appears in the `DATABASE_URL` connection string
- **Connection string**:
  ```text
  postgresql://fastapi:fastapi_password@localhost/fastapi_db
  ```
- **Migration handling**:
  - Store the password in Ansible Vault.
  - Use the vaulted value with `community.postgresql.postgresql_user`.
  - Construct the `.env` `DATABASE_URL` from vaulted variables.
  - Apply `no_log: true` to tasks handling the password.
  - Use mode `0600` for `/opt/fastapi-tutorial/.env` unless the application requires `0644`.

No data bags, Chef Vault items, Conjur variables, CyberArk integrations, AWS Secrets Manager references, environment-variable secret references, TLS certificates, PEM files, key files, or API tokens were detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/.env`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/venv/bin/uvicorn`
- `/etc/systemd/system/fastapi-tutorial.service`
- `/var/lib/pgsql/data/PG_VERSION` on Fedora/RHEL systems
- The distribution-specific PostgreSQL data directory on non-Fedora/RHEL systems

**Database objects to verify**:

- PostgreSQL user `fastapi`
- PostgreSQL database `fastapi_db`
- Database owner `fastapi`
- All privileges on `fastapi_db` for `fastapi`

**Service endpoints to check**:

- `fastapi-tutorial`: `0.0.0.0:8000`
- `postgresql`: `localhost:5432`
- PostgreSQL’s default local Unix socket

**Templates rendered**:

- Chef templates: none
- `/opt/fastapi-tutorial/.env`: one inline file deployment
- `/etc/systemd/system/fastapi-tutorial.service`: one inline file deployment
- Ansible implementation templates, if used, should render each managed file once

## Pre-flight checks

### Package and platform checks

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

On Debian/Ubuntu:

```bash
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev
```

### `fastapi-tutorial` application checks

```bash
git -C /opt/fastapi-tutorial remote -v
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
git -C /opt/fastapi-tutorial status --short
test -d /opt/fastapi-tutorial/venv
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn
test -f /opt/fastapi-tutorial/requirements.txt
```

The checked-out revision should be `main` unless `fastapi_revision` intentionally overrides the default.

Validate the environment file without exposing the password:

```bash
stat -c '%U:%G %a %n' /opt/fastapi-tutorial/.env
grep '^PROJECT_NAME=' /opt/fastapi-tutorial/.env
grep '^API_VERSION=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env
```

Expected keys:

```text
PROJECT_NAME="FastAPI Tutorial"
API_VERSION=1.0.0
DATABASE_URL=postgresql://fastapi:<database_password>@localhost/fastapi_db
```

Validate the `fastapi-tutorial` service:

```bash
systemctl status fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl cat fastapi-tutorial
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl show fastapi-tutorial \
  --property=User,WorkingDirectory,ExecStart,Restart,Environment
```

Verify the unit values:

```bash
grep '^After=' /etc/systemd/system/fastapi-tutorial.service
grep '^User=' /etc/systemd/system/fastapi-tutorial.service
grep '^WorkingDirectory=' /etc/systemd/system/fastapi-tutorial.service
grep '^ExecStart=' /etc/systemd/system/fastapi-tutorial.service
grep '^Restart=' /etc/systemd/system/fastapi-tutorial.service
```

Expected values include:

```text
After=network.target postgresql.service
User=root
WorkingDirectory=/opt/fastapi-tutorial
Restart=always
```

The `ExecStart` value must invoke:

```text
/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Check the FastAPI endpoint and listener:

```bash
curl -I http://127.0.0.1:8000/
curl -sS http://127.0.0.1:8000/
ss -ltnp | grep ':8000'
pgrep -af '/opt/fastapi-tutorial/venv/bin/uvicorn'
```

Expected results:

- `fastapi-tutorial` is enabled and active.
- A Uvicorn process is running from `/opt/fastapi-tutorial/venv/bin/uvicorn`.
- The service listens on `0.0.0.0:8000`.
- The root endpoint responds without a connection failure.

### `postgresql` database checks

```bash
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
sudo -u postgres psql -c "SELECT version();"
sudo -u postgres psql -c "\du fastapi"
sudo -u postgres psql -c "\l fastapi_db"
sudo -u postgres psql -d fastapi_db -c "SELECT current_database();"
sudo -u postgres psql -d fastapi_db -c "SELECT current_user;"
```

Verify application credentials:

```bash
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT 1;"
```

Verify the database owner:

```bash
sudo -u postgres psql -tAc \
  "SELECT pg_catalog.pg_get_userbyid(datdba) FROM pg_database WHERE datname='fastapi_db';"
```

Expected owner:

```text
fastapi
```

Verify the PostgreSQL listener:

```bash
ss -ltnp | grep ':5432'
```

Expected results:

- `postgresql` is enabled and active.
- User `fastapi` exists.
- Database `fastapi_db` exists.
- Database owner is `fastapi`.
- User `fastapi` can authenticate locally and execute `SELECT 1`.
- PostgreSQL listens on port `5432`.

### Service logs and process checks

```bash
journalctl -u postgresql --no-pager -n 50
journalctl -u fastapi-tutorial --no-pager -n 100
systemctl show fastapi-tutorial --property=MainPID,ExecMainStatus,MemoryCurrent
```

Look for:

- PostgreSQL startup failures.
- Authentication failures for `fastapi`.
- Missing Python modules.
- Uvicorn import errors involving `app.main:app`.
- Port binding errors on ports `5432` or `8000`.
- Permission errors involving `/opt/fastapi-tutorial`.
- Incorrect service ordering or missing systemd reloads.

Confirm that `fastapi-tutorial` has working directory `/opt/fastapi-tutorial`, uses `/opt/fastapi-tutorial/venv/bin` in its environment path, listens on port `8000`, and can access the local `fastapi_db` database.