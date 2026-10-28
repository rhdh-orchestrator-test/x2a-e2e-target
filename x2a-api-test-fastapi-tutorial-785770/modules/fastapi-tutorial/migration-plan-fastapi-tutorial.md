---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the `fastapi-tutorial` FastAPI application from the `main` branch of `https://github.com/dibanez/fastapi_tutorial.git` to `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, and PostgreSQL development packages; creates a Python virtual environment; installs application dependencies; creates the PostgreSQL `fastapi` role and `fastapi_db` database; writes an environment file containing the database connection string; and manages the `fastapi-tutorial.service` systemd unit running Uvicorn on `0.0.0.0:8000`.

## Service Type and Instances

**Service Type**: Application Server with PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application server
  - Location/Path: `/opt/fastapi-tutorial`
  - Source repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Dependency file: `/opt/fastapi-tutorial/requirements.txt`
  - Application command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Port/Socket: `0.0.0.0:8000`
  - Systemd unit: `fastapi-tutorial.service`
  - Systemd user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Restart policy: `always`
  - Environment file: `/opt/fastapi-tutorial/.env`
  - Environment path: `/opt/fastapi-tutorial/venv/bin`

- **postgresql**: PostgreSQL service supporting the FastAPI application
  - Service name: `postgresql`
  - Database role: `fastapi`
  - Database: `fastapi_db`
  - Database owner: `fastapi`
  - Port/Socket: `localhost:5432` expected
  - Connection string: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`

## File Structure

**MANDATORY: Preserve this section from the original plan.**

```text
cookbooks/fastapi-tutorial/recipes/default.rb
```

**Recipes:**
```text
cookbooks/fastapi-tutorial/recipes/default.rb
```

**Providers:**
```text
None
```

**Templates:**
```text
None
```

**Attributes:**
```text
None
```

**Files:**
```text
None
```

The cookbook does not use Chef templates, static cookbook files, custom resources, provider files, included recipes, or attribute files.

## Module Explanation

The cookbook performs operations in this order:

1. **Install system packages** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Equivalent Ansible resource: `ansible.builtin.package`.
   - No package versions are specified.
   - These package names are Debian/Ubuntu-oriented. The cookbook metadata declares CentOS support, but no platform-specific package mapping appears in the recipe; distribution-specific mappings are required if CentOS/RHEL support is needed.

2. **Create the application directory** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/opt/fastapi-tutorial` recursively.
   - Sets owner and group to `root:root`.
   - Sets mode to `0755`.
   - Equivalent Ansible resource: `ansible.builtin.file` with `state: directory`.

3. **Synchronize the application Git repository** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Synchronizes `/opt/fastapi-tutorial`.
   - Uses repository `https://github.com/dibanez/fastapi_tutorial.git`.
   - Checks out revision `main`.
   - Equivalent Ansible resource: `ansible.builtin.git`.

4. **Create the Python virtual environment** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Runs `python3 -m venv /opt/fastapi-tutorial/venv`.
   - Uses `/opt/fastapi-tutorial/venv` as the creation guard.
   - Equivalent Ansible resource: `ansible.builtin.command` with `creates: /opt/fastapi-tutorial/venv`.

5. **Install Python dependencies** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Runs `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt`.
   - Uses `/opt/fastapi-tutorial` as the working directory.
   - Installs dependencies into `/opt/fastapi-tutorial/venv`.
   - Equivalent Ansible resource: `ansible.builtin.command` or `ansible.builtin.pip`.
   - The Chef recipe does not notify or conditionally restart the application after dependency installation.

6. **Enable and start PostgreSQL** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Enables the `postgresql` service.
   - Starts the `postgresql` service.
   - Equivalent Ansible resource: `ansible.builtin.service` with `enabled: true` and `state: started`.
   - PostgreSQL must be available before database initialization.

7. **Create the PostgreSQL role and database** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Runs PostgreSQL commands as the `postgres` operating-system user.
   - Creates role `fastapi` with password `fastapi_password`.
   - Creates database `fastapi_db` owned by `fastapi`.
   - Grants all privileges on `fastapi_db` to `fastapi`.
   - The Chef commands suppress errors with `|| true` for repeat execution.
   - Preferred Ansible resources are `community.postgresql.postgresql_user`, `community.postgresql.postgresql_db`, and, if required, `community.postgresql.postgresql_privs`.
   - Database tasks should use `become_user: postgres` rather than unconditional shell commands.

8. **Create the application environment file** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/opt/fastapi-tutorial/.env`.
   - Writes the following exact values:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Sets owner and group to `root:root`.
   - Sets mode to `0644`.
   - Equivalent Ansible resource: `ansible.builtin.copy` with inline content, or a template if variable substitution is required.
   - `DATABASE_URL` contains a plaintext password and should be sourced from Ansible Vault during migration.

9. **Create the systemd service unit** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/etc/systemd/system/fastapi-tutorial.service`.
   - Sets owner and group to `root:root`.
   - Sets mode to `0644`.
   - Uses the following unit content:
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
   - Starts after `network.target` and orders after `postgresql.service`.
   - Runs `app.main:app` as `root` from `/opt/fastapi-tutorial`.
   - Listens on all interfaces at port `8000`.
   - Restarts automatically when the process exits.
   - Is enabled through `multi-user.target`.
   - Equivalent Ansible resource: `ansible.builtin.copy` or `ansible.builtin.template`.
   - Unit changes must notify a systemd daemon reload handler.

10. **Reload systemd** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
    - Defines `execute['systemd_reload']`.
    - Runs `systemctl daemon-reload`.
    - The Chef resource uses action `nothing`.
    - The systemd unit file notifies the reload immediately when it changes.
    - Equivalent Ansible handler: `ansible.builtin.systemd` with `daemon_reload: true`.

11. **Enable and start the FastAPI service** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
    - Enables `fastapi-tutorial.service`.
    - Starts `fastapi-tutorial.service`.
    - Equivalent Ansible resource: `ansible.builtin.service` or `ansible.builtin.systemd`.
    - The daemon reload must occur before startup when the unit is created or modified.

## Dependencies

**External cookbook dependencies**: None listed in the analyzed metadata or execution tree.

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
- `/opt/fastapi-tutorial/requirements.txt`
- Installed into `/opt/fastapi-tutorial/venv`

## Credentials

**Detection Summary**: 1 credential detected in 2 source locations within `cookbooks/fastapi-tutorial/recipes/default.rb`.

**Source**:
- **Provider**: Hardcoded in the Chef recipe
- **URL**: None
- **Path**: None
- **Storage method**: Plaintext PostgreSQL command and plaintext environment file

### PostgreSQL password

- **Variable(s)**: Password for PostgreSQL role `fastapi`; value in source: `fastapi_password`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Source locations**:
  - `CREATE USER fastapi WITH PASSWORD 'fastapi_password';`
  - `DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Current storage**: Hardcoded plaintext in the Chef recipe and generated `/opt/fastapi-tutorial/.env`
- **Usage context**:
  - Creates the PostgreSQL role `fastapi`.
  - Authenticates the FastAPI application to the `fastapi_db` database.
- **Migration guidance**:
  - Store the password in Ansible Vault.
  - Use the vaulted value with `community.postgresql.postgresql_user`.
  - Render the vaulted value into `DATABASE_URL` without committing plaintext to the playbook or repository.
  - Consider mode `0600` for `/opt/fastapi-tutorial/.env` as a security improvement, although the Chef recipe specifies `0644`.

No Chef data bags, encrypted data bags, Chef Vault calls, CyberArk integration, Conjur integration, AWS Secrets Manager references, environment-variable secret lookups, TLS certificate paths, API keys, or tokens were identified.

## Checks for the Migration

**Files to verify**:
- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Database objects to verify**:
- PostgreSQL role `fastapi`
- PostgreSQL database `fastapi_db`
- Owner of `fastapi_db`: `fastapi`
- All privileges granted to `fastapi` on `fastapi_db`

**Service endpoints to check**:
- `fastapi-tutorial`: `0.0.0.0:8000`
- `postgresql`: `localhost:5432` expected
- Unix sockets: no explicit socket path configured

**Templates rendered**:
- No Chef templates are used.
- `/opt/fastapi-tutorial/.env`: rendered once by the Chef `file` resource.
- `/etc/systemd/system/fastapi-tutorial.service`: rendered once by the Chef `file` resource.

**Service reload and restart behavior**:
- Changes to `/etc/systemd/system/fastapi-tutorial.service` trigger `systemctl daemon-reload`.
- The Chef recipe does not explicitly restart `fastapi-tutorial` after unit-file changes.
- The service is enabled and started after the unit file resource.
- The systemd unit uses `Restart=always` for process failures.

## Pre-flight checks

### `fastapi-tutorial` application instance

```bash
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev
test -d /opt/fastapi-tutorial
stat -c '%A %U:%G %n' /opt/fastapi-tutorial
test -d /opt/fastapi-tutorial/venv
test -f /opt/fastapi-tutorial/requirements.txt

test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip --version
/opt/fastapi-tutorial/venv/bin/pip check

cd /opt/fastapi-tutorial
/opt/fastapi-tutorial/venv/bin/python -c "from app.main import app; print(app)"

stat -c '%A %U:%G %n' /opt/fastapi-tutorial/.env
grep '^PROJECT_NAME=' /opt/fastapi-tutorial/.env
grep '^API_VERSION=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env | sed -E 's#://[^:]+:[^@]+@#://***:***@#'

systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl daemon-reload
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl status fastapi-tutorial

systemctl show fastapi-tutorial \
  --property=User,WorkingDirectory,ExecStart,Restart,Environment

ps aux | grep '[u]vicorn'
pgrep -af 'uvicorn app.main:app'
ss -ltnp | grep ':8000'
curl -I http://127.0.0.1:8000/
journalctl -u fastapi-tutorial --no-pager -n 100

stat -c '%A %U:%G %n' /etc/systemd/system/fastapi-tutorial.service
```

Expected application values:
- `User=root`
- `WorkingDirectory=/opt/fastapi-tutorial`
- Uvicorn executable: `/opt/fastapi-tutorial/venv/bin/uvicorn`
- `--host 0.0.0.0`
- `--port 8000`
- `Restart=always`
- `/etc/systemd/system/fastapi-tutorial.service`: `root:root`, mode `0644`
- `/opt/fastapi-tutorial/.env`: `root:root`, mode `0644` unless the migration intentionally applies the security improvement to use `0600`

The HTTP request should receive a response from the FastAPI application. No dedicated `/health` endpoint is defined.

### `postgresql` service instance

```bash
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
ss -ltnp | grep ':5432'
journalctl -u postgresql --no-pager -n 100

sudo -u postgres psql -d postgres -c "\du fastapi"
sudo -u postgres psql -d postgres -c "\l+ fastapi_db"
sudo -u postgres psql -d fastapi_db -c "\dp"

PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_user, current_database();"
```

Expected database values:
- PostgreSQL service is enabled and active.
- PostgreSQL listens on the expected default port `5432`.
- Role `fastapi` exists.
- Database `fastapi_db` exists and is owned by `fastapi`.
- `current_user` is `fastapi`.
- `current_database` is `fastapi_db`.

### Platform package verification

For RPM-based systems, use the equivalent package query:

```bash
rpm -q python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev
```

The package names may require distribution-specific mappings on CentOS/RHEL systems.