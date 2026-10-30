---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, PostgreSQL development libraries, and application dependencies; creates a Python virtual environment; configures the `fastapi` PostgreSQL role and `fastapi_db` database; writes the application `.env` file and systemd unit; and enables and starts PostgreSQL and the FastAPI service. The application runs as `root` under Uvicorn and listens on `0.0.0.0:8000`.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application served by Uvicorn
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Application directory: `/opt/fastapi-tutorial`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Working directory: `/opt/fastapi-tutorial`
  - Start command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Listen address: `0.0.0.0`
  - Port: `8000`
  - Run user: `root`
  - Restart policy: `Restart=always`
  - Service unit: `fastapi-tutorial.service`

- **postgresql**: PostgreSQL database service
  - Service actions: enable and start
  - Database user: `fastapi`
  - Database: `fastapi_db`
  - Database owner: `fastapi`
  - Database privileges: all privileges on `fastapi_db` granted to `fastapi`
  - Application host: `localhost`
  - Port: Not explicitly configured; verify the active platform PostgreSQL port on the target host

## File Structure

Only the recipe file shown in the execution tree is used.

**Recipes:**

```text
recipes/default.rb
```

**Providers:**

```text
```

No custom resource providers are used.

**Templates:**

```text
```

No Chef templates are rendered. The `.env` file and systemd unit are created with inline `file` resources.

**Attributes:**

```text
```

No attribute files are shown or used.

**Files:**

```text
```

No static files are deployed with `cookbook_file` or `remote_file`.

## Module Explanation

The cookbook performs operations in this order:

1. **Install system packages** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Uses one Chef `package` resource containing seven package names.
   - Package installation precedes application checkout, virtual-environment creation, dependency installation, and PostgreSQL configuration.

2. **Create the application directory** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/opt/fastapi-tutorial` recursively.
   - Sets owner and group to `root`.
   - Sets mode to `0755`.
   - Uses one `directory` resource.

3. **Synchronize the Git repository** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git`.
   - Uses destination `/opt/fastapi-tutorial`.
   - Checks out revision `main`.
   - Uses one `git` resource with action `sync`.

4. **Create the Python virtual environment** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Executes `python3 -m venv /opt/fastapi-tutorial/venv`.
   - Guards execution with the existence of `/opt/fastapi-tutorial/venv`.
   - Uses `execute[create_venv]`.

5. **Install Python dependencies** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Runs `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt`.
   - Uses working directory `/opt/fastapi-tutorial`.
   - Runs explicitly during convergence.
   - Uses `execute[install_dependencies]`.

6. **Enable and start PostgreSQL** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Enables and starts the `postgresql` service.
   - Uses `service[postgresql]`.
   - Runs before database initialization.

7. **Create the PostgreSQL user and database** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Runs commands as the `postgres` operating-system user.
   - Creates PostgreSQL role `fastapi` with password `fastapi_password`.
   - Creates database `fastapi_db` owned by `fastapi`.
   - Grants all privileges on `fastapi_db` to `fastapi`.
   - The original commands use `|| true`; the migration should use PostgreSQL-specific idempotent modules rather than suppressing unrelated errors.
   - Uses `execute[create_db_user]`.

8. **Create the application environment file** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/opt/fastapi-tutorial/.env`.
   - Sets owner and group to `root`.
   - Sets mode to `0644` in the source cookbook; the migration should protect the embedded password with Ansible Vault or an external secret provider and use an appropriately restrictive mode.
   - Writes:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Uses `file[/opt/fastapi-tutorial/.env]`.

9. **Create the systemd service unit** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/etc/systemd/system/fastapi-tutorial.service`.
   - Sets owner and group to `root`.
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
   - Uses `file[/etc/systemd/system/fastapi-tutorial.service]`.
   - Immediately notifies `execute[systemd_reload]` when the unit changes.

10. **Reload systemd** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
    - Defines `systemctl daemon-reload`.
    - Uses `execute[systemd_reload]`.
    - Has action `:nothing`.
    - Runs only when notified by a change to the FastAPI systemd unit.

11. **Enable and start the FastAPI service** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
    - Enables and starts the `fastapi-tutorial` service.
    - Uses `service[fastapi-tutorial]`.
    - Runs after deployment of the unit file and systemd daemon reload.
    - The service listens on `0.0.0.0:8000` and restarts automatically after termination.

**Resource summary**:

- `package`: 1 resource containing 7 packages
- `directory`: 1 resource
- `git`: 1 resource
- `execute`: 3 resources:
  - `create_venv`
  - `install_dependencies`
  - `create_db_user`
  - `systemd_reload` is also defined as an execute notification target
- `service`: 2 resources:
  - `postgresql`
  - `fastapi-tutorial`
- `file`: 2 resources:
  - `/opt/fastapi-tutorial/.env`
  - `/etc/systemd/system/fastapi-tutorial.service`
- No `.each` loops, included recipes, custom resources, providers, templates, static files, or attribute files are present.

## Dependencies

**External cookbook dependencies**: None listed in `metadata.rb`.

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**Chef version requirement**:

- Chef `>= 16.0`

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

- `/opt/fastapi-tutorial/requirements.txt`, installed into `/opt/fastapi-tutorial/venv`

## Credentials

**Detection Summary**: 2 credential references detected in `cookbooks/fastapi-tutorial/recipes/default.rb`.

The same PostgreSQL credential is defined in the database creation command and embedded in the application connection string.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None
- **Path**: None
- **Secret-management integration**: No Chef data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, or environment-variable secret lookups were detected.

### PostgreSQL password used to create the database role

- **Variable(s)**: No variable is used; literal password is `fastapi_password`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`, lines 40–42
- **Current storage**: Hardcoded plaintext in an `execute` command
- **Usage context**: Password for PostgreSQL role `fastapi`

### PostgreSQL connection string

- **Variable(s)**: `DATABASE_URL`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`, lines 48–53
- **Current storage**: Plaintext inside `/opt/fastapi-tutorial/.env`
- **Value**: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Usage context**: Application connection to the local PostgreSQL database `fastapi_db`

The Ansible implementation should store the password in Ansible Vault or an approved external secret provider. The generated `.env` file should be protected appropriately because preserving mode `0644` makes the database password readable by all local users.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/venv/bin/python`
- `/opt/fastapi-tutorial/venv/bin/pip`
- `/opt/fastapi-tutorial/venv/bin/uvicorn`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Database objects to verify**:

- PostgreSQL role: `fastapi`
- PostgreSQL database: `fastapi_db`
- Database owner: `fastapi`
- All privileges on `fastapi_db` granted to `fastapi`

**Service endpoints to check**:

- FastAPI: `0.0.0.0:8000`
- PostgreSQL: verify the active PostgreSQL port from the target host configuration
- Unix sockets: no socket path is explicitly configured

**Templates rendered**:

- None; 0 templates rendered

**Inline files created**:

- `/opt/fastapi-tutorial/.env`: 1 file resource
- `/etc/systemd/system/fastapi-tutorial.service`: 1 file resource

## Pre-flight checks

```bash
# Package checks
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev 2>/dev/null || \
rpm -q python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

# fastapi-tutorial instance checks
test -d /opt/fastapi-tutorial
test -f /opt/fastapi-tutorial/requirements.txt
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn
test -f /opt/fastapi-tutorial/.env
test -f /etc/systemd/system/fastapi-tutorial.service

systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl show fastapi-tutorial \
  --property=User,WorkingDirectory,ExecStart,Restart

ss -tlnp | grep ':8000'
curl -I http://127.0.0.1:8000/
curl -sS http://127.0.0.1:8000/

# postgresql instance checks
systemctl is-enabled postgresql
systemctl is-active postgresql
systemctl status postgresql

# Verify the PostgreSQL role
sudo -u postgres psql -tAc \
  "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"

# Verify database and owner
sudo -u postgres psql -tAc \
  "SELECT datname, pg_catalog.pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"

# Verify application database credentials
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_database(), current_user;"

# Verify the active PostgreSQL listener
ss -tlnp | grep postgres

# Verify environment file metadata without printing its secret value
stat -c '%U %G %a %n' /opt/fastapi-tutorial/.env
grep '^PROJECT_NAME=' /opt/fastapi-tutorial/.env
grep '^API_VERSION=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env

# Verify the systemd unit
systemctl cat fastapi-tutorial
grep '^Description=' /etc/systemd/system/fastapi-tutorial.service
grep '^After=' /etc/systemd/system/fastapi-tutorial.service
grep '^User=' /etc/systemd/system/fastapi-tutorial.service
grep '^WorkingDirectory=' /etc/systemd/system/fastapi-tutorial.service
grep '^Environment=' /etc/systemd/system/fastapi-tutorial.service
grep '^ExecStart=' /etc/systemd/system/fastapi-tutorial.service
grep '^Restart=' /etc/systemd/system/fastapi-tutorial.service

# Verify logs and restart policy
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u postgresql --no-pager -n 100
systemctl show fastapi-tutorial --property=Restart

# Verify systemd reload state after a unit change
systemctl daemon-reload
systemctl show fastapi-tutorial \
  --property=LoadState,ActiveState,UnitFileState
```

Expected values include:

```text
fastapi
fastapi_db|fastapi
PROJECT_NAME="FastAPI Tutorial"
API_VERSION=1.0.0
DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
ExecStart=/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
LoadState=loaded
ActiveState=active
UnitFileState=enabled
```

The FastAPI listener must be bound to `0.0.0.0:8000` or an equivalent IPv4 wildcard address. The cookbook does not define a specific health endpoint, so `/health` and `/api/status` must not be assumed.