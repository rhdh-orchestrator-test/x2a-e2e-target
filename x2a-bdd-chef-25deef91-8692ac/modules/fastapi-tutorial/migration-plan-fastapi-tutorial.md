---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI tutorial application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, and PostgreSQL development packages; creates a Python virtual environment; installs dependencies from `requirements.txt`; initializes PostgreSQL where required; creates the `fastapi` PostgreSQL role and `fastapi_db` database; writes an environment file; and manages the `fastapi-tutorial` systemd service. The application runs as `root` through Uvicorn and listens on `0.0.0.0:8000`. The PostgreSQL password is hardcoded in the Chef recipe and must be migrated to Ansible Vault. The exact attribute values, service-name resolution, resource properties, and idempotence guards require verification against the cookbook source.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application served by Uvicorn
  - Location/Path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Entrypoint: `app.main:app`
  - Port/Socket: `0.0.0.0:8000`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Systemd user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Restart policy: `always`
  - Dependencies: `postgresql.service`, `network.target`

- **postgresql**: PostgreSQL database service
  - Service name: `postgresql`
  - Database user: `fastapi`
  - Database name: `fastapi_db`
  - Database owner: `fastapi`
  - Privileges: `fastapi` receives all privileges on `fastapi_db`
  - Connection host: `localhost`
  - Port/Socket: PostgreSQL default is normally `localhost:5432`; the cookbook does not configure the port or socket path
  - Connection URL: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
  - Password: `fastapi_password`, currently hardcoded in the Chef recipe

The supplied analysis identifies the application service as `fastapi-tutorial`, but the structured resource analysis shows an unresolved `service_name` variable. The final service name and related attribute values must be verified from the cookbook source.

## File Structure

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

No Chef templates are rendered. Configuration is written with inline `file` resources.

**Attributes:**
```text
cookbooks/fastapi-tutorial/attributes/default.rb
```

**Files:**
```text
```

No static files are deployed using `cookbook_file` or `remote_file`.

## Attributes

Source file:

```text
cookbooks/fastapi-tutorial/attributes/default.rb
```

The migration analysis references the following attributes, but their definitions and values were not present in the supplied structured analysis and must be verified:

| Chef attribute | Referenced value | Ansible equivalent |
|---|---|---|
| `node['fastapi_tutorial']['app_path']` | `/opt/fastapi-tutorial` | `fastapi_app_path` |
| `node['fastapi_tutorial']['repository']` | `https://github.com/dibanez/fastapi_tutorial.git` | `fastapi_repository` |
| `node['fastapi_tutorial']['revision']` | `main` | `fastapi_revision` |
| `node['fastapi_tutorial']['service_port']` | `8000` | `fastapi_service_port` |

Define these values in `defaults/main.yml` only after confirming them from `cookbooks/fastapi-tutorial/attributes/default.rb`. Inventory or group variables may override them when required.

## Module Explanation

The cookbook performs operations in this order:

1. **`default`** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Checks the platform family and installs the required operating-system packages.
   - On Fedora/RHEL, installs `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, and `libpq-devel`.
   - On non-Fedora/RHEL platforms, installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Package versions are not pinned.
   - On Fedora/RHEL, executes `postgresql-setup --initdb`; the stated idempotence marker is `/var/lib/pgsql/data/PG_VERSION`, but this guard requires source verification.
   - Creates `/opt/fastapi-tutorial` with owner `root`, group `root`, mode `0755`, and recursive creation.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates `/opt/fastapi-tutorial/venv` with `python3 -m venv`; the stated guard is the existence of `/opt/fastapi-tutorial/venv`, which requires source verification.
   - Installs dependencies with `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt` using `/opt/fastapi-tutorial` as the working directory.
   - Enables and starts the `postgresql` service.
   - Creates the PostgreSQL role `fastapi` with password `fastapi_password`.
   - Creates the PostgreSQL database `fastapi_db` owned by `fastapi`.
   - Grants all privileges on `fastapi_db` to `fastapi`.
   - The original PostgreSQL commands suppress errors with `|| true`; Ansible should use idempotent PostgreSQL modules instead.
   - Writes `/opt/fastapi-tutorial/.env` with owner `root`, group `root`, and mode `0644`.
   - The environment file contains:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Writes `/etc/systemd/system/fastapi-tutorial.service` with:
     - Description `FastAPI Tutorial Service`
     - `After=network.target postgresql.service`
     - `Type=simple`
     - `User=root`
     - `WorkingDirectory=/opt/fastapi-tutorial`
     - `Environment="PATH=/opt/fastapi-tutorial/venv/bin"`
     - `ExecStart=/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
     - `Restart=always`
     - `WantedBy=multi-user.target`
   - Defines `execute[systemd_reload]` to run `systemctl daemon-reload` only when notified by a systemd unit-file change.
   - Enables and starts the `fastapi-tutorial` service.
   - The exact file properties, unit contents, service name, and notification behavior require verification against the recipe source because the supplied structured analysis confirms the resource types but not all detailed properties.

No `.each` loops or collection attributes are present. No iteration expansion is required.

## Dependencies

**External cookbook dependencies**: None listed in the supplied metadata or execution analysis.

**System package dependencies**:

- **Fedora/RHEL**:
  - `python3`
  - `python3-pip`
  - `git`
  - `postgresql-server`
  - `postgresql-contrib`
  - `libpq-devel`

- **Non-Fedora/RHEL**:
  - `python3`
  - `python3-pip`
  - `python3-venv`
  - `git`
  - `postgresql`
  - `postgresql-contrib`
  - `libpq-dev`

**Application dependency installation**: `/opt/fastapi-tutorial/requirements.txt` installed into `/opt/fastapi-tutorial/venv`.

**Service dependencies**:

- `postgresql.service`
- `network.target`

**Managed services**:

- `postgresql`
- `fastapi-tutorial`

## Credentials

**Detection Summary**: 1 hardcoded database credential detected in `cookbooks/fastapi-tutorial/recipes/default.rb`. The credential is used in PostgreSQL role creation and the application database URL.

**Source**:
  - **Provider**: None detected; the credential is hardcoded directly in the Chef recipe
  - **URL**: No external secret-management URL detected
  - **Path**: No data bag, Chef Vault, CyberArk, Conjur, or other secret path detected

### PostgreSQL Password

- **Variable(s)**:
  - Literal password: `fastapi_password`
  - Connection URL: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the recipe and written to `/opt/fastapi-tutorial/.env`
- **Usage context**:
  - PostgreSQL role creation:
    ```sql
    CREATE USER fastapi WITH PASSWORD 'fastapi_password';
    ```
  - Application database connection:
    ```dotenv
    DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
    ```

Store the password in Ansible Vault, use it for PostgreSQL role creation and URL construction, suppress it from task output, and consider changing `.env` permissions from `0644` to `0600`.

No TLS certificates, private keys, API keys, tokens, encrypted data bags, Chef Vault items, CyberArk integrations, Conjur variables, or secret environment-variable references were detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- `/var/lib/pgsql/data/PG_VERSION` on Fedora/RHEL

**Database objects to verify**:

- PostgreSQL role `fastapi`
- PostgreSQL database `fastapi_db`
- Database owner `fastapi`

**Service endpoints to check**:

- FastAPI application: `0.0.0.0:8000`
- PostgreSQL: normally `localhost:5432`
- PostgreSQL local Unix socket: distribution default; no explicit socket path is configured

**Templates rendered**: None. No Chef templates are rendered.

**Inline files written**:

- `/opt/fastapi-tutorial/.env`: 1 file resource, written once by the recipe
- `/etc/systemd/system/fastapi-tutorial.service`: 1 file resource, written once by the recipe

Application output is expected in the systemd journal. No dedicated application log file is created.

## Pre-flight checks

```bash
# Verify required tools
python3 --version
python3 -m pip --version
git --version
```

### FastAPI application instance: `fastapi-tutorial`

```bash
# Verify the application directory and checkout
ls -ld /opt/fastapi-tutorial
git -C /opt/fastapi-tutorial remote -v
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
git -C /opt/fastapi-tutorial status --short

# Verify the expected repository and revision
git -C /opt/fastapi-tutorial remote get-url origin
git -C /opt/fastapi-tutorial branch --show-current

# Verify the virtual environment and requirements
ls -ld /opt/fastapi-tutorial/venv
ls -l /opt/fastapi-tutorial/requirements.txt
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip --version
/opt/fastapi-tutorial/venv/bin/pip check
/opt/fastapi-tutorial/venv/bin/uvicorn --version

# Verify the environment file without printing its secret value
ls -l /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION)=' /opt/fastapi-tutorial/.env
grep -q '^DATABASE_URL=' /opt/fastapi-tutorial/.env
echo $?

# Verify the systemd unit
ls -l /etc/systemd/system/fastapi-tutorial.service
systemctl daemon-reload
systemctl cat fastapi-tutorial.service
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl status fastapi-tutorial --no-pager

# Verify key unit settings
systemctl cat fastapi-tutorial.service | \
  grep -E 'Description=|After=|User=|WorkingDirectory=|Environment=|ExecStart=|Restart=|WantedBy='

# Verify the FastAPI process and endpoint
ps aux | grep '[u]vicorn app.main:app'
ss -tlnp | grep ':8000'
curl -I http://127.0.0.1:8000/
curl -sS http://127.0.0.1:8000/

# Review FastAPI logs
journalctl -u fastapi-tutorial --no-pager -n 100
systemctl show fastapi-tutorial \
  --property=ActiveState,SubState,ExecMainStatus,ExecMainCode
```

Expected FastAPI settings:

- Working directory: `/opt/fastapi-tutorial`
- User: `root`
- Executable: `/opt/fastapi-tutorial/venv/bin/uvicorn`
- Application: `app.main:app`
- Listen address: `0.0.0.0`
- Listen port: `8000`
- Restart policy: `always`

### PostgreSQL instance: `postgresql`

```bash
# Verify PostgreSQL service state
systemctl status postgresql --no-pager
systemctl is-enabled postgresql
systemctl is-active postgresql

# Verify Fedora/RHEL initialization when applicable
test -f /var/lib/pgsql/data/PG_VERSION

# Verify the PostgreSQL role
sudo -u postgres psql -tAc \
  "SELECT 1 FROM pg_roles WHERE rolname='fastapi';"

# Verify the database
sudo -u postgres psql -tAc \
  "SELECT 1 FROM pg_database WHERE datname='fastapi_db';"

# Verify database ownership
sudo -u postgres psql -tAc \
  "SELECT pg_catalog.pg_get_userbyid(datdba)
   FROM pg_database WHERE datname='fastapi_db';"

# Verify application-role connectivity
PGPASSWORD='fastapi_password' \
psql -h localhost -U fastapi -d fastapi_db -c "SELECT version();"

PGPASSWORD='fastapi_password' \
psql -h localhost -U fastapi -d fastapi_db -c "SELECT 1;"

# Verify the default PostgreSQL port when applicable
ss -tlnp | grep ':5432'

# Review PostgreSQL logs and state
journalctl -u postgresql --no-pager -n 100
systemctl show postgresql \
  --property=ActiveState,SubState,ExecMainStatus,ExecMainCode
```

Expected PostgreSQL results:

- Role query returns `1`.
- Database query returns `1`.
- Database owner query returns `fastapi`.
- The `fastapi` role connects successfully to `fastapi_db`.
- `SELECT 1` completes successfully.
- Actual service name, port, socket, and listen behavior are verified against the target distribution because the cookbook does not explicitly configure them.
