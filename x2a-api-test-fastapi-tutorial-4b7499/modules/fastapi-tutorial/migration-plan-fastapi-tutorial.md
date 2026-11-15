---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI tutorial application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` under `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, and application dependencies; creates a Python virtual environment; configures PostgreSQL database `fastapi_db` and user `fastapi`; writes an environment file; and manages the `fastapi-tutorial` systemd service. The application listens on TCP port `8000` and PostgreSQL uses its default port, `5432`. The PostgreSQL password is hardcoded in the Chef recipe and must be migrated to Ansible Vault, an Ansible Automation Platform credential, or another secret manager.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application service
  - Location/Path: `/opt/fastapi-tutorial`
  - Git repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Git revision: `main`
  - Python virtual environment: `/opt/fastapi-tutorial/venv`
  - Startup command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Bind address: `0.0.0.0`
  - Port/Socket: TCP `8000`
  - Runtime user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Restart policy: `Restart=always`
  - Service dependency: `postgresql.service`

- **fastapi_db**: PostgreSQL application database
  - Database user: `fastapi`
  - Database owner: `fastapi`
  - Database host: `localhost`
  - Port/Socket: PostgreSQL TCP port `5432`
  - Database URL: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
  - Privileges: `fastapi` receives all privileges on `fastapi_db`

There are no collection attributes or `.each` iterations. The recipe configures exactly one FastAPI application service and one PostgreSQL database.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**
```text
recipes/default.rb
```

**Providers:**
```text
```

No custom resources or provider files are used.

**Templates:**
```text
```

No `.erb` templates are used. Configuration files are created directly with Chef `file` resources.

**Attributes:**
```text
```

No attribute files are used by the analyzed execution flow.

**Files:**
```text
```

No static files are deployed with `cookbook_file` or `remote_file`.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - This is the only recipe and performs package installation, application deployment, PostgreSQL setup, configuration generation, and service startup.
   - On RHEL/Fedora systems, when `platform_family?('fedora', 'rhel')` is true, installs `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, and `libpq-devel`.
   - On non-RHEL/Fedora systems, installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - On RHEL/Fedora systems, runs `postgresql-setup --initdb` through `execute[initialize_postgresql]`, guarded by `/var/lib/pgsql/data/PG_VERSION`.
   - Creates `/opt/fastapi-tutorial` as `root:root` with mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates `/opt/fastapi-tutorial/venv` with `python3 -m venv /opt/fastapi-tutorial/venv`, guarded by the virtual-environment path.
   - Installs dependencies from `/opt/fastapi-tutorial/requirements.txt` using `/opt/fastapi-tutorial/venv/bin/pip` with `/opt/fastapi-tutorial` as the working directory.
   - Enables and starts the `postgresql` service.
   - Creates PostgreSQL role `fastapi` with password `fastapi_password`, database `fastapi_db` owned by `fastapi`, and grants all privileges on `fastapi_db` to `fastapi`.
   - Creates `/opt/fastapi-tutorial/.env` as `root:root` with mode `0644`, containing:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Creates `/etc/systemd/system/fastapi-tutorial.service` as `root:root` with mode `0644`, containing:
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
   - When `/etc/systemd/system/fastapi-tutorial.service` changes, immediately runs `systemctl daemon-reload` through `execute[systemd_reload]`.
   - Enables and starts the `fastapi-tutorial` systemd service.
   - Execution order is: platform packages, PostgreSQL initialization where applicable, application directory, Git repository, virtual environment, Python dependencies, PostgreSQL service, PostgreSQL role and database, `.env`, systemd unit, systemd reload when required, and FastAPI service.
   - There are no `.each` loops to expand.

## Dependencies

**External cookbook dependencies**: None listed in the provided metadata.

**Supported platforms**:
- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**System package dependencies**:

RHEL/Fedora:
- `python3`
- `python3-pip`
- `git`
- `postgresql-server`
- `postgresql-contrib`
- `libpq-devel`

Debian/Ubuntu and other non-RHEL/Fedora systems:
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

**Detection Summary**: 2 credential references detected in 1 recipe file. Both references represent the same PostgreSQL credential.

**Source**:
- **Provider**: Hardcoded in the Chef recipe
- **URL**: No external vault or secret manager URL detected
- **Path**: No data bag, vault path, CyberArk path, or secret-manager path detected
- **Source file**: `cookbooks/fastapi-tutorial/recipes/default.rb`

### PostgreSQL password for database creation

- **Variable(s)**: None; literal value is `fastapi_password`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Location**: Line 49
- **Current storage**: Hardcoded in an `execute` resource
- **Usage context**: `CREATE USER fastapi WITH PASSWORD ...`

### PostgreSQL password in application connection string

- **Variable(s)**: `DATABASE_URL`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Location**: Line 61
- **Current storage**: Hardcoded inside `.env` file content
- **Usage context**: Application connection to the local PostgreSQL database
- **Value pattern**: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`

No Chef Vault, data bag, encrypted data bag, Conjur, CyberArk, or environment-variable-based secret retrieval was detected. No SSL/TLS certificate, private key, API token, or external service credential was detected.

The migration must store the PostgreSQL password in Ansible Vault or an AAP credential, generate the database task and `DATABASE_URL` from the same protected variable, and preferably protect `.env` with mode `0600`.

## Checks for the Migration

**Files to verify**:
- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- `/var/lib/pgsql/data/PG_VERSION` on RHEL/Fedora

**Database objects to verify**:
- PostgreSQL role `fastapi`
- PostgreSQL database `fastapi_db`
- Database owner `fastapi`
- All privileges on `fastapi_db` granted to `fastapi`

**Service endpoints to check**:
- `fastapi-tutorial`: TCP port `8000`
- `fastapi_db`: local PostgreSQL TCP port `5432`, or the PostgreSQL Unix socket when TCP is disabled

**Templates rendered**: 0

The cookbook creates these files directly with Chef `file` resources:
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

## Pre-flight checks

### Platform and package checks

```bash
cat /etc/os-release

dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev 2>/dev/null
rpm -q python3 python3-pip git postgresql-server postgresql-contrib libpq-devel 2>/dev/null
```

On RHEL/Fedora:

```bash
test -f /var/lib/pgsql/data/PG_VERSION
```

Expected result: exit code `0`.

### fastapi-tutorial application checks

```bash
ls -ld /opt/fastapi-tutorial
stat -c '%U:%G %a %n' /opt/fastapi-tutorial
git -C /opt/fastapi-tutorial remote -v
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
test -f /opt/fastapi-tutorial/requirements.txt

test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip list

systemctl cat fastapi-tutorial
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
curl -I http://127.0.0.1:8000/
curl -sS http://127.0.0.1:8000/
ss -tlnp | grep ':8000'
```

Verify:
- `/opt/fastapi-tutorial` is owned by `root:root` with mode `755`.
- The repository is `https://github.com/dibanez/fastapi_tutorial.git` at revision `main`.
- `requirements.txt`, the virtual environment, and its dependencies exist.
- The unit is enabled and active.
- Uvicorn runs from `/opt/fastapi-tutorial/venv/bin/uvicorn`.
- The service listens on `0.0.0.0:8000` and returns an HTTP response.

### fastapi_db PostgreSQL checks

```bash
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql

sudo -u postgres psql -tAc "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"
sudo -u postgres psql -tAc "SELECT datname FROM pg_database WHERE datname = 'fastapi_db';"
sudo -u postgres psql -tAc "SELECT pg_catalog.pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"
```

Expected output:
```text
fastapi
fastapi_db
fastapi
```

Verify PostgreSQL connectivity using a protected secret injection method:

```bash
PGPASSWORD='REDACTED' psql -h localhost -U fastapi -d fastapi_db -c "SELECT version();"
PGPASSWORD='REDACTED' psql -h localhost -U fastapi -d fastapi_db -c "SELECT current_database(), current_user;"
```

Expected values:
- PostgreSQL returns its version.
- The database is `fastapi_db`.
- The connected user is `fastapi`.

Check the PostgreSQL endpoint:

```bash
ss -tlnp | grep ':5432'
find /var/run/postgresql /tmp -maxdepth 2 -type s -name '.s.PGSQL.5432' -print 2>/dev/null
```

### Configuration and service checks

```bash
stat -c '%U:%G %a %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' /opt/fastapi-tutorial/.env

systemctl show fastapi-tutorial | grep -E 'MainPID|Restart|SubState|ActiveState'
systemctl restart fastapi-tutorial
systemctl is-active fastapi-tutorial

journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u postgresql --no-pager -n 100
```

Verify `.env` contains `PROJECT_NAME`, `API_VERSION`, and `DATABASE_URL`; redact the password from operational output. Verify successful Uvicorn startup, no `app.main:app` import errors, no database authentication failures, and no PostgreSQL startup errors. The FastAPI service must return to `active` after restart and continue listening on port `8000`.