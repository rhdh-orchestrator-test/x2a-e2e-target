---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`. It installs platform-specific Python, Git, and PostgreSQL dependencies, creates a Python virtual environment, installs application requirements, initializes and manages PostgreSQL, creates the `fastapi` role and `fastapi_db` database, writes the application `.env` file, and manages the application through the `fastapi-tutorial` systemd service on port `8000`. The cookbook executes one recipe and contains no custom resources, providers, templates, attributes, or static files.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI/Uvicorn application server
  - Source repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Location/Path: `/opt/fastapi-tutorial`
  - Working directory: `/opt/fastapi-tutorial`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Run user: `root`
  - Executable: `/opt/fastapi-tutorial/venv/bin/uvicorn`
  - Application target: `app.main:app`
  - Listen address: `0.0.0.0`
  - Port/Socket: TCP `8000`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Configuration file: `/opt/fastapi-tutorial/.env`
  - Restart policy: `Restart=always`

- **postgresql**: PostgreSQL database service
  - Service name: `postgresql`
  - Database user: `fastapi`
  - Database password: `fastapi_password`
  - Database name: `fastapi_db`
  - Database owner: `fastapi`
  - Connection host: `localhost`
  - Port/Socket: The recipe does not explicitly configure a port. PostgreSQL’s conventional TCP port is `5432`, and the connection string relies on PostgreSQL’s default local connection behavior.
  - Privileges: `fastapi` receives all privileges on `fastapi_db`

There are no collection attributes or `.each` iterations. The explicitly configured instances are `fastapi-tutorial` and `fastapi_db`.

## File Structure

```text
cookbooks/fastapi-tutorial/
└── recipes/
    └── default.rb
```

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

No ERB templates are rendered. Configuration files are created directly with Chef `file` resources.

**Attributes:**
```text
```

No attribute files are used.

**Files:**
```text
```

No static files are deployed with `cookbook_file` or `remote_file`.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Selects platform-specific system packages.
   - On Fedora/RHEL, installs `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, and `libpq-devel`.
   - On Debian/Ubuntu, installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - On Fedora/RHEL, runs `postgresql-setup --initdb` through `execute[initialize_postgresql]` only when `/var/lib/pgsql/data/PG_VERSION` does not exist.
   - Creates `/opt/fastapi-tutorial` as a recursive directory owned by `root:root` with mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates `/opt/fastapi-tutorial/venv` with `python3 -m venv` when the virtual-environment directory does not already exist.
   - Installs dependencies from `/opt/fastapi-tutorial/requirements.txt` using `/opt/fastapi-tutorial/venv/bin/pip`.
   - Enables and starts the `postgresql` service.
   - Creates the PostgreSQL user `fastapi` with password `fastapi_password`.
   - Creates the PostgreSQL database `fastapi_db` owned by `fastapi`.
   - Grants all privileges on `fastapi_db` to `fastapi`.
   - The Chef database commands use `|| true`, so errors are ignored and the commands are repeated on each Chef run.
   - Creates `/opt/fastapi-tutorial/.env` owned by `root:root` with mode `0644`, containing:
     - `PROJECT_NAME="FastAPI Tutorial"`
     - `API_VERSION=1.0.0`
     - `DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db`
   - Creates `/etc/systemd/system/fastapi-tutorial.service` owned by `root:root` with mode `0644`.
   - Defines the systemd service with:
     - `After=network.target postgresql.service`
     - `User=root`
     - `WorkingDirectory=/opt/fastapi-tutorial`
     - `Environment="PATH=/opt/fastapi-tutorial/venv/bin"`
     - `ExecStart=/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
     - `Restart=always`
     - `WantedBy=multi-user.target`
   - Runs `systemctl daemon-reload` immediately when the systemd unit changes through `execute[systemd_reload]`.
   - Enables and starts the `fastapi-tutorial` service.
   - No `.each` loops are present; therefore, there are no additional iterations to expand.

## Dependencies

**External cookbook dependencies**: None declared in metadata or the execution tree.

**System package dependencies**:

- **Fedora/RHEL**:
  - `python3`
  - `python3-pip`
  - `git`
  - `postgresql-server`
  - `postgresql-contrib`
  - `libpq-devel`

- **Debian/Ubuntu**:
  - `python3`
  - `python3-pip`
  - `python3-venv`
  - `git`
  - `postgresql`
  - `postgresql-contrib`
  - `libpq-dev`

**Application dependency source**: `/opt/fastapi-tutorial/requirements.txt`, installed with `/opt/fastapi-tutorial/venv/bin/pip`.

**Service dependencies**:

- `postgresql`
- `fastapi-tutorial`

**Repository dependency**:

- Repository: `https://github.com/dibanez/fastapi_tutorial.git`
- Revision: `main`

**Ansible collection dependency for PostgreSQL management**:

- `community.postgresql`

## Credentials

**Detection Summary**: 2 credential references detected in 1 recipe file. Both are hardcoded in `cookbooks/fastapi-tutorial/recipes/default.rb`. No external secret provider, data bag, Chef Vault, CyberArk, Conjur, or environment-variable secret lookup was detected.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None
- **Path**: None
- **Recommended storage**: Ansible Vault variable rather than plaintext in the playbook or generated file

### PostgreSQL user password

- **Variable/value**: `fastapi_password`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`, lines 49 and 61
- **Current storage**: Hardcoded in the database creation command and duplicated in the `.env` content
- **Usage context**:
  - Sets the password for PostgreSQL user `fastapi`
  - Appears in `DATABASE_URL`
  - Allows the FastAPI application to connect to `fastapi_db`

The Ansible migration should define the password in an encrypted Ansible Vault variable, such as `fastapi_db_password`, and use that variable for both the PostgreSQL user task and `.env` rendering.

### PostgreSQL connection string

- **Variable**: `DATABASE_URL`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`, lines 57–62
- **Current storage**: Hardcoded plaintext in `/opt/fastapi-tutorial/.env`
- **Value pattern**: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Usage context**: Application database connection configuration

The Ansible version should preserve the same connection-string structure while interpolating the vaulted password. The generated `.env` file should preferably use mode `0600` instead of `0644`, unless world-readable access is required by the application.

No TLS certificate paths, private keys, API keys, tokens, data bags, Chef Vault items, CyberArk integrations, Conjur variables, or secret-related attribute namespaces were detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- `/var/lib/pgsql/data/PG_VERSION` on Fedora/RHEL
- Debian/Ubuntu PostgreSQL data location, which is package-managed and not explicitly configured by the recipe

**Database objects to verify**:

- PostgreSQL role: `fastapi`
- PostgreSQL database: `fastapi_db`
- Database owner: `fastapi`
- All privileges granted to `fastapi`

**Service endpoints to check**:

- FastAPI HTTP endpoint: `0.0.0.0:8000`
- PostgreSQL local connection behavior
- PostgreSQL conventional TCP port: `5432`

**Systemd units to verify**:

- `postgresql`
- `fastapi-tutorial`

**Templates rendered**: None (0). The cookbook writes two configuration files directly with Chef `file` resources:

- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

## Pre-flight checks:

```bash
# Verify the fastapi-tutorial application instance
ls -ld /opt/fastapi-tutorial
ls -l /opt/fastapi-tutorial/requirements.txt
ls -ld /opt/fastapi-tutorial/venv

git -C /opt/fastapi-tutorial remote -v
git -C /opt/fastapi-tutorial branch --show-current
git -C /opt/fastapi-tutorial rev-parse HEAD

test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip list

stat -c '%U:%G %a %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' /opt/fastapi-tutorial/.env
```

Do not print the full `.env` file in shared logs because it contains the database password.

```bash
# Verify the postgresql instance
systemctl status postgresql --no-pager
systemctl is-enabled postgresql
systemctl is-active postgresql

sudo -u postgres psql -tAc \
  "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"

sudo -u postgres psql -tAc \
  "SELECT datname, pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"

PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_database(), current_user;"

sudo -u postgres psql -d fastapi_db -c "\dp"
sudo -u postgres psql -tAc \
  "SELECT has_database_privilege('fastapi', 'fastapi_db', 'CONNECT,CREATE,TEMPORARY');"
```

Expected role output:

```text
fastapi
```

Expected database and owner output:

```text
fastapi_db | fastapi
```

The privilege check should return `t`.

```bash
# Verify the fastapi-tutorial systemd unit
systemctl cat fastapi-tutorial
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service

systemctl daemon-reload
systemctl status fastapi-tutorial --no-pager
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
```

Verify these exact settings:

```text
WorkingDirectory=/opt/fastapi-tutorial
Environment="PATH=/opt/fastapi-tutorial/venv/bin"
ExecStart=/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
After=network.target postgresql.service
```

```bash
# Verify the fastapi-tutorial process and endpoint
ps aux | grep '[u]vicorn'
pgrep -af '/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app'

ss -tlnp | grep ':8000'
curl -I http://127.0.0.1:8000/

journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u fastapi-tutorial -f
```

The socket check should show a listener on TCP port `8000`. The HTTP request should return an HTTP response from the FastAPI application; the exact status code depends on the application routes.

```bash
# Verify PostgreSQL logs
journalctl -u postgresql --no-pager -n 100

# Verify Fedora/RHEL PostgreSQL initialization when applicable
test -f /var/lib/pgsql/data/PG_VERSION && cat /var/lib/pgsql/data/PG_VERSION
```

The PostgreSQL initialization marker is required on Fedora/RHEL systems after `postgresql-setup --initdb`. It is not required on Debian/Ubuntu because the recipe does not define the Debian/Ubuntu PostgreSQL data directory.