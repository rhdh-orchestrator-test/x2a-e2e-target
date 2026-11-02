---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI application from the `main` branch of `https://github.com/dibanez/fastapi_tutorial.git` into `/opt/fastapi-tutorial`. It installs Python, PostgreSQL, Git, and PostgreSQL development packages; creates a Python virtual environment; installs application dependencies; configures the local PostgreSQL role and database; writes the application environment file; and manages a systemd service running Uvicorn on `0.0.0.0:8000`. The cookbook contains one recipe, no custom resources, no templates, no loops, and no external cookbook dependencies.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application served by Uvicorn
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Location/Path: `/opt/fastapi-tutorial`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Environment file: `/opt/fastapi-tutorial/.env`
  - Application entry point: `app.main:app`
  - Process command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Port/Socket: `0.0.0.0:8000`
  - Run user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Service unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Restart policy: `Restart=always`
  - Startup ordering: After `network.target` and `postgresql.service`

- **fastapi_db**: Local PostgreSQL application database
  - Database user: `fastapi`
  - Database password: `fastapi_password`
  - Owner: `fastapi`
  - Connection host: `localhost`
  - Port/Socket: PostgreSQL default port `5432`; platform-default local Unix socket
  - Connection URL: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
  - Granted privileges: All privileges on `fastapi_db` to `fastapi`

No collection attributes or `.each` iterations are present. No additional application sites, workers, database definitions, or service instances are configured.

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

No ERB templates are rendered. Configuration is written using inline Chef `file` resources.

**Attributes:**

```text
```

No attribute files are used by the execution tree.

**Files:**

```text
```

No static files from `files/default/` or `files/` are deployed by `cookbook_file` or `remote_file`.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the system packages `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev` using one `package` resource.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates the Python virtual environment with:
     ```bash
     python3 -m venv /opt/fastapi-tutorial/venv
     ```
     The command runs only when `/opt/fastapi-tutorial/venv` does not exist.
   - Installs dependencies from `/opt/fastapi-tutorial/requirements.txt` into `/opt/fastapi-tutorial/venv` with the working directory `/opt/fastapi-tutorial`.
   - Enables and starts the `postgresql` service.
   - Creates PostgreSQL role `fastapi`, database `fastapi_db` owned by `fastapi`, and grants all privileges on `fastapi_db` to `fastapi`.
   - Writes `/opt/fastapi-tutorial/.env` with mode `0644`, owner `root`, and group `root`:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Writes `/etc/systemd/system/fastapi-tutorial.service` with mode `0644`, owner `root`, and group `root`:
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
   - Immediately notifies `execute[systemd_reload]` when the systemd unit changes.
   - Runs `systemctl daemon-reload` only when notified by the unit-file resource.
   - Enables and starts the `fastapi-tutorial` service after the repository, virtual environment, dependencies, PostgreSQL service, database objects, environment file, and systemd unit are available.
   - Resources used in execution order:
     - `package`: 1 resource containing 7 packages
     - `directory`: 1 resource
     - `git`: 1 resource
     - `execute`: 4 resources (`create_venv`, `install_dependencies`, `create_db_user`, and `systemd_reload`)
     - `service`: 2 resources (`postgresql` and `fastapi-tutorial`)
     - `file`: 2 resources (`/opt/fastapi-tutorial/.env` and `/etc/systemd/system/fastapi-tutorial.service`)
   - Iterations: None; no `.each` loops are defined.

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

**Service dependencies**:

- `postgresql`
- `fastapi-tutorial`

**Application dependency source**: `/opt/fastapi-tutorial/requirements.txt`

**Application dependency destination**: `/opt/fastapi-tutorial/venv`

The requirements file is obtained from the Git repository and installed into the Python virtual environment.

## Credentials

**Detection Summary**: 1 plaintext database credential detected in `cookbooks/fastapi-tutorial/recipes/default.rb`. No Chef Vault, encrypted data bag, data bag, CyberArk, Conjur, or external secrets-manager integration was detected.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None
- **Path**: None

### PostgreSQL Password

- **Variable(s)**:
  - PostgreSQL role password: `fastapi_password`
  - `DATABASE_URL`: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded plaintext in the recipe and written to `/opt/fastapi-tutorial/.env`
- **Usage context**:
  - Creates the PostgreSQL role `fastapi`
  - Authenticates the FastAPI application to the local PostgreSQL database
  - Populates the application `DATABASE_URL`
- **Migration guidance**: Store the value in Ansible Vault or an AAP credential/secret integration. Do not commit the plaintext value to the Ansible repository.

### PostgreSQL Username and Database Name

- **Variable(s)**:
  - Username: `fastapi`
  - Database: `fastapi_db`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded non-secret configuration
- **Usage context**:
  - Creates the PostgreSQL role
  - Sets database ownership
  - Constructs `DATABASE_URL`

No TLS certificate paths, private keys, API keys, tokens, encrypted data bags, Vault paths, CyberArk references, Conjur variables, or secret-related attribute namespaces were detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/fastapi-tutorial/recipes/default.rb`
- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/venv/bin/python`
- `/opt/fastapi-tutorial/venv/bin/pip`
- `/opt/fastapi-tutorial/venv/bin/uvicorn`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Database objects to verify**:

- PostgreSQL role `fastapi`
- PostgreSQL database `fastapi_db`
- Owner of `fastapi_db`: `fastapi`
- All privileges on `fastapi_db` granted to `fastapi`

**Service endpoints to check**:

- FastAPI application: `0.0.0.0:8000`
- PostgreSQL: `localhost:5432`
- PostgreSQL local Unix socket: platform-default socket

**Templates rendered**: None. The cookbook uses inline `file` resources.

**Configuration render counts**:

- `/opt/fastapi-tutorial/.env`: written once
- `/etc/systemd/system/fastapi-tutorial.service`: written once

## Pre-flight checks

```bash
# Verify required packages on Debian-family systems.
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

# Verify required packages on RPM-family systems when applicable.
rpm -q python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

# Verify the FastAPI application instance.
ls -ld /opt/fastapi-tutorial
ls -ld /opt/fastapi-tutorial/venv
test -f /opt/fastapi-tutorial/requirements.txt
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn
git -C /opt/fastapi-tutorial remote -v
git -C /opt/fastapi-tutorial branch --show-current
git -C /opt/fastapi-tutorial rev-parse --verify HEAD

# Verify the fastapi-tutorial service instance.
systemctl status fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl cat fastapi-tutorial
systemctl show fastapi-tutorial \
  --property=LoadState,ActiveState,SubState,UnitFileState,User,WorkingDirectory,After
test -f /etc/systemd/system/fastapi-tutorial.service
grep -E '^(Description|After|Type|User|WorkingDirectory|Environment|ExecStart|Restart|WantedBy)=' \
  /etc/systemd/system/fastapi-tutorial.service
ss -tlnp | grep ':8000'
curl -sS -o /dev/null -w 'HTTP status: %{http_code}\n' \
  http://127.0.0.1:8000/

# Verify the fastapi_db database instance and PostgreSQL service.
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
sudo -u postgres psql -tAc \
  "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"
sudo -u postgres psql -tAc \
  "SELECT datname, pg_catalog.pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"
sudo -u postgres psql -tAc \
  "SELECT has_database_privilege('fastapi', 'fastapi_db', 'ALL');"

# Verify application connectivity to fastapi_db.
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_database(), current_user;"

# Verify the deployed environment file without exposing it in shared logs.
stat -c '%A %U:%G %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' \
  /opt/fastapi-tutorial/.env

# Verify process and service logs.
ps aux | grep '[u]vicorn app.main:app'
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u postgresql --no-pager -n 100

# Verify systemd reload behavior.
systemctl daemon-reload
systemctl reset-failed fastapi-tutorial
systemctl restart fastapi-tutorial
systemctl is-active fastapi-tutorial
```

The repository should use `https://github.com/dibanez/fastapi_tutorial.git` at revision `main`. The `fastapi-tutorial` service should be enabled, active, and listening on `0.0.0.0:8000`. The `fastapi_db` database should be owned by `fastapi`, and the PostgreSQL service should be enabled and active. The migrated Ansible implementation should use a handler for `systemctl daemon-reload` notified when `/etc/systemd/system/fastapi-tutorial.service` changes.