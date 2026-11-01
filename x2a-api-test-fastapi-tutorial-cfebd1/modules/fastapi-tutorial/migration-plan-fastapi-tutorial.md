---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys a single FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main`. It installs Python, PostgreSQL, Git, and PostgreSQL development libraries; creates a Python virtual environment; installs application dependencies; creates the `fastapi` PostgreSQL user and `fastapi_db` database; writes an environment file; and manages a systemd service listening on TCP port `8000`.

## Service Type and Instances

**Service Type**: Application Server

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application server
  - Application path: `/opt/fastapi-tutorial`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Entrypoint: `app.main:app`
  - Service user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Listening address: `0.0.0.0`
  - Port/Socket: TCP `8000`
  - Service unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Restart policy: `Restart=always`

- **fastapi_db**: PostgreSQL application database
  - Owner: `fastapi`
  - Connection host: `localhost`
  - Port: PostgreSQL default TCP port `5432`
  - Connection URL: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`

- **fastapi**: PostgreSQL application database user
  - Database access: `fastapi_db`
  - Password: `fastapi_password`
  - Granted privileges: All privileges on `fastapi_db`

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**
```text
recipes/default.rb
```

**Providers:**
```text
None
```

**Templates:**
```text
None
```

The cookbook writes the `.env` and systemd unit contents using inline `file` resources rather than `.erb` templates.

**Attributes:**
```text
None
```

**Files:**
```text
None
```

No `cookbook_file` or `remote_file` resource is present.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the seven system packages `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev` using one `package` resource.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` into `/opt/fastapi-tutorial` at revision `main`.
   - Creates the Python virtual environment by running `python3 -m venv /opt/fastapi-tutorial/venv`.
   - Guards virtual-environment creation on `/opt/fastapi-tutorial/venv` not already existing.
   - Installs dependencies with `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt` from `/opt/fastapi-tutorial`.
   - Performs dependency installation unconditionally; it has no notification attached to the FastAPI service.
   - Enables and starts the `postgresql` service.
   - Attempts to create the PostgreSQL user `fastapi` with password `fastapi_password`.
   - Attempts to create the PostgreSQL database `fastapi_db` owned by `fastapi`.
   - Grants all privileges on `fastapi_db` to `fastapi`.
   - Uses `|| true` on the PostgreSQL commands, suppressing failures from duplicate or unsuccessful user, database, and grant operations.
   - Writes `/opt/fastapi-tutorial/.env` as `root:root` with mode `0644`, containing:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Writes `/etc/systemd/system/fastapi-tutorial.service` as `root:root` with mode `0644`.
   - Configures the `fastapi-tutorial.service` unit as a simple service running as `root` from `/opt/fastapi-tutorial`.
   - Sets `PATH=/opt/fastapi-tutorial/venv/bin`.
   - Starts `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`.
   - Configures `Restart=always`, `After=network.target postgresql.service`, and `WantedBy=multi-user.target`.
   - Immediately notifies `execute[systemd_reload]` when the systemd unit file changes.
   - Defines `execute[systemd_reload]` to run `systemctl daemon-reload`; its default action is `:nothing`.
   - Enables and starts the `fastapi-tutorial` service after the unit file is present and systemd has reloaded its unit definitions.
   - Resources used:
     - `package` resource: one resource containing seven packages
     - `directory[/opt/fastapi-tutorial]`
     - `git[/opt/fastapi-tutorial]`
     - `execute[create_venv]`
     - `execute[install_dependencies]`
     - `service[postgresql]`
     - `execute[create_db_user]`
     - `file[/opt/fastapi-tutorial/.env]`
     - `file[/etc/systemd/system/fastapi-tutorial.service]`
     - `execute[systemd_reload]`, action `:nothing`
     - `service[fastapi-tutorial]`
   - Iterations: None; no `.each` loops are present.
   - Includes: None; there are no `include_recipe` calls, custom resources, providers, templates, or static file deployments.

## Dependencies

**External cookbook dependencies**: None shown in the supplied metadata or execution tree.

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

The `fastapi-tutorial` systemd unit declares `After=network.target postgresql.service`.

## Credentials

**Detection Summary**: 1 credential detected in 1 recipe file. The same credential is written into the database-creation command and the application `.env` database URL.

**Source**:

- **Provider**: Hardcoded
- **URL**: None
- **Path**: None

### PostgreSQL password for the `fastapi` user

- **Variable(s)**: No named Chef attribute is used. The literal password is `fastapi_password`.
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the recipe and written to `/opt/fastapi-tutorial/.env`.
- **Usage context**:
  - PostgreSQL user creation:
    ```sql
    CREATE USER fastapi WITH PASSWORD 'fastapi_password';
    ```
  - Application database URL:
    ```text
    postgresql://fastapi:fastapi_password@localhost/fastapi_db
    ```

No Chef data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, HashiCorp Vault, AWS Secrets Manager, secret-related attributes, environment-variable secret lookups, TLS certificate references, API keys, or tokens were detected.

For the Ansible migration, store this password in Ansible Vault rather than embedding it directly in the playbook or committed `.env` content.

## Checks for the Migration

**Files to verify**:

- `cookbooks/fastapi-tutorial/recipes/default.rb`
- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Database objects to verify**:

- PostgreSQL role: `fastapi`
- PostgreSQL database: `fastapi_db`

**Service endpoints to check**:

- **fastapi-tutorial**: HTTP endpoint `0.0.0.0:8000`
- **fastapi_db**: PostgreSQL connection at `localhost:5432`

**Unix sockets**:

- No PostgreSQL Unix socket path is specified by the cookbook.
- PostgreSQL may expose its platform-default local socket.

**Templates rendered**:

- None; the cookbook uses inline `file` resources.
- `/opt/fastapi-tutorial/.env`: written once.
- `/etc/systemd/system/fastapi-tutorial.service`: written once.

## Pre-flight checks

### Package and application files

```bash
dpkg -s python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

test -d /opt/fastapi-tutorial
test -d /opt/fastapi-tutorial/venv
test -f /opt/fastapi-tutorial/requirements.txt
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn
```

### Repository verification for `fastapi-tutorial`

```bash
git -C /opt/fastapi-tutorial remote -v
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
git -C /opt/fastapi-tutorial log -1 --oneline
```

Expected repository:

```text
https://github.com/dibanez/fastapi_tutorial.git
```

Expected checked-out revision:

```text
main
```

### PostgreSQL service for `fastapi_db`

```bash
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
```

Expected results:

- PostgreSQL is enabled.
- PostgreSQL is active and running.

### PostgreSQL role `fastapi`

```bash
sudo -u postgres psql -tAc "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"
```

Expected result:

```text
fastapi
```

### PostgreSQL database `fastapi_db`

```bash
sudo -u postgres psql -tAc "SELECT datname FROM pg_database WHERE datname = 'fastapi_db';"
```

Expected result:

```text
fastapi_db
```

### Database connection for `fastapi_db`

```bash
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_database(), current_user;"
```

Expected results:

- Current database: `fastapi_db`
- Current user: `fastapi`

### Environment file for `fastapi-tutorial`

```bash
stat -c '%U:%G %a %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' /opt/fastapi-tutorial/.env
```

Expected configuration:

```text
PROJECT_NAME="FastAPI Tutorial"
API_VERSION=1.0.0
DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
```

The file is expected to be owned by `root:root` with mode `0644`. A safer migration may use mode `0600` instead.

### systemd unit for `fastapi-tutorial`

```bash
stat -c '%U:%G %a %n' /etc/systemd/system/fastapi-tutorial.service
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl cat fastapi-tutorial
```

Verify that the unit contains:

```text
User=root
WorkingDirectory=/opt/fastapi-tutorial
Environment="PATH=/opt/fastapi-tutorial/venv/bin"
ExecStart=/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
After=network.target postgresql.service
```

### FastAPI instance `fastapi-tutorial`

```bash
systemctl daemon-reload
systemctl status fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
```

Expected results:

- The `fastapi-tutorial` unit is enabled.
- The `fastapi-tutorial` unit is active.
- The Uvicorn process is running from `/opt/fastapi-tutorial/venv/bin/uvicorn`.

### FastAPI HTTP endpoint for `fastapi-tutorial`

```bash
curl -i http://127.0.0.1:8000/
```

The application should return an HTTP response. The exact status and response body depend on the repository implementation.

Verify the listening socket:

```bash
ss -ltnp | grep ':8000'
lsof -iTCP:8000 -sTCP:LISTEN
```

Expected result: a process associated with `fastapi-tutorial` or Uvicorn is listening on TCP port `8000`.

### FastAPI logs for `fastapi-tutorial`

```bash
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u fastapi-tutorial -f
```

Check for startup failures, import errors, missing Python dependencies, database connection failures, and permission errors.

### PostgreSQL endpoint for `fastapi_db`

```bash
ss -ltnp | grep ':5432'
lsof -iTCP:5432 -sTCP:LISTEN
```

Expected result: PostgreSQL is listening on local TCP port `5432`, unless the distribution configuration uses a different platform-specific setting.