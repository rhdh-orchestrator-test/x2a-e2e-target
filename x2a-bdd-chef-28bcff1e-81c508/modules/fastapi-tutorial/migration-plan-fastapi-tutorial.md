---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI tutorial application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, and PostgreSQL development dependencies using platform-specific package names, creates a Python virtual environment, installs the repository requirements, provisions PostgreSQL database `fastapi_db` and user `fastapi`, writes a root-owned environment file containing the database connection URL, and manages a systemd service named `fastapi-tutorial` listening on port `8000`.

## Service Type and Instances

**Service Type**: Application Server with PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application served by Uvicorn
  - Location/Path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Service user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Port/Socket: TCP `8000`
  - Listening address: `0.0.0.0`
  - Restart policy: `always`

- **postgresql**: Application database service
  - Database user: `fastapi`
  - Database name: `fastapi_db`
  - Host: `localhost`
  - Port: `5432`
  - Database URL: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
  - Service dependency: PostgreSQL must be enabled and started before the application

No collection attributes or `.each` loops are present in this cookbook.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

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

No Chef templates are rendered. The environment file and systemd unit are generated directly by `file` resources using inline content.

**Attributes:**
```text
cookbooks/fastapi-tutorial/attributes/default.rb
```

**Files:**
```text
```

No static files are deployed using `cookbook_file` or `remote_file`.

## Module Explanation

The cookbook performs operations in the following order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Selects the Fedora/RHEL or non-Fedora/RHEL package branch.
   - On Fedora/RHEL, installs `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, and `libpq-devel`.
   - On Fedora/RHEL, runs `postgresql-setup --initdb` through `execute[initialize_postgresql]` unless `/var/lib/pgsql/data/PG_VERSION` already exists.
   - On other platforms, installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Package versions are not pinned.
   - Creates `/opt/fastapi-tutorial` with owner `root`, group `root`, mode `0755`, and recursive creation enabled.

2. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Synchronizes the Git repository into `/opt/fastapi-tutorial`.
   - Uses repository `https://github.com/dibanez/fastapi_tutorial.git` and revision `main`.
   - The repository is synchronized before dependency installation so `/opt/fastapi-tutorial/requirements.txt` is available.

3. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates the virtual environment using `execute[create_venv]`.
   - Runs `python3 -m venv /opt/fastapi-tutorial/venv`.
   - Uses `/opt/fastapi-tutorial/venv` as the idempotence guard.
   - The virtual environment is created under the application directory and has no separately assigned application user.

4. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs Python dependencies through `execute[install_dependencies]`.
   - Runs `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt`.
   - Uses `/opt/fastapi-tutorial` as the working directory.
   - Dependency versions and package names come from the repository’s `requirements.txt`.

5. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Enables and starts `service[postgresql]`.
   - Uses service name `postgresql`.

6. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates the PostgreSQL role and database through `execute[create_db_user]`.
   - Runs, in order:
     ```bash
     sudo -u postgres psql -c "CREATE USER fastapi WITH PASSWORD 'fastapi_password';" || true
     sudo -u postgres psql -c "CREATE DATABASE fastapi_db OWNER fastapi;" || true
     sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE fastapi_db TO fastapi;" || true
     ```
   - Configures role `fastapi`, database `fastapi_db`, password `fastapi_password`, owner `fastapi`, and `ALL PRIVILEGES` on `fastapi_db`.
   - The original implementation is shell-based, non-transactional, and suppresses errors with `|| true`.
   - The migration should preferably use `community.postgresql.postgresql_user`, `community.postgresql.postgresql_db`, and `community.postgresql.postgresql_privs` for idempotence.

7. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/opt/fastapi-tutorial/.env` using an inline `file` resource.
   - Sets owner `root`, group `root`, and mode `0644`.
   - Writes:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - The migrated file should generate the password from a vaulted or approved secret variable.
   - The Chef execution tree does not show a notification from this file; do not add an automatic application restart unless intentionally approved.

8. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/etc/systemd/system/fastapi-tutorial.service` using an inline `file` resource.
   - Sets owner `root`, group `root`, and mode `0644`.
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
   - Preserves service name `fastapi-tutorial`, user `root`, working directory, Uvicorn path, address, port, restart policy, and PostgreSQL/network ordering.
   - Running the application as `root` is existing behavior and a security concern. Introducing a dedicated service account requires separate approval.

9. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Defines `execute[systemd_reload]` with command `systemctl daemon-reload` and action `nothing`.
   - The systemd unit notifies this resource immediately when the unit file changes.
   - The Ansible equivalent is a handler using `ansible.builtin.systemd` with `daemon_reload: true`.

10. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
    - Enables and starts `service[fastapi-tutorial]`.
    - Uses service name `fastapi-tutorial`.
    - The migrated systemd task must preserve enablement, startup, and daemon reload behavior.
    - The Chef recipe does not explicitly restart the service when the unit changes; any restart behavior must be an intentional migration decision.

## Dependencies

**External cookbook dependencies**: None declared in the supplied `metadata.rb`.

**System package dependencies**:

- Fedora/RHEL:
  - `python3`
  - `python3-pip`
  - `git`
  - `postgresql-server`
  - `postgresql-contrib`
  - `libpq-devel`
  - Initialization command: `postgresql-setup --initdb`
- Non-Fedora/RHEL:
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
- The FastAPI unit must retain `After=network.target postgresql.service`.

## Credentials

**Detection Summary**: 1 credential detected across 1 file.

**Source**:
  - **Provider**: Hardcoded in the Chef recipe; no Vault, CyberArk, AWS Secrets Manager, Chef Vault, encrypted data bag, or regular data bag usage detected
  - **URL**: No external secret provider URL
  - **Path**: `cookbooks/fastapi-tutorial/recipes/default.rb`

### PostgreSQL application password

- **Variable(s)**: No Chef attribute variable; literal value is `fastapi_password`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the PostgreSQL creation command and repeated in the generated `.env` database URL
- **Usage context**:
  - PostgreSQL role creation:
    ```text
    CREATE USER fastapi WITH PASSWORD 'fastapi_password';
    ```
  - Application connection string:
    ```text
    DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
    ```
- **Database identity**:
  - User: `fastapi`
  - Database: `fastapi_db`
  - Host: `localhost`

Store the password in Ansible Vault or an approved secret-management integration. Do not reproduce `fastapi_password` as plaintext in Ansible defaults, task files, or committed templates. No SSL/TLS certificate, private key, API key, token, or environment-variable-based secret reference was detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- Fedora/RHEL PostgreSQL data directory: `/var/lib/pgsql/data`
- Non-Fedora/RHEL distribution-managed PostgreSQL data directory

**Service endpoints to check**:

- `fastapi-tutorial`: TCP `8000`
- `postgresql`: TCP `5432`, if TCP listening is enabled
- PostgreSQL local Unix socket, typically under `/var/run/postgresql` or `/var/lib/pgsql`

**Database objects to verify**:

- PostgreSQL role `fastapi`
- PostgreSQL database `fastapi_db`
- Role ownership of `fastapi_db`
- `ALL PRIVILEGES` granted to `fastapi` on `fastapi_db`

**Templates rendered**:

- No `.erb` templates rendered: `0`
- No Chef templates are present

**Inline files created**:

- `/opt/fastapi-tutorial/.env`: 1 file
- `/etc/systemd/system/fastapi-tutorial.service`: 1 file

## Pre-flight checks

```bash
# Verify required packages and tools
python3 --version
pip3 --version
git --version

# Verify the FastAPI instance directory and checkout
ls -ld /opt/fastapi-tutorial
git -C /opt/fastapi-tutorial status
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
test -f /opt/fastapi-tutorial/requirements.txt

# Verify the FastAPI instance virtual environment
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip --version
/opt/fastapi-tutorial/venv/bin/pip list

# Verify the PostgreSQL instance
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
sudo -u postgres psql -c "SELECT version();"

# Verify PostgreSQL role and database
sudo -u postgres psql -tAc "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"
sudo -u postgres psql -tAc "SELECT datname, pg_catalog.pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"
sudo -u postgres psql -c "\l+ fastapi_db"

# Verify application access to PostgreSQL
PGPASSWORD='<retrieve-from-Ansible-Vault>' \
psql -h localhost -U fastapi -d fastapi_db -c "SELECT current_database(), current_user;"

# Verify PostgreSQL endpoint
ss -tlnp | grep ':5432'

# Verify the FastAPI environment file without exposing its password
stat -c '%U %G %a %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION)=' /opt/fastapi-tutorial/.env
sed -E 's#(postgresql://[^:]+:)[^@]+#\1********#' /opt/fastapi-tutorial/.env

# Verify the FastAPI systemd unit
systemctl cat fastapi-tutorial
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl show fastapi-tutorial \
  --property=User \
  --property=WorkingDirectory \
  --property=ExecStart \
  --property=Restart
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl status fastapi-tutorial

# Verify the FastAPI endpoint and process
ss -tlnp | grep ':8000'
lsof -iTCP:8000 -sTCP:LISTEN
curl -i http://127.0.0.1:8000/
ps aux | grep '[u]vicorn'
journalctl -u fastapi-tutorial --no-pager -n 100

# Verify service ordering
systemctl is-active postgresql
systemctl is-active fastapi-tutorial
systemctl show fastapi-tutorial \
  --property=After \
  --property=Wants \
  --property=Requires
```

Expected environment values:

```text
PROJECT_NAME="FastAPI Tutorial"
API_VERSION=1.0.0
```

Expected FastAPI systemd settings:

```text
User=root
WorkingDirectory=/opt/fastapi-tutorial
ExecStart=/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
```

The root endpoint must return an HTTP response from the application. The exact status code depends on the repository application code. A connection refusal or systemd crash indicates a deployment failure. The PostgreSQL password placeholder must be supplied securely during validation and must not be committed to shell history or source files.