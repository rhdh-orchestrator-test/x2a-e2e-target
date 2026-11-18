---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, and development dependencies; creates a Python virtual environment; installs the repository requirements; initializes and manages PostgreSQL; creates database `fastapi_db` and user `fastapi`; writes `/opt/fastapi-tutorial/.env`; and manages the `fastapi-tutorial` systemd service listening on port `8000`. The database password is currently hardcoded and must be migrated to Ansible Vault.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application server
  - Location/Path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Dependency file: `/opt/fastapi-tutorial/requirements.txt`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Service user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Startup command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Listen address: `0.0.0.0`
  - Port/Socket: `8000`
  - Restart policy: `always`
  - Startup dependency: `postgresql.service`
  - Application configuration: `/opt/fastapi-tutorial/.env`

- **postgresql**: PostgreSQL database service
  - Database: `fastapi_db`
  - Database user: `fastapi`
  - Database password: `fastapi_password`
  - Host: `localhost`
  - Port/Socket: TCP port `5432` and/or the local PostgreSQL Unix socket
  - Database URL: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
  - Managed service: `postgresql`

## File Structure

The following are the relevant files used by this cookbook.

**Recipes:**
```text
cookbooks/fastapi-tutorial/recipes/default.rb
```

**Providers:**
```text
```

No custom Chef resources or provider files are used.

**Templates:**
```text
```

No ERB templates are rendered. Configuration files are generated with inline `file` resources.

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

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Selects one platform-specific package branch.
   - On Fedora/RHEL, installs `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, and `libpq-devel`.
   - On Fedora/RHEL, runs `postgresql-setup --initdb` only when `/var/lib/pgsql/data/PG_VERSION` does not exist.
   - On non-Fedora/RHEL platforms, installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` into `/opt/fastapi-tutorial` at revision `main`.
   - Creates `/opt/fastapi-tutorial/venv` with `python3 -m venv /opt/fastapi-tutorial/venv` when the directory does not exist.
   - Installs dependencies from `/opt/fastapi-tutorial/requirements.txt` using `/opt/fastapi-tutorial/venv/bin/pip`, with working directory `/opt/fastapi-tutorial`.
   - Enables and starts `postgresql`.
   - Creates PostgreSQL user `fastapi` with password `fastapi_password`.
   - Creates PostgreSQL database `fastapi_db` owned by `fastapi`.
   - Grants `ALL PRIVILEGES` on `fastapi_db` to `fastapi`.
   - Writes `/opt/fastapi-tutorial/.env` with owner `root`, group `root`, and mode `0644`.
   - Writes `/etc/systemd/system/fastapi-tutorial.service` with owner `root`, group `root`, and mode `0644`.
   - Notifies `execute[systemd_reload]` immediately when the systemd unit changes.
   - Runs `systemctl daemon-reload` only when notified.
   - Enables and starts `fastapi-tutorial`.

   The generated `/opt/fastapi-tutorial/.env` contains:
   ```dotenv
   PROJECT_NAME="FastAPI Tutorial"
   API_VERSION=1.0.0
   DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
   ```

   The generated `/etc/systemd/system/fastapi-tutorial.service` contains:
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

   There are no `.each` loops or collection attributes. No iterations require expansion.

### Source attributes

`cookbooks/fastapi-tutorial/attributes/default.rb` defines:

| Chef attribute | Value |
|---|---|
| `node['fastapi_tutorial']['app_path']` | `/opt/fastapi-tutorial` |
| `node['fastapi_tutorial']['repository']` | `https://github.com/dibanez/fastapi_tutorial.git` |
| `node['fastapi_tutorial']['revision']` | `main` |
| `node['fastapi_tutorial']['service_port']` | `8000` |

Recommended Ansible defaults:

```yaml
fastapi_app_path: /opt/fastapi-tutorial
fastapi_repository: https://github.com/dibanez/fastapi_tutorial.git
fastapi_revision: main
fastapi_service_port: 8000
fastapi_service_name: fastapi-tutorial
```

## Dependencies

**External cookbook dependencies**: None declared in the supplied metadata.

**System package dependencies**:

Fedora/RHEL:

- `python3`
- `python3-pip`
- `git`
- `postgresql-server`
- `postgresql-contrib`
- `libpq-devel`

Other supported platforms:

- `python3`
- `python3-pip`
- `python3-venv`
- `git`
- `postgresql`
- `postgresql-contrib`
- `libpq-dev`

**Service dependencies**:

- `postgresql.service`
- `fastapi-tutorial.service`

**Ansible collection dependencies**:

- `community.postgresql` for PostgreSQL user, database, and privilege management

**Supported Chef platforms from metadata**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`
- Explicit Fedora/RHEL package handling is also present in the recipe.

## Credentials

**Detection Summary**: 2 credential references detected in 2 source locations. Both references contain the same PostgreSQL database password: one in the PostgreSQL user creation command and one in the application database URL.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None
- **Path**: None
- **Vault integration**: None detected
- **Data bags**: None detected
- **Chef Vault**: None detected
- **CyberArk/Conjur**: None detected
- **Environment-variable secret lookup**: None detected

### PostgreSQL database password

- **Variable(s)**:
  - Literal password: `fastapi_password`
  - Database URL: `DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the PostgreSQL user creation command and inline `.env` file content
- **Usage context**:
  - Sets the password for PostgreSQL user `fastapi`
  - Authenticates the FastAPI application to database `fastapi_db`
- **Migration requirement**:
  - Store the password in Ansible Vault as `fastapi_db_password`
  - Use the vaulted variable in the PostgreSQL user task
  - Use the same vaulted variable when rendering `/opt/fastapi-tutorial/.env`
  - Avoid exposing the password in command output or task logs

### PostgreSQL database connection string

- **Variable(s)**: `DATABASE_URL`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in `/opt/fastapi-tutorial/.env`
- **Usage context**: Application database connection configuration
- **Sensitive components**:
  - Username: `fastapi`
  - Password: `fastapi_password`
  - Host: `localhost`
  - Database: `fastapi_db`
- **Migration requirement**: Render the connection string from the vaulted password and non-secret variables rather than embedding the password in playbook source.

No TLS certificate, private key, API token, SSH key, or external secret-manager endpoint was detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- `/var/lib/pgsql/data/PG_VERSION` on Fedora/RHEL
- PostgreSQL data directory selected by the installed package on other supported platforms

**Database objects to verify**:

- PostgreSQL role `fastapi`
- PostgreSQL database `fastapi_db`
- Database owner `fastapi`
- `ALL PRIVILEGES` on `fastapi_db` granted to `fastapi`

**Service endpoints to check**:

- `fastapi-tutorial`: `0.0.0.0:8000`
- `postgresql`: local TCP port `5432` and/or the PostgreSQL Unix socket

**Templates rendered**:

- No ERB templates are rendered.
- `/opt/fastapi-tutorial/.env` — inline `file` content, rendered once
- `/etc/systemd/system/fastapi-tutorial.service` — inline `file` content, rendered once

## Pre-flight checks:
```bash
# Confirm the operating system and supported platform
cat /etc/os-release

# Verify required executables
python3 --version
python3 -m pip --version
git --version
psql --version

# Fedora/RHEL PostgreSQL initialization marker
if grep -Eqi 'fedora|rhel|centos' /etc/os-release; then
  ls -l /var/lib/pgsql/data/PG_VERSION
fi

# Verify PostgreSQL instance: postgresql
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql

# Verify PostgreSQL role: fastapi
sudo -u postgres psql -tAc \
  "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"

# Verify PostgreSQL database: fastapi_db
sudo -u postgres psql -tAc \
  "SELECT datname FROM pg_database WHERE datname = 'fastapi_db';"

# Verify database owner: fastapi
sudo -u postgres psql -tAc \
  "SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"

# Verify application credentials without exposing the password in logs
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT 1;"

# Verify PostgreSQL listener
ss -tlnp | grep ':5432'

# Verify FastAPI application directory and virtual environment
ls -ld /opt/fastapi-tutorial
ls -ld /opt/fastapi-tutorial/venv
ls -l /opt/fastapi-tutorial/requirements.txt
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip --version
/opt/fastapi-tutorial/venv/bin/uvicorn --version

# Verify repository source and revision
git -C /opt/fastapi-tutorial remote -v
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
git -C /opt/fastapi-tutorial log -1 --oneline

# Verify application configuration ownership and permissions
stat -c '%U:%G %a %n' /opt/fastapi-tutorial/.env

# Verify required configuration keys without exposing the password
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' \
  /opt/fastapi-tutorial/.env
sed 's#fastapi_password#REDACTED#g' /opt/fastapi-tutorial/.env

# Validate the FastAPI systemd unit
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl cat fastapi-tutorial

# Verify required FastAPI unit settings
grep -E '^(Description|After|Type|User|WorkingDirectory|Environment|ExecStart|Restart|WantedBy)=' \
  /etc/systemd/system/fastapi-tutorial.service

# Verify FastAPI instance: fastapi-tutorial
systemctl status fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial

# Verify the FastAPI process and listener
ps aux | grep '[u]vicorn app.main:app'
pgrep -af 'uvicorn app.main:app'
ss -tlnp | grep ':8000'

# Test the FastAPI HTTP endpoint
curl -I http://127.0.0.1:8000/
curl -sS http://127.0.0.1:8000/ | head

# Review service logs
journalctl -u fastapi-tutorial --since "10 minutes ago" --no-pager
journalctl -u postgresql --since "10 minutes ago" --no-pager

# Verify dependency ordering
systemctl show fastapi-tutorial -p After -p Requires -p Wants

# Verify FastAPI restart behavior
systemctl restart fastapi-tutorial
systemctl is-active fastapi-tutorial
curl -I http://127.0.0.1:8000/

# Verify PostgreSQL processes
pgrep -af postgres
```