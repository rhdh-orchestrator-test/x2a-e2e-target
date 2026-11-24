---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys one FastAPI application from the `main` revision of `https://github.com/dibanez/fastapi_tutorial.git` into `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, and PostgreSQL development dependencies, creates a Python virtual environment, installs application requirements, initializes PostgreSQL, creates the `fastapi` user and `fastapi_db` database, writes an application `.env` file, and manages the application with the `fastapi-tutorial.service` systemd unit. Uvicorn listens on `0.0.0.0:8000`. The database password is currently hardcoded and should be migrated to Ansible Vault.

## Service Type and Instances

**Service Type**: Application Server with PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application served by Uvicorn
  - Location/Path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Requirements file: `/opt/fastapi-tutorial/requirements.txt`
  - Environment file: `/opt/fastapi-tutorial/.env`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Service user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Application: `app.main:app`
  - Port/Socket: `0.0.0.0:8000`
  - Restart policy: `always`
  - Ordering: after `network.target` and `postgresql.service`

- **postgresql**: Local PostgreSQL service used by the FastAPI application
  - Service name: `postgresql`
  - Database: `fastapi_db`
  - Database user: `fastapi`
  - Database host: `localhost`
  - Port/Socket: PostgreSQL default port, expected to be `localhost:5432`; no port is explicitly configured
  - Privileges: `fastapi` owns `fastapi_db` and receives all privileges on it
  - Password: `fastapi_password`

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**

```text
cookbooks/fastapi-tutorial/recipes/default.rb
```

**Providers:**

```text
```

No custom Chef providers are used.

**Templates:**

```text
```

No ERB templates are used. Configuration is written using inline Chef `file` resources.

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

1. **`default`** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Evaluates `platform_family?('fedora', 'rhel')`.
   - On Fedora/RHEL, installs six packages: `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, and `libpq-devel`.
   - On non-Fedora/RHEL systems, installs seven packages: `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - On Fedora/RHEL, runs `postgresql-setup --initdb`, guarded by `/var/lib/pgsql/data/PG_VERSION`.
   - Creates `/opt/fastapi-tutorial` as `root:root` with mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates the virtual environment with:
     ```bash
     python3 -m venv /opt/fastapi-tutorial/venv
     ```
     guarded by `/opt/fastapi-tutorial/venv`.
   - Installs dependencies from `/opt/fastapi-tutorial/requirements.txt` using the virtual-environment pip executable.
   - Enables and starts `postgresql`.
   - Creates the PostgreSQL user `fastapi` with password `fastapi_password`.
   - Creates the PostgreSQL database `fastapi_db`, owned by `fastapi`.
   - Grants `fastapi` all privileges on `fastapi_db`.
   - Writes `/opt/fastapi-tutorial/.env` with mode `0644`:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Writes `/etc/systemd/system/fastapi-tutorial.service` with mode `0644`.
   - Reloads systemd through `execute[systemd_reload]` after the unit file changes.
   - Enables and starts `fastapi-tutorial.service`.
   - No `.each` loops are present; the only application instance is `fastapi-tutorial`.

   **Chef resources and execution details:**
   - `package` for the Fedora/RHEL six-package branch.
   - `execute[initialize_postgresql]` for Fedora/RHEL PostgreSQL initialization.
   - `package` for the non-Fedora/RHEL seven-package branch.
   - `directory[node['fastapi_tutorial']['app_path']]` for the application directory.
   - `git[node['fastapi_tutorial']['app_path']]` for repository synchronization.
   - `execute[create_venv]` for virtual-environment creation.
   - `execute[install_dependencies]` for dependency installation.
   - `service[postgresql]` to enable and start PostgreSQL.
   - `execute[create_db_user]` for PostgreSQL user, database, and privilege commands.
   - `file[/opt/fastapi-tutorial/.env]` for application configuration.
   - `file[/etc/systemd/system/fastapi-tutorial.service]` for the systemd unit.
   - `execute[systemd_reload]` with action `nothing`, notified by the systemd unit file resource.
   - `service[fastapi-tutorial]` to enable and start the application.

   **Systemd unit configuration:**
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

   **Attributes:**

   The attributes file is `cookbooks/fastapi-tutorial/attributes/default.rb`. The supplied plan reports the following values, although the repository, revision, and port attributes require source-level verification:

   - `node['fastapi_tutorial']['app_path']`: `/opt/fastapi-tutorial`
   - `node['fastapi_tutorial']['repository']`: `https://github.com/dibanez/fastapi_tutorial.git`
   - `node['fastapi_tutorial']['revision']`: `main`
   - `node['fastapi_tutorial']['service_port']`: `8000`

## Dependencies

**External cookbook dependencies**: None shown in the analyzed metadata or execution tree.

**System package dependencies**:

Fedora/RHEL:

- `python3`
- `python3-pip`
- `git`
- `postgresql-server`
- `postgresql-contrib`
- `libpq-devel`

Non-Fedora/RHEL:

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

**Application dependency installation**:

- Requirements source: `/opt/fastapi-tutorial/requirements.txt`
- Installation environment: `/opt/fastapi-tutorial/venv`

## Credentials

**Detection Summary**: 1 database credential detected across `cookbooks/fastapi-tutorial/recipes/default.rb` and the generated `.env` content.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None
- **Path**: None
- **Secret type**: PostgreSQL database password

### PostgreSQL `fastapi` database password

- **Variable(s)**: No dedicated Chef attribute variable; literal value is `fastapi_password`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
  - Generated `/opt/fastapi-tutorial/.env`
- **Current storage**: Hardcoded in the PostgreSQL user-creation command and the generated database connection string
- **Usage context**:
  - PostgreSQL user creation:
    ```sql
    CREATE USER fastapi WITH PASSWORD 'fastapi_password';
    ```
  - Application connection string:
    ```text
    DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
    ```
- **Migration recommendation**:
  - Store the password in Ansible Vault.
  - Use the vaulted value with `community.postgresql.postgresql_user`.
  - Use the vaulted value when generating `.env`.
  - Do not expose the plaintext password in playbooks, logs, task arguments, or CI output.

No Chef data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, external secret manager, API keys, tokens, or TLS certificates were detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/fastapi-tutorial/recipes/default.rb`
- `cookbooks/fastapi-tutorial/attributes/default.rb`
- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/.env`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv/`
- `/etc/systemd/system/fastapi-tutorial.service`
- `/var/lib/pgsql/data/` on Fedora/RHEL
- Distribution-specific PostgreSQL data directory on non-Fedora/RHEL systems
- PostgreSQL database `fastapi_db`

**Service endpoints to check**:

- `fastapi-tutorial`: `0.0.0.0:8000`
- `postgresql`: `localhost:5432` expected by default
- PostgreSQL distribution-default Unix socket

**Templates rendered**:

- ERB templates: 0
- `/opt/fastapi-tutorial/.env`: 1 inline file deployment
- `/etc/systemd/system/fastapi-tutorial.service`: 1 inline file deployment

## Pre-flight checks

```bash
# PostgreSQL instance
systemctl status postgresql
systemctl is-enabled postgresql
sudo -u postgres psql -d postgres -c "SELECT version();"
sudo -u postgres psql -d postgres -c "\du fastapi"
sudo -u postgres psql -d postgres -c "\l fastapi_db"

# FastAPI application instance
systemctl status fastapi-tutorial.service
systemctl is-enabled fastapi-tutorial.service
systemctl show fastapi-tutorial.service --property=ExecStart
systemctl show fastapi-tutorial.service --property=User
systemctl show fastapi-tutorial.service --property=WorkingDirectory

# PostgreSQL application connectivity
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_database(), current_user;"

# FastAPI HTTP endpoints
curl -i http://127.0.0.1:8000/
curl -i http://127.0.0.1:8000/docs
curl -s http://127.0.0.1:8000/openapi.json

# Listening ports
ss -tlnp | grep ':8000'
ss -tlnp | grep ':5432'

# Application files and permissions
test -f /opt/fastapi-tutorial/.env
test -f /opt/fastapi-tutorial/requirements.txt
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn
stat -c '%A %U:%G %n' /opt/fastapi-tutorial
stat -c '%A %U:%G %n' /opt/fastapi-tutorial/.env
stat -c '%A %U:%G %n' /etc/systemd/system/fastapi-tutorial.service

# Python dependencies
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip check

# Repository state
git -C /opt/fastapi-tutorial remote -v
git -C /opt/fastapi-tutorial branch --show-current
git -C /opt/fastapi-tutorial rev-parse --verify HEAD

# Systemd and service logs
systemctl daemon-reload
journalctl -u fastapi-tutorial.service --no-pager -n 100
journalctl -u postgresql --no-pager -n 100
```

Verify the following:

- `postgresql` is active and enabled.
- `fastapi-tutorial.service` is active and enabled.
- Uvicorn runs from `/opt/fastapi-tutorial/venv/bin/uvicorn`.
- The application target is `app.main:app`.
- The application uses `/opt/fastapi-tutorial` as its working directory.
- FastAPI listens on `0.0.0.0:8000`.
- PostgreSQL contains user `fastapi` and database `fastapi_db`.
- `fastapi_db` is owned by `fastapi`.
- The repository points to `https://github.com/dibanez/fastapi_tutorial.git`.
- The checked-out revision corresponds to `main`.
- `/opt/fastapi-tutorial/.env` and the systemd unit contain the expected configuration.
- The `.env` file and command output do not expose the plaintext database password in migration or CI logs.