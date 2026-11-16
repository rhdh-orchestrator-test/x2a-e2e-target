---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the `dibanez/fastapi_tutorial` FastAPI application from Git, installs Python, PostgreSQL, Git, and application dependencies, creates a Python virtual environment, initializes and configures PostgreSQL, writes an environment file containing the database connection string, and runs Uvicorn under systemd on port `8000`. It configures one application instance named `fastapi-tutorial`, with PostgreSQL database `fastapi_db` and user `fastapi`. No custom resources, templates, attribute files, or iteration loops are present.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application served by Uvicorn
  - Location/Path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Working directory: `/opt/fastapi-tutorial`
  - Service user: `root`
  - Application command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Port/Socket: `0.0.0.0:8000`
  - systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Restart policy: `always`

- **postgresql**: PostgreSQL service supporting the FastAPI application
  - Database: `fastapi_db`
  - Database user: `fastapi`
  - Database owner: `fastapi`
  - Database host: `localhost`
  - Port/Socket: Local PostgreSQL service, typically port `5432`, with a distribution-dependent Unix socket
  - Connection string: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`

No `.each` loops or collection-based resource iterations are present.

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

The `.env` file and systemd unit are generated directly by Chef `file` resources rather than templates or static cookbook files.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Selects packages based on `platform_family?('fedora', 'rhel')`.
   - On Fedora/RHEL, installs `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, and `libpq-devel`.
   - On non-Fedora/RHEL systems, installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - On Fedora/RHEL, initializes PostgreSQL with `postgresql-setup --initdb`, guarded by `/var/lib/pgsql/data/PG_VERSION`.
   - Creates `/opt/fastapi-tutorial` as `root:root` with mode `0755`.
   - Checks out `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates `/opt/fastapi-tutorial/venv` with `python3 -m venv`, guarded by the virtual-environment path.
   - Installs `/opt/fastapi-tutorial/requirements.txt` into the virtual environment.
   - Enables and starts the `postgresql` service.
   - Creates PostgreSQL role `fastapi` with password `fastapi_password`.
   - Creates database `fastapi_db` owned by `fastapi`.
   - Grants all privileges on `fastapi_db` to `fastapi`.
   - Creates `/opt/fastapi-tutorial/.env` as `root:root` with mode `0644`, containing:
     - `PROJECT_NAME="FastAPI Tutorial"`
     - `API_VERSION=1.0.0`
     - `DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db`
   - Creates `/etc/systemd/system/fastapi-tutorial.service` as `root:root` with mode `0644`.
   - Configures the unit to run as `root`, use `/opt/fastapi-tutorial` as its working directory, use `/opt/fastapi-tutorial/venv/bin` in `PATH`, start Uvicorn on `0.0.0.0:8000`, restart automatically, and start after `network.target` and `postgresql.service`.
   - Immediately notifies `execute[systemd_reload]` when the systemd unit changes.
   - Runs `systemctl daemon-reload` only when notified.
   - Enables and starts the `fastapi-tutorial` service.
   - Iterations: None.

## Dependencies

**External cookbook dependencies**: None listed in the provided metadata or execution tree.

**System package dependencies**:

- Fedora/RHEL:
  - `python3`
  - `python3-pip`
  - `git`
  - `postgresql-server`
  - `postgresql-contrib`
  - `libpq-devel`
- Non-Fedora/RHEL:
  - `python3`
  - `python3-pip`
  - `python3-venv`
  - `git`
  - `postgresql`
  - `postgresql-contrib`
  - `libpq-dev`

**Application dependency source**: `/opt/fastapi-tutorial/requirements.txt`, obtained from `https://github.com/dibanez/fastapi_tutorial.git`.

**Service dependencies**:

- `postgresql`
- `fastapi-tutorial`
- The FastAPI systemd unit declares `After=network.target postgresql.service`.

## Credentials

**Detection Summary**: 1 credential detected in 1 recipe file. The credential is used by the PostgreSQL role creation command and embedded in the generated database connection string.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None
- **Path**: None
- **Source file**: `cookbooks/fastapi-tutorial/recipes/default.rb`

### PostgreSQL Database Password

- **Variable(s)**:
  - No Chef attribute variable
  - Literal password: `fastapi_password`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded plaintext in the recipe
- **Usage context**:
  - Sets the password for PostgreSQL user `fastapi`.
  - Is embedded in `DATABASE_URL` as `postgresql://fastapi:fastapi_password@localhost/fastapi_db`.

The Ansible migration should store this value in Ansible Vault, such as `fastapi_db_password`, and use the vaulted value in both the PostgreSQL role task and the generated `.env` file.

### Other secret sources

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, `conjur_variable`, CyberArk data bags, `node['vault']`, `node['secrets']`, environment-variable lookups, TLS certificate or private-key files, API keys, or tokens were detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- Fedora/RHEL PostgreSQL data directory: `/var/lib/pgsql/data/`
- Non-Fedora/RHEL PostgreSQL distribution-specific data directory

**Service endpoints to check**:

- `fastapi-tutorial`: HTTP endpoint `http://127.0.0.1:8000/`
- `fastapi-tutorial`: TCP listener `0.0.0.0:8000`
- `postgresql`: local PostgreSQL connection, typically port `5432`
- `postgresql`: default local Unix socket, distribution-dependent

**Templates rendered**: None.

**Generated configuration files**:

- `/opt/fastapi-tutorial/.env`: generated once by `file[/opt/fastapi-tutorial/.env]`
- `/etc/systemd/system/fastapi-tutorial.service`: generated once by `file[/etc/systemd/system/fastapi-tutorial.service]`

## Pre-flight checks

```bash
# Verify installed packages and runtimes
python3 --version
python3 -m pip --version
git --version

# Verify the fastapi-tutorial application checkout
test -d /opt/fastapi-tutorial
git -C /opt/fastapi-tutorial rev-parse --is-inside-work-tree
git -C /opt/fastapi-tutorial branch --show-current
test -f /opt/fastapi-tutorial/requirements.txt

# Verify the fastapi-tutorial virtual environment
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn

# Verify the fastapi-tutorial environment file
stat -c '%a %U:%G %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' /opt/fastapi-tutorial/.env

# Check the postgresql service
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql

# Verify the fastapi PostgreSQL role and fastapi_db database
sudo -u postgres psql -tAc "SELECT usename FROM pg_user WHERE usename = 'fastapi';"
sudo -u postgres psql -tAc "SELECT datname FROM pg_database WHERE datname = 'fastapi_db';"
sudo -u postgres psql -d fastapi_db -tAc "SELECT current_database(), current_user;"

# Verify PostgreSQL credentials for fastapi_db
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT version();"

# Verify the fastapi-tutorial systemd unit
test -f /etc/systemd/system/fastapi-tutorial.service
stat -c '%a %U:%G %n' /etc/systemd/system/fastapi-tutorial.service
systemctl daemon-reload
systemctl status fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial

# Validate fastapi-tutorial unit settings
systemctl cat fastapi-tutorial
systemctl show fastapi-tutorial \
  -p User \
  -p WorkingDirectory \
  -p ExecStart \
  -p Restart

# Check the FastAPI endpoint and listening port
curl -i http://127.0.0.1:8000/
ss -tlnp | grep ':8000'

# Verify the Uvicorn process
ps aux | grep '[u]vicorn app.main:app'

# Review service logs
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u postgresql --no-pager -n 100

# Verify ownership and permissions
ls -ld /opt/fastapi-tutorial
ls -l /opt/fastapi-tutorial/.env
ls -l /etc/systemd/system/fastapi-tutorial.service
```

Expected results:

- `/opt/fastapi-tutorial` is a valid Git checkout containing `requirements.txt`.
- The virtual environment contains executable Python, pip, and Uvicorn binaries.
- `.env` is owned by `root:root` with mode `0644` and contains `PROJECT_NAME`, `API_VERSION`, and `DATABASE_URL`.
- `postgresql` is enabled and active.
- Role `fastapi` and database `fastapi_db` exist, with `fastapi` as the database owner.
- PostgreSQL accepts authenticated connections for `fastapi` to `fastapi_db`.
- `fastapi-tutorial` is enabled and active.
- The systemd unit uses `User=root`, working directory `/opt/fastapi-tutorial`, Uvicorn at `/opt/fastapi-tutorial/venv/bin/uvicorn`, module `app.main:app`, host `0.0.0.0`, port `8000`, and restart policy `always`.
- The FastAPI application returns an HTTP response and listens on port `8000`.
- The application and PostgreSQL logs contain no authentication, import, dependency, startup, or bind errors.
- `/opt/fastapi-tutorial` is owned by `root:root` with mode `0755`.
- The systemd unit is owned by `root:root` with mode `0644`.