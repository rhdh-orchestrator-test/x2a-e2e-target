---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, PostgreSQL development dependencies, and application requirements; creates a Python virtual environment; configures the `fastapi` PostgreSQL user and `fastapi_db` database; writes an application environment file; and manages the `fastapi-tutorial` systemd service on port `8000`. The cookbook contains one recipe, no providers or attribute files, no collection iterations, and no repeated configured instances.

## Service Type and Instances

**Service Type**: Application Server with PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application server
  - Source repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Location/Path: `/opt/fastapi-tutorial`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Application module: `app.main:app`
  - Runtime user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Bind address: `0.0.0.0`
  - Port/Socket: `8000`
  - Restart policy: `Restart=always`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`

- **postgresql**: PostgreSQL database service
  - Service state: Enabled and started
  - Database user: `fastapi`
  - Database password: `fastapi_password`
  - Database name: `fastapi_db`
  - Database owner: `fastapi`
  - Privileges: All privileges on `fastapi_db` granted to `fastapi`
  - Connection host: `localhost`
  - Connection port: PostgreSQL default port, normally `5432`
  - Connection string: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`

No `.each` loops, collection attributes, or repeated configured instances are present.

## File Structure

Only files used by the execution tree are listed below.

**Recipes:**
```text
recipes/default.rb
```

**Providers:**
```text
```

**Templates:**
```text
```

**Attributes:**
```text
```

**Files:**
```text
```

The cookbook uses inline `file` resources rather than `.erb` templates or static cookbook files. No provider or attribute files are used.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the exact system package set:
     - `python3`
     - `python3-pip`
     - `python3-venv`
     - `git`
     - `postgresql`
     - `postgresql-contrib`
     - `libpq-dev`
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates the virtual environment with `python3 -m venv /opt/fastapi-tutorial/venv`, only when `/opt/fastapi-tutorial/venv` does not already exist.
   - Installs dependencies from `/opt/fastapi-tutorial/requirements.txt` using `/opt/fastapi-tutorial/venv/bin/pip` with `/opt/fastapi-tutorial` as the working directory.
   - Enables and starts the `postgresql` service.
   - Creates the PostgreSQL user `fastapi` with password `fastapi_password`.
   - Creates the PostgreSQL database `fastapi_db` owned by `fastapi`.
   - Grants all privileges on `fastapi_db` to `fastapi`.
   - Uses PostgreSQL modules in Ansible to provide idempotent database management rather than reproducing the original shell commands' broad `|| true` error suppression.
   - Writes `/opt/fastapi-tutorial/.env` with owner `root`, group `root`, and mode `0644`:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Deploys `/etc/systemd/system/fastapi-tutorial.service` with owner `root`, group `root`, and mode `0644`:
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
   - Reloads systemd immediately when `/etc/systemd/system/fastapi-tutorial.service` changes. The Ansible migration must flush the handler immediately after deploying the unit, or explicitly run `daemon_reload: true` before enabling or starting `fastapi-tutorial`.
   - Enables and starts the `fastapi-tutorial` systemd service after the unit is deployed and systemd has been reloaded.
   - Preserves the following systemd behavior:
     - Starts after `network.target`.
     - Starts after `postgresql.service`.
     - Runs Uvicorn from `/opt/fastapi-tutorial/venv/bin`.
     - Loads `app.main:app`.
     - Binds to `0.0.0.0:8000`.
     - Restarts automatically with `Restart=always`.
     - Runs as `root`, matching the Chef configuration. This should be reviewed for production security.

## Dependencies

**External cookbook dependencies**: None listed in the provided metadata or execution tree.

**System package dependencies**:

- `python3`
- `python3-pip`
- `python3-venv`
- `git`
- `postgresql`
- `postgresql-contrib`
- `libpq-dev`

Package names may require platform-specific mapping on CentOS/RHEL because the recipe uses Debian-style names. `libpq-dev` is required by Python packages that compile PostgreSQL client bindings.

**Service dependencies**:

- `postgresql`
- `fastapi-tutorial`

**Application dependencies**:

- Git repository: `https://github.com/dibanez/fastapi_tutorial.git`
- Git revision: `main`
- Requirements file: `/opt/fastapi-tutorial/requirements.txt`
- Application module: `app.main:app`

## Credentials

**Detection Summary**: 1 credential detected in 1 source file.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None
- **Path**: None
- **Current storage location**: Inline database command and inline `.env` content

### PostgreSQL database password

- **Variable(s)**:
  - PostgreSQL user `fastapi` password
  - `DATABASE_URL` password component: `fastapi_password`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded plaintext
- **Usage context**:
  - PostgreSQL user creation
  - PostgreSQL connection string in `/opt/fastapi-tutorial/.env`
  - Application database authentication
- **Migration handling**:
  - Store the password in Ansible Vault.
  - Use the vaulted value in `community.postgresql.postgresql_user`.
  - Use the same vaulted value when rendering `/opt/fastapi-tutorial/.env`.
  - Do not place the password in Git-managed role defaults or task files.
  - Consider changing `.env` mode from `0644` to `0600` unless exact Chef compatibility is required.

No Chef data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secret references, TLS certificates, API keys, or tokens were detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/app/main.py` or the repository's corresponding application module
- PostgreSQL data directory determined by the target distribution
- PostgreSQL service logs managed by the target operating system

**Service endpoints to check**:

- **fastapi-tutorial**: `http://127.0.0.1:8000/`, listening on `0.0.0.0:8000`
- **postgresql**: `localhost:5432`
- **postgresql Unix socket**: Distribution-dependent, commonly under `/var/run/postgresql/`

**Templates rendered**:

- No cookbook templates are rendered.
- `/opt/fastapi-tutorial/.env`: written once by `file[/opt/fastapi-tutorial/.env]`
- `/etc/systemd/system/fastapi-tutorial.service`: written once by `file[/etc/systemd/system/fastapi-tutorial.service]`

## Pre-flight checks

Run these checks after the Ansible migration.

### Package and application checks for `fastapi-tutorial`

```bash
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev
test -d /opt/fastapi-tutorial
test -d /opt/fastapi-tutorial/venv
test -f /opt/fastapi-tutorial/requirements.txt
test -f /opt/fastapi-tutorial/app/main.py
readlink -f /opt/fastapi-tutorial/venv/bin/python
/opt/fastapi-tutorial/venv/bin/pip --version
```

On RPM-based systems, use the platform package query equivalent instead of `dpkg`.

### PostgreSQL service checks for `postgresql`

```bash
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
journalctl -u postgresql --no-pager -n 100
```

Expected results:

- `postgresql` is enabled.
- `postgresql` is active.
- The service reports no startup errors.

### PostgreSQL database checks for `postgresql`

```bash
sudo -u postgres psql -tAc "SELECT usename FROM pg_catalog.pg_user WHERE usename = 'fastapi';"
sudo -u postgres psql -tAc "SELECT datname FROM pg_catalog.pg_database WHERE datname = 'fastapi_db';"
sudo -u postgres psql -tAc "SELECT pg_get_userbyid(datdba) FROM pg_catalog.pg_database WHERE datname = 'fastapi_db';"
```

Expected results:

- The first command returns `fastapi`.
- The second command returns `fastapi_db`.
- The third command returns `fastapi`.

Test application credentials and database connectivity:

```bash
PGPASSWORD='RETRIEVE_FROM_ANSIBLE_VAULT' \
psql -h localhost -U fastapi -d fastapi_db -c "SELECT 1;"
```

Expected result:

```text
 ?column?
----------
        1
```

### Environment file checks for `fastapi-tutorial`

```bash
stat -c '%U:%G %a %n' /opt/fastapi-tutorial/.env
grep '^PROJECT_NAME=' /opt/fastapi-tutorial/.env
grep '^API_VERSION=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env
```

Expected values:

- Owner and group: `root:root`
- Mode: `0644` for exact Chef compatibility
- `PROJECT_NAME="FastAPI Tutorial"`
- `API_VERSION=1.0.0`
- `DATABASE_URL` references database `fastapi_db` and user `fastapi`

Do not print the database password in migration logs or CI output.

### Systemd checks for `fastapi-tutorial`

```bash
systemctl daemon-reload
systemctl status fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl cat fastapi-tutorial
systemctl show fastapi-tutorial \
  --property=User,WorkingDirectory,ExecStart,Restart,ActiveState,SubState
```

Expected values:

- `User=root`
- `WorkingDirectory=/opt/fastapi-tutorial`
- `ExecStart` invokes `/opt/fastapi-tutorial/venv/bin/uvicorn`
- The command uses `app.main:app`
- The command binds to `0.0.0.0`
- The command uses port `8000`
- `Restart=always`
- `fastapi-tutorial` is enabled and active

### FastAPI endpoint checks for `fastapi-tutorial`

```bash
curl -I http://127.0.0.1:8000/
curl -sS http://127.0.0.1:8000/
ss -tlnp | grep ':8000'
lsof -iTCP:8000 -sTCP:LISTEN
```

Expected results:

- `fastapi-tutorial` accepts TCP connections on port `8000`.
- The HTTP response is returned by the FastAPI application.
- The exact HTTP status code depends on the repository's route definitions.
- A response rather than a connection failure confirms that Uvicorn is reachable.

### Application and service logs for `fastapi-tutorial`

```bash
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u fastapi-tutorial -f
ps aux | grep '[u]vicorn'
```

Expected results:

- A Uvicorn process runs with `app.main:app`.
- The process is managed by `fastapi-tutorial.service`.
- Python and pip resolve from `/opt/fastapi-tutorial/venv`.