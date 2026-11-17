---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys a FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, and PostgreSQL development packages; creates the application directory and Python virtual environment; installs application dependencies; enables and starts PostgreSQL; creates the `fastapi` PostgreSQL role and `fastapi_db` database; writes an application `.env` file; and manages the application through a systemd service named `fastapi-tutorial` on port `8000`. The exact attribute defaults, file contents, permissions, and some resource guards should be verified against the underlying Chef source before migration.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application served by Uvicorn
  - Location/Path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Service user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Startup command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Listening address: `0.0.0.0`
  - Port: `8000`
  - Restart policy: `always`

- **postgresql**: Local PostgreSQL database service
  - Service name: `postgresql`
  - Database user: `fastapi`
  - Database name: `fastapi_db`
  - Database owner: `fastapi`
  - Host: `localhost`
  - Port: `5432`
  - Password: `fastapi_password` in the existing Chef implementation; store the migrated value in an approved secret store

No Chef collection attributes or `.each` iterations are present in the supplied execution tree.

## File Structure

Only files shown in the supplied execution tree and directory listing are included.

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

No Chef templates are rendered. The `.env` file and systemd unit are created directly with Chef `file` resources.

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
   - Branches on `platform_family?('fedora', 'rhel')`.
   - On Fedora/RHEL, installs `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, and `libpq-devel`.
   - On non-Fedora/RHEL platforms, installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Runs `execute[initialize_postgresql]` with `postgresql-setup --initdb` on Fedora/RHEL.
   - The supplied analysis confirms the initialization command but does not confirm an existence guard for `/var/lib/pgsql/data/PG_VERSION`. The Ansible migration should verify the Chef source and add an idempotent guard if appropriate.
   - The package branches are mutually exclusive.

2. **Application directory creation** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/opt/fastapi-tutorial`.
   - The analyzed resource is `directory[node['fastapi_tutorial']['app_path']]`.
   - The intended configuration is owner `root`, group `root`, mode `0755`, with recursive creation.

3. **Repository synchronization** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` into `/opt/fastapi-tutorial`.
   - Uses revision `main`.
   - The analyzed resource is `git[node['fastapi_tutorial']['app_path']]`.

4. **Python virtual environment creation** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Runs `python3 -m venv /opt/fastapi-tutorial/venv`.
   - Uses `execute[create_venv]`.
   - The supplied analysis confirms the command but does not confirm a guard for `/opt/fastapi-tutorial/venv`. Ansible should use an idempotent `creates` condition only after verifying the intended Chef behavior.

5. **Python dependency installation** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Runs `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt`.
   - Uses `/opt/fastapi-tutorial` as the working directory.
   - Uses `execute[install_dependencies]`.
   - The analyzed command has no confirmed conditional guard.

6. **PostgreSQL service management** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Enables and starts the `postgresql` service.
   - Uses `service[postgresql]`.

7. **PostgreSQL role and database creation** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Uses `execute[create_db_user]`.
   - Runs PostgreSQL commands as the PostgreSQL operating-system user:
     - Creates role `fastapi`.
     - Sets the role password to `fastapi_password`.
     - Creates database `fastapi_db` owned by `fastapi`.
     - Grants all privileges on `fastapi_db` to `fastapi`.
   - The existing shell commands use `|| true`, suppressing both already-exists conditions and unrelated errors.
   - The Ansible implementation should use `community.postgresql.postgresql_user`, `community.postgresql.postgresql_db`, and, if required, `community.postgresql.postgresql_privs` with `become_user: postgres`.

8. **Application environment file** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/opt/fastapi-tutorial/.env` through a Chef `file` resource.
   - The analyzed execution tree confirms the file resource but does not independently confirm its content, ownership, or mode.
   - The reported intended content is:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - The reported intended ownership is `root:root` with mode `0644`; verify these values against the recipe.
   - In Ansible, store the database password in Ansible Vault, an AAP credential, or another approved secret provider. Prefer mode `0600` for the migrated `.env` file.

9. **Systemd unit creation** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/etc/systemd/system/fastapi-tutorial.service` through a Chef `file` resource.
   - The analyzed execution tree confirms the file resource and dynamically named service path but does not independently confirm the unit contents or file properties.
   - The reported intended unit content is:
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
   - Verify the reported owner `root`, group `root`, and mode `0644` against the Chef source.
   - The Ansible implementation should use `ansible.builtin.copy` or `ansible.builtin.template`.

10. **Systemd reload** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
    - Defines `execute[systemd_reload]` with action `:nothing`.
    - The resource runs `systemctl daemon-reload`.
    - The unit file resource notifies it immediately when the unit changes.
    - Ansible should implement this behavior with a handler or `daemon_reload: true`.

11. **FastAPI service management** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
    - Enables and starts the dynamically named `fastapi-tutorial` service.
    - The corresponding unit is `fastapi-tutorial.service`.
    - Uses `service[service_name]`.
    - Ansible should manage the service with `ansible.builtin.systemd`, enabled and started after the unit is deployed and systemd has reloaded.

## Dependencies

**External cookbook dependencies**: None shown in the supplied metadata or execution tree.

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

- Requirements file: `/opt/fastapi-tutorial/requirements.txt`
- Virtual environment: `/opt/fastapi-tutorial/venv`

**Execution order dependency chain**:

1. Install operating-system packages.
2. Initialize PostgreSQL on Fedora/RHEL if required.
3. Create `/opt/fastapi-tutorial`.
4. Synchronize the Git repository.
5. Create the Python virtual environment.
6. Install Python requirements.
7. Enable and start PostgreSQL.
8. Create the PostgreSQL role and database.
9. Write `.env`.
10. Write the systemd unit.
11. Reload systemd when the unit changes.
12. Enable and start `fastapi-tutorial`.

## Credentials

**Detection Summary**: 2 sensitive credential references detected in 1 source file.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None
- **Path**: None

### PostgreSQL application username

- **Variable/value**: `fastapi`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in PostgreSQL shell commands and `.env` content
- **Usage context**:
  - PostgreSQL role creation
  - Database ownership
  - Application connection string:
    `postgresql://fastapi:fastapi_password@localhost/fastapi_db`

### PostgreSQL application password

- **Variable/value**: `fastapi_password`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded plaintext
- **Usage context**:
  - PostgreSQL role password
  - Application `DATABASE_URL` in `/opt/fastapi-tutorial/.env`

The migrated password must not remain in normal inventory or task files. Store it in Ansible Vault, an AAP credential, or an approved external secret provider. No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, CyberArk, Conjur, or environment-variable-based secret lookup was detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial/`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv/`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- Fedora/RHEL PostgreSQL data directory: `/var/lib/pgsql/data/`
- Distribution-managed PostgreSQL data directory on non-Fedora/RHEL systems
- PostgreSQL logs from the `postgresql` systemd unit
- FastAPI logs from the `fastapi-tutorial` systemd unit

**Service endpoints to check**:

- `fastapi-tutorial`: TCP port `8000`, bind address `0.0.0.0`
- `postgresql`: TCP port `5432`, host `localhost`
- PostgreSQL Unix socket: distribution-managed path; not explicitly set by the cookbook

**Templates rendered**:

- No `.erb` templates are used.
- `/opt/fastapi-tutorial/.env` — rendered once by a Chef `file` resource
- `/etc/systemd/system/fastapi-tutorial.service` — rendered once by a Chef `file` resource

## Pre-flight checks

```bash
# Verify operating-system tools
python3 --version
git --version
psql --version

# Verify the application instance
ls -ld /opt/fastapi-tutorial
ls -l /opt/fastapi-tutorial/requirements.txt
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/uvicorn --version

# Verify the PostgreSQL instance
systemctl status postgresql --no-pager
systemctl is-enabled postgresql
systemctl is-active postgresql
ss -ltnp | grep ':5432'

# Verify the PostgreSQL role and database
sudo -u postgres psql -d postgres -c "\du fastapi"
sudo -u postgres psql -d postgres -c "\l+ fastapi_db"

# Verify application-database connectivity using the approved secret store
PGPASSWORD='RETRIEVE_FROM_APPROVED_SECRET_STORE' \
  psql -h localhost -U fastapi -d fastapi_db -c "SELECT version();"

PGPASSWORD='RETRIEVE_FROM_APPROVED_SECRET_STORE' \
  psql -h localhost -U fastapi -d fastapi_db -c "SELECT current_database(), current_user;"

# Verify the application environment file without exposing its password
ls -l /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION)=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env | \
  sed -E 's#(postgresql://[^:]+:)[^@]+#\1REDACTED#'

# Verify the FastAPI systemd instance
systemctl cat fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl status fastapi-tutorial --no-pager
systemctl show fastapi-tutorial \
  --property=LoadState,ActiveState,SubState,ExecMainStatus

# Verify the FastAPI process and endpoint
ps aux | grep '[u]vicorn app.main:app'
ss -ltnp | grep ':8000'
lsof -iTCP:8000 -sTCP:LISTEN
curl -i http://127.0.0.1:8000/
curl -sS -o /dev/null -w 'HTTP status: %{http_code}\n' \
  http://127.0.0.1:8000/

# Verify application dependencies and repository state
/opt/fastapi-tutorial/venv/bin/pip freeze
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
git -C /opt/fastapi-tutorial rev-parse HEAD

# Verify logs for each named service
journalctl -u postgresql --no-pager -n 100
journalctl -u fastapi-tutorial --no-pager -n 100

# Verify the systemd unit path after reload
systemctl daemon-reload
systemctl show fastapi-tutorial --property=FragmentPath
```

Expected FastAPI service values:

```text
LoadState=loaded
ActiveState=active
SubState=running
ExecMainStatus=0
```

The expected systemd fragment path is:

```text
/etc/systemd/system/fastapi-tutorial.service
```

The cookbook does not define a dedicated health endpoint. The root endpoint `/` is the available generic HTTP check; confirm a successful TCP connection and an application HTTP response rather than assuming a specific HTTP status code.