---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys a FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, and PostgreSQL development dependencies; creates a Python virtual environment; installs application requirements; creates PostgreSQL database `fastapi_db` and user `fastapi`; writes `/opt/fastapi-tutorial/.env`; and manages a systemd service named `fastapi-tutorial` listening on port `8000`. The database password is currently hardcoded as `fastapi_password` and must be protected during migration. Attribute values and recipe resource properties should be verified against the cookbook source because the validation summary did not include their complete source analysis.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application server
  - Application path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Git revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Environment file: `/opt/fastapi-tutorial/.env`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Service user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Start command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Listen address: `0.0.0.0`
  - Listen port: `8000`
  - Restart policy: `always`
  - Startup dependency: `postgresql.service`

- **fastapi_db**: PostgreSQL database for the FastAPI application
  - PostgreSQL owner: `fastapi`
  - PostgreSQL user: `fastapi`
  - Database host: `localhost`
  - Database port: `5432`
  - Database connection URL: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
  - Privileges: `fastapi` receives all privileges on `fastapi_db`

The supplied validation summary confirms the execution flow, package branches, PostgreSQL commands, hardcoded recipe password, and exclusion of unrelated data bags. The attribute values, `service_name` definition, and detailed resource properties should be verified directly in the cookbook source before implementation.

## File Structure

**Recipes:**
```text
cookbooks/fastapi-tutorial/recipes/default.rb
```

**Providers:**
```text
```

No custom Chef resources are used, so no provider files are required.

**Templates:**
```text
```

No ERB templates are used. Configuration files are created with inline Chef `file` resources.

**Attributes:**
```text
cookbooks/fastapi-tutorial/attributes/default.rb
```

**Files:**
```text
```

No static files are deployed with `cookbook_file` or `remote_file`.

**Data bags:**

No data bags are referenced by the selected cookbook's reachable execution flow. Repository-level entries for `nginx_secrets` and `nginx_sites` are unrelated and must not be migrated as dependencies of `fastapi-tutorial`.

## Attributes

**Source file:**
```text
cookbooks/fastapi-tutorial/attributes/default.rb
```

The migration plan identifies these defaults, pending direct source verification:

| Chef attribute | Default value | Ansible equivalent |
|---|---|---|
| `node['fastapi_tutorial']['app_path']` | `/opt/fastapi-tutorial` | `fastapi_app_path` |
| `node['fastapi_tutorial']['repository']` | `https://github.com/dibanez/fastapi_tutorial.git` | `fastapi_repository` |
| `node['fastapi_tutorial']['revision']` | `main` | `fastapi_revision` |
| `node['fastapi_tutorial']['service_port']` | `8000` | `fastapi_service_port` |

Recommended Ansible variable defaults:

```yaml
fastapi_app_path: /opt/fastapi-tutorial
fastapi_repository: https://github.com/dibanez/fastapi_tutorial.git
fastapi_revision: main
fastapi_service_port: 8000
fastapi_service_name: fastapi-tutorial
fastapi_database_name: fastapi_db
fastapi_database_user: fastapi
```

The supplied validation summary does not establish whether `fastapi_service_name`, `fastapi_database_name`, or `fastapi_database_user` are Chef attributes. Verify their definitions before migration. These values represent one application and one database configuration and do not require iteration.

## Module Explanation

The cookbook performs operations in the following order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs platform-specific system packages.
   - Initializes PostgreSQL on RHEL/Fedora systems.
   - Creates `/opt/fastapi-tutorial`.
   - Synchronizes the Git repository at revision `main`.
   - Creates the Python virtual environment.
   - Installs dependencies from `requirements.txt`.
   - Enables and starts PostgreSQL.
   - Creates the PostgreSQL role, database, and privileges.
   - Writes `/opt/fastapi-tutorial/.env`.
   - Writes `/etc/systemd/system/fastapi-tutorial.service`.
   - Reloads systemd when the unit changes.
   - Enables and starts `fastapi-tutorial`.

   **RHEL/Fedora package branch** (`platform_family?('fedora', 'rhel')`):
   - Installs `python3`.
   - Installs `python3-pip`.
   - Installs `git`.
   - Installs `postgresql-server`.
   - Installs `postgresql-contrib`.
   - Installs `libpq-devel`.
   - Runs `postgresql-setup --initdb` when `/var/lib/pgsql/data/PG_VERSION` is absent.

   **Non-RHEL/Fedora package branch**:
   - Installs `python3`.
   - Installs `python3-pip`.
   - Installs `python3-venv`.
   - Installs `git`.
   - Installs `postgresql`.
   - Installs `postgresql-contrib`.
   - Installs `libpq-dev`.

   **Application directory**:
   - Creates `/opt/fastapi-tutorial` as a recursive `root:root` directory with mode `0755`.

   **Git checkout**:
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` into `/opt/fastapi-tutorial`.
   - Checks out revision `main`.

   **Python virtual environment**:
   - Runs `python3 -m venv /opt/fastapi-tutorial/venv`.
   - Uses `/opt/fastapi-tutorial/venv` as the idempotence marker.

   **Python dependencies**:
   - Runs `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt`.
   - Uses `/opt/fastapi-tutorial` as the working directory.

   **PostgreSQL service**:
   - Enables and starts the `postgresql` service.

   **PostgreSQL objects**:
   - Creates user `fastapi` with password `fastapi_password`.
   - Creates database `fastapi_db` owned by `fastapi`.
   - Grants all privileges on `fastapi_db` to `fastapi`.
   - The original Chef commands append `|| true`, suppressing existing-object errors and potentially hiding other failures.
   - The Ansible migration should use `community.postgresql.postgresql_user`, `community.postgresql.postgresql_db`, and `community.postgresql.postgresql_privs` with `become_user: postgres`.

   **Environment file**:
   - Creates `/opt/fastapi-tutorial/.env` with owner `root`, group `root`, and mode `0644`.
   - Writes:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - The database password must be supplied through Ansible Vault or an approved external secret provider.

   **Systemd unit**:
   - Creates `/etc/systemd/system/fastapi-tutorial.service` with owner `root`, group `root`, and mode `0644`.
   - Configures:
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

   **Systemd reload and service startup**:
   - Runs `systemctl daemon-reload` when the unit file changes.
   - Enables and starts the `fastapi-tutorial` service after the unit is installed and systemd has reloaded its definitions.

   The validation summary does not independently demonstrate the definition of `service_name`. Verify that the cookbook resolves it to `fastapi-tutorial` before finalizing the unit name.

## Dependencies

**External cookbook dependencies**: None are declared in the supplied `metadata.rb`.

**System package dependencies**:

RHEL/Fedora:

- `python3`
- `python3-pip`
- `git`
- `postgresql-server`
- `postgresql-contrib`
- `libpq-devel`

Non-RHEL/Fedora:

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

**Application dependency source**:

```text
/opt/fastapi-tutorial/requirements.txt
```

This file is provided by the synchronized Git repository and is installed into `/opt/fastapi-tutorial/venv`.

## Credentials

**Detection Summary**: One hardcoded database credential was detected in `cookbooks/fastapi-tutorial/recipes/default.rb`. The same credential is used in the PostgreSQL command and written to `/opt/fastapi-tutorial/.env`. Attribute credential scanning was not independently confirmed because the supplied validation summary did not include the complete attributes-file contents.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None
- **Path**: None; the value is embedded in the recipe and generated environment file

### PostgreSQL database password

- **Variable(s)**:
  - No Chef attribute variable is used.
  - Literal password: `fastapi_password`
  - Connection URL: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the Chef recipe and written to `/opt/fastapi-tutorial/.env`
- **Usage context**:
  - PostgreSQL command: `CREATE USER fastapi WITH PASSWORD 'fastapi_password'`
  - Application connection through `DATABASE_URL`
- **Migration requirement**:
  - Store the password in Ansible Vault or an approved external secret manager.
  - Do not place the literal password in committed defaults, templates, or unencrypted variable files.
  - Use the protected variable when creating the PostgreSQL role and rendering `/opt/fastapi-tutorial/.env`.

No data bags, Chef Vault items, CyberArk integrations, Conjur variables, environment-variable secret lookups, TLS certificate references, API keys, or additional credential namespaces were identified in the selected cookbook's execution flow.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- `/var/lib/pgsql/data/PG_VERSION` on RHEL/Fedora systems

**Database objects to verify**:

- PostgreSQL role: `fastapi`
- PostgreSQL database: `fastapi_db`
- Database owner: `fastapi`
- All database privileges granted to `fastapi`

**Service endpoints to check**:

- FastAPI: `0.0.0.0:8000`
- PostgreSQL: `localhost:5432`
- PostgreSQL distribution-managed local Unix socket

**Templates rendered**:

- No ERB templates are used.
- `/opt/fastapi-tutorial/.env`: rendered once by an inline file resource
- `/etc/systemd/system/fastapi-tutorial.service`: rendered once by an inline file resource

## Pre-flight checks

```bash
# Verify the PostgreSQL instance
systemctl status postgresql --no-pager
systemctl is-enabled postgresql
systemctl is-active postgresql

# Verify the fastapi_db database instance
sudo -u postgres psql -c "\du fastapi"
sudo -u postgres psql -c "\l fastapi_db"
sudo -u postgres psql -d fastapi_db -c "SELECT current_database();"
sudo -u postgres psql -d fastapi_db -c "SELECT current_user;"

# Verify PostgreSQL connectivity for fastapi_db
PGPASSWORD='<protected-fastapi-password>' \
psql -h localhost -U fastapi -d fastapi_db -c "SELECT 1;"

# Verify the FastAPI application instance
systemctl status fastapi-tutorial --no-pager
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial

# Verify application files
test -d /opt/fastapi-tutorial
test -f /opt/fastapi-tutorial/requirements.txt
test -d /opt/fastapi-tutorial/venv
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn

# Verify application configuration
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' \
  /opt/fastapi-tutorial/.env

# Verify the systemd unit
systemctl daemon-reload
systemctl cat fastapi-tutorial
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service

# Verify the application process and endpoint
ps aux | grep '[u]vicorn app.main:app'
ss -tlnp | grep ':8000'
curl -I http://127.0.0.1:8000/docs

# Verify the repository and revision
git -C /opt/fastapi-tutorial remote -v
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
git -C /opt/fastapi-tutorial status --short

# Review service logs
journalctl -u postgresql --no-pager -n 100
journalctl -u fastapi-tutorial --no-pager -n 100
```

Expected results:

- PostgreSQL is enabled and active.
- Role `fastapi` and database `fastapi_db` exist.
- `fastapi_db` is owned by `fastapi`.
- The protected-password connection returns successfully.
- `fastapi-tutorial` is enabled and active.
- The virtual environment contains executable Python, pip, and Uvicorn binaries.
- The systemd unit passes `systemd-analyze verify`.
- Uvicorn listens on `0.0.0.0:8000`.
- The `/docs` endpoint returns an HTTP response if it is provided by the application.
- The repository remote is `https://github.com/dibanez/fastapi_tutorial.git`.
- The checkout corresponds to revision `main`.

Do not print the database password in shared logs, shell history, or terminal recordings.