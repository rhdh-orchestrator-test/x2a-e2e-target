---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI tutorial application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, and platform-specific PostgreSQL development packages; creates a Python virtual environment; installs dependencies from `requirements.txt`; creates the PostgreSQL role `fastapi` and database `fastapi_db`; writes `/opt/fastapi-tutorial/.env`; and manages the `fastapi-tutorial` systemd service. The application runs as `root` through Uvicorn on `0.0.0.0:8000`. The PostgreSQL password is currently hardcoded as `fastapi_password` and must be migrated to the Ansible variable `fastapi_db_password`, stored in Ansible Vault or an approved AAP credential mechanism.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application server
  - Location/Path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Dependency file: `/opt/fastapi-tutorial/requirements.txt`
  - Service unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Service user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Startup command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Listen address: `0.0.0.0`
  - Port: `8000`
  - Restart policy: `always`
  - Systemd dependencies: `network.target`, `postgresql.service`

- **postgresql**: PostgreSQL database service
  - Database user: `fastapi`
  - Database name: `fastapi_db`
  - Database host: `localhost`
  - Database port: PostgreSQL default configured port; no explicit port is configured by the cookbook
  - Connection string: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
  - Password migration variable: `fastapi_db_password`

There is no collection attribute and no `.each` iteration in the recipe.

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

No Chef templates are used. Configuration files are created with inline `file` resources.

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
   - Selects package names based on the platform family.
   - On RHEL/Fedora, installs `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, and `libpq-devel`.
   - On Debian/Ubuntu and other non-RHEL platforms, installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - On RHEL/Fedora, runs `postgresql-setup --initdb` through `execute[initialize_postgresql]`. The plan identifies `/var/lib/pgsql/data/PG_VERSION` as the initialization guard; this guard must be confirmed in the source recipe during migration.
   - Resources used: `package`, `execute[initialize_postgresql]`.

2. **Application directory creation** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/opt/fastapi-tutorial` from `node['fastapi_tutorial']['app_path']`.
   - Sets owner and group to `root`.
   - Sets mode to `0755`.
   - Creates parent directories recursively.
   - Resource used: `directory[node['fastapi_tutorial']['app_path']]`.

3. **Repository synchronization** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git`.
   - Places the repository at `/opt/fastapi-tutorial`.
   - Checks out revision `main`.
   - Resource used: `git[node['fastapi_tutorial']['app_path']]`.

4. **Python virtual environment creation** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Runs `python3 -m venv /opt/fastapi-tutorial/venv`.
   - Creates the environment only when `/opt/fastapi-tutorial/venv` does not exist.
   - Resource used: `execute[create_venv]`.

5. **Python dependency installation** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Runs `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt`.
   - Uses `/opt/fastapi-tutorial` as the working directory.
   - Resource used: `execute[install_dependencies]`.

6. **PostgreSQL service management** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Enables the `postgresql` service at boot.
   - Starts the `postgresql` service immediately.
   - Resource used: `service[postgresql]`.

7. **PostgreSQL role and database creation** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Executes PostgreSQL commands as the `postgres` operating-system user.
   - Creates role `fastapi`.
   - Sets the role password to the current hardcoded value `fastapi_password`.
   - Creates database `fastapi_db` owned by `fastapi`.
   - Grants all privileges on `fastapi_db` to `fastapi`.
   - The Chef commands use `|| true`, suppressing errors when objects already exist.
   - The Ansible migration must use idempotent PostgreSQL modules or controlled `become_user: postgres` commands and must obtain the password from `fastapi_db_password`.
   - Resource used: `execute[create_db_user]`.

8. **Environment file creation** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/opt/fastapi-tutorial/.env`.
   - Writes:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Sets owner and group to `root`.
   - Sets mode to `0644`.
   - The migrated file must use `fastapi_db_password` and safely handle URL encoding for special characters.
   - Resource used: `file[#{node['fastapi_tutorial']['app_path']}/.env]`.

9. **Systemd unit creation** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/etc/systemd/system/fastapi-tutorial.service`.
   - Uses the following unit configuration:
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
   - Sets owner and group to `root`.
   - Sets mode to `0644`.
   - Resource used: `file[/etc/systemd/system/fastapi-tutorial.service]`.

10. **Systemd reload** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
    - Defines `execute[systemd_reload]` with `action :nothing`.
    - Runs `systemctl daemon-reload` when notified by the systemd unit file resource.
    - The notification is immediate:
      `file[/etc/systemd/system/fastapi-tutorial.service]` notifies `execute[systemd_reload]`.

11. **FastAPI service management** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
    - Enables the `fastapi-tutorial` service at boot.
    - Starts the `fastapi-tutorial` service immediately.
    - Resource used: `service[service_name]`.
    - The resolved service name is `fastapi-tutorial`.

The attributes referenced by the recipe are:

- `node['fastapi_tutorial']['app_path']`: `/opt/fastapi-tutorial`
- `node['fastapi_tutorial']['repository']`: `https://github.com/dibanez/fastapi_tutorial.git`
- `node['fastapi_tutorial']['revision']`: `main`
- `node['fastapi_tutorial']['service_port']`: `8000`

These references are documented from the migration plan and should be verified against `cookbooks/fastapi-tutorial/attributes/default.rb`.

## Dependencies

**External cookbook dependencies**: None identified in `metadata.rb`.

**System package dependencies**:

RHEL/Fedora:
- `python3`
- `python3-pip`
- `git`
- `postgresql-server`
- `postgresql-contrib`
- `libpq-devel`

Debian/Ubuntu and other non-RHEL platforms:
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
- `/opt/fastapi-tutorial/requirements.txt`

## Credentials

**Detection Summary**: 1 credential detected in 2 usage locations.

**Source**:
- **Provider**: Hardcoded in the Chef recipe
- **URL**: None detected
- **Path**: None detected

### PostgreSQL application password

- **Variable(s)**:
  - Current Chef value: `fastapi_password`
  - Required Ansible variable: `fastapi_db_password`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
  - Generated file: `/opt/fastapi-tutorial/.env`
- **Current storage**: Hardcoded plaintext in the Chef recipe and generated database URL
- **Usage context**:
  - PostgreSQL role creation:
    ```sql
    CREATE USER fastapi WITH PASSWORD 'fastapi_password';
    ```
  - FastAPI connection string:
    ```dotenv
    DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
    ```
- **Migration requirement**:
  - Store `fastapi_db_password` in Ansible Vault or an approved AAP credential mechanism.
  - Do not expose the plaintext value in playbooks, role defaults, task arguments, or logs.
  - Use the vaulted variable when creating the PostgreSQL role and rendering `.env`.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secret references, TLS certificate references, API tokens, or additional credentials were detected.

## Checks for the Migration

**Files to verify**:
- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- `/var/lib/pgsql/data/PG_VERSION` on RHEL/Fedora
- PostgreSQL database `fastapi_db`
- PostgreSQL role `fastapi`

**Service endpoints to check**:
- FastAPI: `http://127.0.0.1:8000/`
- FastAPI listener: `0.0.0.0:8000`
- PostgreSQL host: `localhost`
- PostgreSQL port: default configured PostgreSQL port

**Templates rendered**:
- No Chef templates are rendered.
- `/opt/fastapi-tutorial/.env` — inline `file` resource, rendered once.
- `/etc/systemd/system/fastapi-tutorial.service` — inline `file` resource, rendered once.

## Pre-flight checks

### Platform and package checks

RHEL/Fedora:
```bash
rpm -q python3
rpm -q python3-pip
rpm -q git
rpm -q postgresql-server
rpm -q postgresql-contrib
rpm -q libpq-devel
test -f /var/lib/pgsql/data/PG_VERSION
```

Debian/Ubuntu:
```bash
dpkg -s python3
dpkg -s python3-pip
dpkg -s python3-venv
dpkg -s git
dpkg -s postgresql
dpkg -s postgresql-contrib
dpkg -s libpq-dev
```

### PostgreSQL instance checks

```bash
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
sudo -u postgres psql -tAc "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"
sudo -u postgres psql -tAc "SELECT datname, pg_catalog.pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"
```

Expected role:
```text
fastapi
```

Expected database and owner:
```text
fastapi_db|fastapi
```

Test PostgreSQL connectivity without embedding a real password in the command history:
```bash
PGPASSWORD='REPLACE_WITH_VAULTED_PASSWORD' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_database(), current_user;"
```

Check PostgreSQL logs:
```bash
journalctl -u postgresql --no-pager -n 100
```

### FastAPI application instance checks

```bash
test -d /opt/fastapi-tutorial
test -d /opt/fastapi-tutorial/venv
test -f /opt/fastapi-tutorial/requirements.txt
test -x /opt/fastapi-tutorial/venv/bin/python3
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
git -C /opt/fastapi-tutorial rev-parse HEAD
```

### Environment file checks

```bash
stat -c '%U:%G %a %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION)=' /opt/fastapi-tutorial/.env
sed -E 's#(postgresql://[^:]+:)[^@]+(@.*)#\1REDACTED\2#' \
  /opt/fastapi-tutorial/.env
```

Expected permissions:
```text
root:root 644 /opt/fastapi-tutorial/.env
```

Expected redacted database URL:
```text
DATABASE_URL=postgresql://fastapi:REDACTED@localhost/fastapi_db
```

### FastAPI systemd instance checks

```bash
test -f /etc/systemd/system/fastapi-tutorial.service
stat -c '%U:%G %a %n' /etc/systemd/system/fastapi-tutorial.service
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl daemon-reload
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl status fastapi-tutorial
```

Verify required settings:
```bash
grep -E '^(Description|After|Type|User|WorkingDirectory|Environment|ExecStart|Restart|WantedBy)=' \
  /etc/systemd/system/fastapi-tutorial.service
```

Expected values include:
```text
Description=FastAPI Tutorial Service
After=network.target postgresql.service
Type=simple
User=root
WorkingDirectory=/opt/fastapi-tutorial
Environment="PATH=/opt/fastapi-tutorial/venv/bin"
ExecStart=/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
WantedBy=multi-user.target
```

Check the process and listener:
```bash
pgrep -af '/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app'
ss -tlnp | grep ':8000'
curl -i http://127.0.0.1:8000/
```

Expected listener:
```text
0.0.0.0:8000
```

Check FastAPI logs:
```bash
journalctl -u fastapi-tutorial --no-pager -n 100
```

### Resource and path checks

```bash
ls -ld /opt/fastapi-tutorial
ls -ld /opt/fastapi-tutorial/venv
ls -l /opt/fastapi-tutorial/.env
ls -l /etc/systemd/system/fastapi-tutorial.service
systemctl show fastapi-tutorial \
  --property=User \
  --property=WorkingDirectory \
  --property=ExecStart \
  --property=Restart
```

The migration is complete when the `postgresql` instance is active and enabled, role `fastapi` can connect to database `fastapi_db`, the virtual environment contains the application dependencies, the `fastapi-tutorial` systemd unit is valid and enabled, and the FastAPI instance is listening on TCP port `8000`.