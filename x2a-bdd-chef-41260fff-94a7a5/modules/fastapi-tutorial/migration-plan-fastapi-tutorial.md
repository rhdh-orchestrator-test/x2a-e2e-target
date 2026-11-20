---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, and PostgreSQL development packages; creates a Python virtual environment; installs dependencies from `requirements.txt`; creates the PostgreSQL role and database; writes an environment file containing the database connection string; and manages a systemd service named `fastapi-tutorial` listening on port `8000`.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

PostgreSQL is installed and started locally as the FastAPI application database dependency.

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application launched by Uvicorn
  - Location/Path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Service user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Start command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Listening address: `0.0.0.0`
  - Port/Socket: `8000`; PostgreSQL uses the local distribution-managed socket and normally TCP port `5432`
  - Restart policy: `always`
  - Dependency ordering: starts after `network.target` and `postgresql.service`

- **postgresql**: Local PostgreSQL database service for the FastAPI application
  - Role: Provides the `fastapi_db` database and `fastapi` PostgreSQL role
  - Database: `fastapi_db`
  - Database owner: `fastapi`
  - Port/Socket: Normally TCP port `5432` and the distribution-managed local Unix socket
  - Service unit: `postgresql`
  - Required before: PostgreSQL role/database creation and `fastapi-tutorial` startup

The cookbook does not contain collection iterations or `.each` loops. There are no additional application instances, sites, database collections, or service-instance loops to expand.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**
```text
cookbooks/fastapi-tutorial/recipes/default.rb
```

**Providers:**
```text
```

No custom Chef resource providers are used.

**Templates:**
```text
```

No `.erb` templates are rendered. The environment file and systemd unit are created with inline `file` resources.

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
   - On Fedora/RHEL, installs `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, and `libpq-devel`.
   - On other supported platforms, installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - On Fedora/RHEL, runs `postgresql-setup --initdb` only when `/var/lib/pgsql/data/PG_VERSION` does not exist.
   - The platform-specific package split must be preserved; both package sets must not be installed together.

2. **Create the application directory** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/opt/fastapi-tutorial` recursively.
   - Sets owner and group to `root`.
   - Sets mode to `0755`.

3. **Synchronize the application repository** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main`.
   - Uses `/opt/fastapi-tutorial` as the destination.
   - The repository must be synchronized before the requirements file and application module are used.

4. **Create the Python virtual environment** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Runs `python3 -m venv /opt/fastapi-tutorial/venv`.
   - Guards execution with the existence of `/opt/fastapi-tutorial/venv`.

5. **Install Python dependencies** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Runs `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt`.
   - Uses `/opt/fastapi-tutorial` as the working directory.
   - Uses the virtual environment’s `pip`.
   - Runs explicitly without a `creates` guard.

6. **Enable and start PostgreSQL** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Enables the `postgresql` service at boot.
   - Starts the `postgresql` service immediately.
   - A platform-specific PostgreSQL unit override may be required where the distribution uses a version-specific service name.

7. **Create the PostgreSQL role and database** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - As the `postgres` operating-system user, attempts:
     - `CREATE USER fastapi WITH PASSWORD 'fastapi_password';`
     - `CREATE DATABASE fastapi_db OWNER fastapi;`
     - `GRANT ALL PRIVILEGES ON DATABASE fastapi_db TO fastapi;`
   - The Chef commands suppress failures with `|| true`; the Ansible migration should preferably use `community.postgresql.postgresql_user`, `community.postgresql.postgresql_db`, and, if needed, `community.postgresql.postgresql_privs` for idempotency.
   - PostgreSQL must be running before these operations.

8. **Create the application environment file** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/opt/fastapi-tutorial/.env` once.
   - Sets owner and group to `root`.
   - Sets mode to `0644`.
   - Writes:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Ansible Vault should be used for the database password; mode `0600` is preferable if exact Chef permissions are not required.

9. **Create the systemd service unit** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/etc/systemd/system/fastapi-tutorial.service` once.
   - Sets owner and group to `root`.
   - Sets mode to `0644`.
   - Installs:
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
   - The Ansible migration should use `ansible.builtin.copy` or `ansible.builtin.template`.
   - Changes notify a systemd daemon-reload handler.

10. **Reload systemd** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
    - Defines `systemctl daemon-reload` with action `nothing`.
    - Runs immediately only when `/etc/systemd/system/fastapi-tutorial.service` changes.
    - Maps to an Ansible `ansible.builtin.systemd` handler with `daemon_reload: true`.

11. **Enable and start the FastAPI service** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
    - Enables and starts the `fastapi-tutorial` service.
    - The service starts only after the repository, virtual environment, dependencies, PostgreSQL service, PostgreSQL role, `fastapi_db` database, `.env` file, systemd unit, and daemon reload are complete.

## Dependencies

**External cookbook dependencies**: None are declared in the provided metadata.

**System package dependencies**:

**Fedora/RHEL**:
- `python3`
- `python3-pip`
- `git`
- `postgresql-server`
- `postgresql-contrib`
- `libpq-devel`

**Non-Fedora/RHEL**:
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

The requirements file is supplied by the synchronized Git repository and is installed into `/opt/fastapi-tutorial/venv`.

## Credentials

**Detection Summary**: One database credential detected across two usages in `cookbooks/fastapi-tutorial/recipes/default.rb`.

**Source**:
  - **Provider**: Hardcoded in the Chef recipe
  - **URL**: None
  - **Path**: None
  - **Storage**: Inline SQL command and inline environment-file content

### PostgreSQL application password

- **Variable(s)**: No Chef variable is used; the literal password is `fastapi_password`.
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded
- **Usage context**:
  - Used in `CREATE USER fastapi WITH PASSWORD 'fastapi_password'`.
  - Embedded in `.env` as `DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db`.
- **Associated database identity**:
  - User: `fastapi`
  - Database: `fastapi_db`
- **Migration guidance**:
  - Store the password in Ansible Vault as `fastapi_tutorial_db_password`.
  - Use the vaulted value when creating the PostgreSQL role and rendering `.env`.
  - Do not commit the literal password to the Ansible repository.
  - Consider changing `.env` permissions from `0644` to `0600`.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secret references, TLS certificates, API keys, or external secret-manager URLs were detected.

## Checks for the Migration

**Files to verify**:
- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- RHEL/Fedora PostgreSQL data directory: `/var/lib/pgsql/data`
- Non-RHEL PostgreSQL data directory: distribution-managed location
- PostgreSQL database: `fastapi_db`
- PostgreSQL role: `fastapi`

**Service endpoints to check**:
- FastAPI: `http://127.0.0.1:8000`
- FastAPI bind address: `0.0.0.0:8000`
- PostgreSQL TCP endpoint: local port `5432` when TCP listening is enabled
- PostgreSQL Unix socket: distribution-managed local socket

**Templates rendered**:
- No `.erb` templates are rendered.
- `/opt/fastapi-tutorial/.env`: inline Chef `file` resource, rendered once
- `/etc/systemd/system/fastapi-tutorial.service`: inline Chef `file` resource, rendered once

## Pre-flight checks

### Platform package and PostgreSQL initialization checks

For Fedora/RHEL:

```bash
rpm -q python3 python3-pip git postgresql-server postgresql-contrib libpq-devel
test -f /var/lib/pgsql/data/PG_VERSION
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
```

For non-Fedora/RHEL:

```bash
dpkg -s python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
```

### `fastapi-tutorial` application instance

```bash
ls -ld /opt/fastapi-tutorial
git -C /opt/fastapi-tutorial remote -v
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
git -C /opt/fastapi-tutorial rev-parse HEAD
test -f /opt/fastapi-tutorial/requirements.txt

test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip check

cd /opt/fastapi-tutorial
/opt/fastapi-tutorial/venv/bin/python -c "import app.main; print('app.main import succeeded')"
```

Verify the repository remote is `https://github.com/dibanez/fastapi_tutorial.git` and the checked-out revision corresponds to `main`.

Verify the environment file:

```bash
ls -l /opt/fastapi-tutorial/.env
grep '^PROJECT_NAME=' /opt/fastapi-tutorial/.env
grep '^API_VERSION=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env \
  | sed -E 's#(postgresql://[^:]+:)[^@]+@#\1*****@#'
```

Verify the systemd unit:

```bash
ls -l /etc/systemd/system/fastapi-tutorial.service
systemctl cat fastapi-tutorial
systemctl show fastapi-tutorial \
  --property=LoadState,ActiveState,SubState,UnitFileState,User,WorkingDirectory
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service

grep '^After=' /etc/systemd/system/fastapi-tutorial.service
grep '^User=' /etc/systemd/system/fastapi-tutorial.service
grep '^WorkingDirectory=' /etc/systemd/system/fastapi-tutorial.service
grep '^Environment=' /etc/systemd/system/fastapi-tutorial.service
grep '^ExecStart=' /etc/systemd/system/fastapi-tutorial.service
grep '^Restart=' /etc/systemd/system/fastapi-tutorial.service
```

Verify the service command is:

```text
/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Check the application service:

```bash
systemctl status fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
ps aux | grep '[u]vicorn'
ss -tlnp | grep ':8000'
curl -i http://127.0.0.1:8000/
journalctl -u fastapi-tutorial --no-pager -n 100
```

If the repository exposes a health endpoint, verify it after confirming the path:

```bash
curl -i http://127.0.0.1:8000/health
```

### `postgresql` database instance

```bash
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql

sudo -u postgres psql -tAc "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"
sudo -u postgres psql -tAc "SELECT datname FROM pg_database WHERE datname = 'fastapi_db';"
sudo -u postgres psql -d fastapi_db -c "\l+ fastapi_db"
```

Expected role and database results:

```text
fastapi
fastapi_db
```

Verify database connectivity without exposing the password in logs:

```bash
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_user, current_database();"
```

Expected values are `fastapi` for `current_user` and `fastapi_db` for `current_database`.

### Final configuration and connectivity checks

```bash
systemctl daemon-reload
systemctl restart fastapi-tutorial
systemctl is-active fastapi-tutorial
curl -i http://127.0.0.1:8000/

PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT 1;"
```

The PostgreSQL command should return `1` successfully.