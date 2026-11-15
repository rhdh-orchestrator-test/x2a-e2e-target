---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI tutorial application from `https://github.com/dibanez/fastapi_tutorial.git` into `/opt/fastapi-tutorial`, installs platform-specific Python, Git, PostgreSQL, and PostgreSQL development dependencies, creates a Python virtual environment, installs application requirements, provisions the `fastapi` PostgreSQL user and `fastapi_db` database, writes an application environment file, and manages the `fastapi-tutorial` systemd service on port `8000`. The cookbook supports Ubuntu and CentOS/RHEL-style systems and contains one recipe with no custom resources, templates, attributes, static files, or collection iterations.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application server
  - Application path: `/opt/fastapi-tutorial`
  - Source repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Repository revision: `main`
  - Python virtual environment: `/opt/fastapi-tutorial/venv`
  - Application command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Listen address: `0.0.0.0`
  - Listen port: `8000`
  - systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - systemd user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Restart policy: `Restart=always`
  - PostgreSQL dependency: `postgresql.service`

- **fastapi_db**: PostgreSQL application database
  - Owner: `fastapi`
  - Host: `localhost`
  - Port: `5432`
  - Connection URL: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
  - Database privilege: `ALL` granted to `fastapi`

- **fastapi**: PostgreSQL application database user
  - Password: `fastapi_password` in the original Chef implementation
  - Owner of: `fastapi_db`
  - Database privilege: `ALL` on `fastapi_db`

There are no collection attributes or `.each` iterations in the execution tree.

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

The cookbook uses inline Chef `file` resources for the `.env` file and systemd unit. These are not static files under a `files/` directory.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Contains the complete implementation.
   - Has no `include_recipe` calls, custom resources, providers, templates, attributes, or static files.
   - Has no `.each` loops or iterable configuration items.

2. **Platform-specific package installation** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - On Fedora/RHEL systems, installs:
     - `python3`
     - `python3-pip`
     - `git`
     - `postgresql-server`
     - `postgresql-contrib`
     - `libpq-devel`
   - On non-Fedora/RHEL systems, including supported Ubuntu systems, installs:
     - `python3`
     - `python3-pip`
     - `python3-venv`
     - `git`
     - `postgresql`
     - `postgresql-contrib`
     - `libpq-dev`

3. **PostgreSQL initialization on Fedora/RHEL** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Runs `execute[initialize_postgresql]`.
   - Executes `postgresql-setup --initdb`.
   - Runs only when `/var/lib/pgsql/data/PG_VERSION` does not exist.
   - This initialization behavior applies only to the Fedora/RHEL branch.

4. **Application directory creation** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/opt/fastapi-tutorial`.
   - Sets owner and group to `root`.
   - Sets mode to `0755`.
   - Enables recursive directory creation.

5. **Repository synchronization** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` into `/opt/fastapi-tutorial`.
   - Uses revision `main`.
   - The repository is required before dependency installation because `/opt/fastapi-tutorial/requirements.txt` is used later.

6. **Python virtual environment creation** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Runs `execute[create_venv]`.
   - Executes `python3 -m venv /opt/fastapi-tutorial/venv`.
   - Runs only when `/opt/fastapi-tutorial/venv` does not exist.

7. **Python dependency installation** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Runs `execute[install_dependencies]`.
   - Executes `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt`.
   - Uses `/opt/fastapi-tutorial` as the working directory.
   - Ansible may use `ansible.builtin.pip` with virtual environment `/opt/fastapi-tutorial/venv` and requirements file `/opt/fastapi-tutorial/requirements.txt`.

8. **PostgreSQL service startup** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Enables and starts `service[postgresql]`.
   - Uses the service name `postgresql`.

9. **PostgreSQL user and database creation** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Runs `execute[create_db_user]` as the `postgres` operating-system user.
   - Creates PostgreSQL user `fastapi` with password `fastapi_password`.
   - Creates database `fastapi_db` owned by `fastapi`.
   - Grants `ALL` privileges on `fastapi_db` to `fastapi`.
   - The original commands append `|| true`, allowing failures to be ignored.
   - The Ansible migration should use `community.postgresql.postgresql_user`, `community.postgresql.postgresql_db`, and `community.postgresql.postgresql_privs` for idempotent behavior.
   - Database operations must remain in this order: user creation, database creation, and privilege grant.

10. **Application environment file creation** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
    - Creates `/opt/fastapi-tutorial/.env`.
    - Sets owner and group to `root`.
    - Sets mode to `0644`.
    - Writes:
      ```dotenv
      PROJECT_NAME="FastAPI Tutorial"
      API_VERSION=1.0.0
      DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
      ```
    - The migrated password should come from Ansible Vault.
    - The original mode makes the password readable by local users; a mode of `0600` may be used if the application can read the file as its configured service user.

11. **systemd unit creation** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
    - Creates `/etc/systemd/system/fastapi-tutorial.service`.
    - Sets owner and group to `root`.
    - Sets mode to `0644`.
    - Writes:
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
    - The unit declares ordering after `network.target` and `postgresql.service`.
    - Changes notify `execute[systemd_reload]` immediately.

12. **systemd reload** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
    - Runs `execute[systemd_reload]`.
    - Executes `systemctl daemon-reload`.
    - Has action `nothing` and runs only when notified by the systemd unit file resource.

13. **FastAPI service startup** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
    - Enables and starts `service[fastapi-tutorial]`.
    - Starts after the repository, virtual environment, Python requirements, PostgreSQL service, database user, database, `.env` file, systemd unit, and systemd reload are complete.
    - Runs as `root`.
    - Starts Uvicorn on `0.0.0.0:8000`.
    - Uses `Restart=always`.

## Dependencies

**External cookbook dependencies**: None listed in `metadata.rb`.

**Supported platforms**:
- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**System package dependencies**:

Fedora/RHEL:
- `python3`
- `python3-pip`
- `git`
- `postgresql-server`
- `postgresql-contrib`
- `libpq-devel`

Debian/Ubuntu:
- `python3`
- `python3-pip`
- `python3-venv`
- `git`
- `postgresql`
- `postgresql-contrib`
- `libpq-dev`

**Python dependency source**: `/opt/fastapi-tutorial/requirements.txt`

**Service dependencies**:
- `postgresql`
- `fastapi-tutorial`

**Ansible collection dependency**:
- `community.postgresql` for PostgreSQL user, database, and privilege management

## Credentials

**Detection Summary**: 1 logical database credential detected across `cookbooks/fastapi-tutorial/recipes/default.rb`. The same hardcoded password is used in the PostgreSQL user creation command and the application database URL.

**Source**:
- **Provider**: Hardcoded in the Chef recipe
- **URL**: None
- **Path**: None

### PostgreSQL database password

- **Variable(s)**:
  - No Chef attribute variable
  - Hardcoded password literal: `fastapi_password`
  - Application variable: `DATABASE_URL`
  - Database user: `fastapi`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the PostgreSQL `execute` resource and inline `.env` content
- **Usage context**:
  - PostgreSQL user creation:
    ```sql
    CREATE USER fastapi WITH PASSWORD 'fastapi_password';
    ```
  - Application connection string:
    ```text
    DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
    ```

The Ansible migration should store the password in Ansible Vault, such as `fastapi_database_password`, and use the vaulted value in both PostgreSQL tasks and the `.env` file.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secret lookups, TLS certificates, private keys, API keys, or external secret-manager integrations were detected.

## Checks for the Migration

**Files to verify**:
- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/.git`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- RHEL/Fedora PostgreSQL data directory: `/var/lib/pgsql/data`
- Debian/Ubuntu distribution-managed PostgreSQL data path

**Service endpoints to check**:
- `fastapi-tutorial`: `0.0.0.0:8000`
- `fastapi_db`: `localhost:5432`
- PostgreSQL local Unix socket: distribution-managed socket path

**Templates rendered**:
- None; no `.erb` templates exist.

**Inline configuration files created**:
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Expected systemd behavior**:
- `fastapi-tutorial.service` is enabled and active.
- The service runs as `root`.
- The service launches Uvicorn.
- The process listens on port `8000`.
- The service uses `/opt/fastapi-tutorial` as its working directory.
- The service restarts after an unexpected exit because `Restart=always` is configured.
- `postgresql.service` is enabled and active.

## Pre-flight checks:

```bash
# Platform and package checks
python3 --version
python3 -m pip --version
git --version
psql --version

# Fedora/RHEL package checks
rpm -q python3
rpm -q python3-pip
rpm -q git
rpm -q postgresql-server
rpm -q postgresql-contrib
rpm -q libpq-devel

# Debian/Ubuntu package checks
dpkg -s python3
dpkg -s python3-pip
dpkg -s python3-venv
dpkg -s git
dpkg -s postgresql
dpkg -s postgresql-contrib
dpkg -s libpq-dev

# PostgreSQL instance: postgresql
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
ss -ltnp | grep ':5432'

# PostgreSQL user and database: fastapi and fastapi_db
sudo -u postgres psql -tAc "SELECT usename FROM pg_catalog.pg_user WHERE usename = 'fastapi';"
sudo -u postgres psql -tAc "SELECT datname, pg_catalog.pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"
sudo -u postgres psql -d fastapi_db -tAc "SELECT has_database_privilege('fastapi', 'fastapi_db', 'CONNECT');"

# Application repository: fastapi-tutorial
stat -c '%A %U:%G %n' /opt/fastapi-tutorial
test -d /opt/fastapi-tutorial/.git
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
test -f /opt/fastapi-tutorial/requirements.txt

# Python environment: fastapi-tutorial
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip list

# Environment file: fastapi-tutorial
stat -c '%A %U:%G %n' /opt/fastapi-tutorial/.env
grep '^PROJECT_NAME=' /opt/fastapi-tutorial/.env
grep '^API_VERSION=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env

# systemd instance: fastapi-tutorial
systemctl cat fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl show fastapi-tutorial --property=User,WorkingDirectory,ExecStart,Restart
grep '^Description=' /etc/systemd/system/fastapi-tutorial.service
grep '^After=' /etc/systemd/system/fastapi-tutorial.service
grep '^User=' /etc/systemd/system/fastapi-tutorial.service
grep '^WorkingDirectory=' /etc/systemd/system/fastapi-tutorial.service
grep '^Environment=' /etc/systemd/system/fastapi-tutorial.service
grep '^ExecStart=' /etc/systemd/system/fastapi-tutorial.service
grep '^Restart=' /etc/systemd/system/fastapi-tutorial.service

# FastAPI instance: fastapi-tutorial
systemctl status fastapi-tutorial
pgrep -af 'uvicorn app.main:app'
ss -ltnp | grep ':8000'
curl -i http://127.0.0.1:8000/
curl -i http://localhost:8000/

# PostgreSQL connection for fastapi_db
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_database(), current_user;"

# Service logs for postgresql and fastapi-tutorial
journalctl -u postgresql --no-pager -n 100
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u postgresql --no-pager | grep -E 'ERROR|FATAL|failed'
journalctl -u fastapi-tutorial --no-pager | grep -E 'ERROR|Traceback|Failed|failed'

# Application-to-database connectivity
PGPASSWORD='fastapi_password' \
  /opt/fastapi-tutorial/venv/bin/python -c \
  "import psycopg2; conn=psycopg2.connect('postgresql://fastapi:fastapi_password@localhost/fastapi_db'); print(conn.get_dsn_parameters()['dbname']); conn.close()"

# Change and restart behavior for fastapi-tutorial
systemctl daemon-reload
systemctl restart fastapi-tutorial
systemctl is-active fastapi-tutorial
curl -i http://127.0.0.1:8000/
```

Expected repository branch:

```text
main
```

Expected database owner output should contain:

```text
fastapi_db|fastapi
```

Expected database connection privilege output:

```text
t
```

Expected non-secret environment values:

```text
PROJECT_NAME="FastAPI Tutorial"
API_VERSION=1.0.0
```

The full `DATABASE_URL` must not be printed in shared logs because it contains the database password. Validate it using a redacted or controlled check.

Expected FastAPI command:

```text
ExecStart=/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
```

If the deployed requirements use a PostgreSQL Python driver other than `psycopg2`, use that driver for the connectivity test while preserving these connection values:

```text
User: fastapi
Database: fastapi_db
Host: localhost
Port: 5432
```

After changing the systemd unit or `.env` through Ansible, verify that the role writes the changed file, reloads systemd when the unit changes, restarts or starts `fastapi-tutorial`, leaves PostgreSQL enabled and active, and preserves the `fastapi` user and `fastapi_db` database.