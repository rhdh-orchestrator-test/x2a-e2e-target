---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI tutorial application from the `main` branch of `https://github.com/dibanez/fastapi_tutorial.git` to `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, PostgreSQL development libraries, and application dependencies; creates a Python virtual environment; initializes the `fastapi_db` PostgreSQL database and `fastapi` role; writes an inline `.env` file and systemd unit; and enables and starts PostgreSQL and the FastAPI application. The FastAPI service runs as `root` and listens on `0.0.0.0:8000`.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application server
  - Location/Path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Port/Socket: `0.0.0.0:8000`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Application command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Working directory: `/opt/fastapi-tutorial`
  - System user: `root`
  - Restart policy: `Restart=always`
  - Environment PATH: `/opt/fastapi-tutorial/venv/bin`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`

- **postgresql**: PostgreSQL database service
  - Location/Path: Local PostgreSQL installation
  - Port/Socket: Not explicitly configured by the cookbook
  - Service actions: Enabled and started
  - Database user: `fastapi`
  - Database password: `fastapi_password`
  - Database name: `fastapi_db`
  - Database owner: `fastapi`
  - Database host: `localhost`
  - Connection string: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`

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

**Templates:**
```text
```

**Attributes:**
```text
```

**Files:**
```text
```

The `.env` file and systemd unit are created inline by Chef `file` resources and are not cookbook template or static files.

## Module Explanation

The cookbook performs operations in this order:

1. **Install system packages** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs `python3`.
   - Installs `python3-pip`.
   - Installs `python3-venv`.
   - Installs `git`.
   - Installs `postgresql`.
   - Installs `postgresql-contrib`.
   - Installs `libpq-dev`.
   - Resource: `package (1)`.
   - The migration should use the platform-appropriate package manager with this exact package list.

2. **Create the application directory** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/opt/fastapi-tutorial` recursively.
   - Sets owner to `root`.
   - Sets group to `root`.
   - Sets mode to `0755`.
   - Resource: `directory (1)`.

3. **Synchronize the application repository** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git`.
   - Checks out revision `main`.
   - Uses `/opt/fastapi-tutorial` as the destination.
   - Does not assign a separate application user; the directory remains owned by `root`.
   - Resource: `git (1)`.

4. **Create the Python virtual environment** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Runs `python3 -m venv /opt/fastapi-tutorial/venv`.
   - Creates `/opt/fastapi-tutorial/venv`.
   - Runs only when `/opt/fastapi-tutorial/venv` does not already exist through `creates '/opt/fastapi-tutorial/venv'`.
   - Resource: `execute[create_venv] (1)`.

5. **Install Python dependencies** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Runs `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt`.
   - Uses `/opt/fastapi-tutorial` as the working directory.
   - Preserves the repository-provided `requirements.txt`; package names are not inferred because its contents are not specified.
   - Resource: `execute[install_dependencies] (1)`.

6. **Enable and start PostgreSQL** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Enables the `postgresql` service.
   - Starts the `postgresql` service.
   - This service is started before database initialization.
   - Resource: `service[postgresql] (1)`.

7. **Create the PostgreSQL user and database** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Runs database commands as the `postgres` operating-system user.
   - Creates PostgreSQL role `fastapi` with password `fastapi_password`.
   - Creates database `fastapi_db` owned by `fastapi`.
   - Grants all privileges on `fastapi_db` to `fastapi`.
   - The original shell commands suppress errors with `|| true`, including existing-role and existing-database errors.
   - A semantic migration should use PostgreSQL-specific modules for the role, database, and privileges.
   - If shell commands are retained, they must run as the PostgreSQL administrative user and preserve the original error-tolerant behavior.
   - Resource: `execute[create_db_user] (1)`.

8. **Create the application environment file** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/opt/fastapi-tutorial/.env`.
   - Sets owner to `root`.
   - Sets group to `root`.
   - Sets mode to `0644`.
   - Writes:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - The migrated implementation should preferably source the password from Ansible Vault while rendering the same connection string.
   - Resource: `file[/opt/fastapi-tutorial/.env] (1)`.

9. **Create the systemd service unit** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/etc/systemd/system/fastapi-tutorial.service`.
   - Sets owner to `root`.
   - Sets group to `root`.
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
   - Starts after `network.target` and `postgresql.service`.
   - Runs the application as `root`.
   - Uses `/opt/fastapi-tutorial` as the working directory.
   - Runs `app.main:app` through Uvicorn on `0.0.0.0:8000`.
   - Restarts automatically with `Restart=always`.
   - Is enabled through `multi-user.target`.
   - Resource: `file[/etc/systemd/system/fastapi-tutorial.service] (1)`.

10. **Reload systemd** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
    - Defines `systemctl daemon-reload`.
    - Uses `action: nothing`.
    - Runs immediately when `/etc/systemd/system/fastapi-tutorial.service` changes.
    - The migrated implementation should use a systemd daemon-reload handler notified only when the unit changes.
    - Resource: `execute[systemd_reload] (1, action: nothing until notified)`.

11. **Enable and start the FastAPI service** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
    - Enables the `fastapi-tutorial` service.
    - Starts the `fastapi-tutorial` service.
    - Starts only after the repository, virtual environment, dependencies, `.env` file, and systemd unit exist.
    - Resource: `service[fastapi-tutorial] (1)`.

**Total resource invocations in execution order**:

1. `package (1)`
2. `directory (1)`
3. `git (1)`
4. `execute[create_venv] (1)`
5. `execute[install_dependencies] (1)`
6. `service[postgresql] (1)`
7. `execute[create_db_user] (1)`
8. `file[/opt/fastapi-tutorial/.env] (1)`
9. `file[/etc/systemd/system/fastapi-tutorial.service] (1)`
10. `execute[systemd_reload] (1, action: nothing until notified)`
11. `service[fastapi-tutorial] (1)`

No collection attributes or `.each` loops are present.

## Dependencies

**External cookbook dependencies**: None declared in `metadata.rb`

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

**Application dependency source**:

```text
/opt/fastapi-tutorial/requirements.txt
```

The Python package names are supplied by the checked-out repository and are not specified in the execution tree.

## Credentials

**Detection Summary**: 1 hardcoded database credential detected in 1 recipe file.

**Source**:
  - **Provider**: Hardcoded in the Chef recipe
  - **URL**: No external vault or secret-manager URL detected
  - **Path**: No data bag, vault path, or secret-manager path detected

### PostgreSQL password

- **Variable(s)**:
  - PostgreSQL role password: `fastapi_password`
  - `DATABASE_URL`: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded
- **Usage context**:
  - Creates PostgreSQL role `fastapi`.
  - Is embedded in `/opt/fastapi-tutorial/.env`.
  - Is used by the FastAPI application for its PostgreSQL connection.
- **Migration recommendation**:
  - Store the password in Ansible Vault.
  - Use the vaulted value in the PostgreSQL user task.
  - Render the same vaulted value into `DATABASE_URL`.
  - Use `no_log: true` when the password is passed to a module or command.

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, CyberArk, Conjur, environment-variable secret lookup, TLS certificate, private key, API token, or external database connection credential was detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/.env`
- `/opt/fastapi-tutorial/venv`
- `/etc/systemd/system/fastapi-tutorial.service`

**Application data and code directory**:

- `/opt/fastapi-tutorial`

**Database objects to verify**:

- PostgreSQL role: `fastapi`
- PostgreSQL database: `fastapi_db`
- Database owner: `fastapi`

**Service endpoints to check**:

- FastAPI: `0.0.0.0:8000`
- PostgreSQL: Local PostgreSQL service; port and socket are not explicitly configured by the cookbook

**Templates rendered**:

- None. The `.env` file and systemd unit are created using inline Chef `file` resources.

**Render counts**:

- `/opt/fastapi-tutorial/.env`: 1 inline file resource
- `/etc/systemd/system/fastapi-tutorial.service`: 1 inline file resource
- Cookbook templates: 0

**Service and reload behavior**:

- `postgresql` is enabled and started before database initialization.
- `systemd_reload` runs immediately when `/etc/systemd/system/fastapi-tutorial.service` changes.
- `fastapi-tutorial` is enabled and started after the unit is written.
- The FastAPI unit contains `Restart=always`.

## Pre-flight checks:

```bash
# Verify installed packages and tools
python3 --version
python3 -m pip --version
git --version
psql --version
```

```bash
# Verify the fastapi-tutorial application directory and repository
ls -ld /opt/fastapi-tutorial
git -C /opt/fastapi-tutorial status --short
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
test -f /opt/fastapi-tutorial/requirements.txt
```

```bash
# Verify the fastapi-tutorial virtual environment
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip check
```

```bash
# Verify the fastapi-tutorial environment file without exposing its password
stat -c '%U:%G %a %n' /opt/fastapi-tutorial/.env
grep '^PROJECT_NAME=' /opt/fastapi-tutorial/.env
grep '^API_VERSION=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env
```

Do not print the complete `.env` file in shared logs because it contains the PostgreSQL password.

```bash
# Verify the postgresql instance
systemctl status postgresql --no-pager
systemctl is-enabled postgresql
systemctl is-active postgresql
```

```bash
# Verify the fastapi PostgreSQL role
sudo -u postgres psql -tAc "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"
```

Expected output:

```text
fastapi
```

```bash
# Verify the fastapi_db database and fastapi owner
sudo -u postgres psql -tAc "SELECT datname, pg_catalog.pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"
```

Expected output:

```text
fastapi_db | fastapi
```

```bash
# Verify database connectivity for the fastapi application role
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_database(), current_user;"
```

Expected output:

```text
fastapi_db | fastapi
```

```bash
# Verify the fastapi-tutorial systemd instance
systemctl cat fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl status fastapi-tutorial --no-pager
```

```bash
# Verify fastapi-tutorial systemd dependencies and startup configuration
grep '^After=' /etc/systemd/system/fastapi-tutorial.service
grep '^WorkingDirectory=' /etc/systemd/system/fastapi-tutorial.service
grep '^ExecStart=' /etc/systemd/system/fastapi-tutorial.service
grep '^Restart=' /etc/systemd/system/fastapi-tutorial.service
```

Expected configuration:

```text
After=network.target postgresql.service
WorkingDirectory=/opt/fastapi-tutorial
ExecStart=/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
```

```bash
# Verify the fastapi-tutorial process
ps aux | grep '[u]vicorn'
```

```bash
# Verify the fastapi-tutorial listening port
ss -tlnp | grep ':8000'
```

The output should show a listener on port `8000`.

```bash
# Verify HTTP availability for fastapi-tutorial
curl -I http://127.0.0.1:8000/
```

The application should return an HTTP response. The cookbook does not define a dedicated health endpoint, so `/` is the safest endpoint check.

```bash
# Verify fastapi-tutorial logs
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u fastapi-tutorial -p err --no-pager
```

```bash
# Verify postgresql logs
journalctl -u postgresql --no-pager -n 100
journalctl -u postgresql -p err --no-pager
```

```bash
# Verify expected application and service files
find /opt/fastapi-tutorial -maxdepth 1 -type d -printf '%p\n'
test -f /opt/fastapi-tutorial/.env
test -f /etc/systemd/system/fastapi-tutorial.service
```

The migration is complete when the `postgresql` instance is enabled and active, role `fastapi` and database `fastapi_db` exist with `fastapi` as owner, the `fastapi-tutorial` instance is enabled and active, port `8000` is listening, and `http://127.0.0.1:8000/` returns an application response.