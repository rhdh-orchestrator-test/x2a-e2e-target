---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` under `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, and required system packages; creates a Python virtual environment; installs application dependencies; provisions the PostgreSQL role `fastapi` and database `fastapi_db`; writes the application environment file; and manages the FastAPI application with the `fastapi-tutorial` systemd service on port `8000`.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application served by Uvicorn
  - Location/Path: `/opt/fastapi-tutorial`
  - Source repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Source revision: `main`
  - Python virtual environment: `/opt/fastapi-tutorial/venv`
  - Application entry point: `app.main:app`
  - Bind address: `0.0.0.0`
  - Port/Socket: TCP port `8000`
  - Runtime user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Process command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Restart policy: `Restart=always`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`

- **postgresql**: Local PostgreSQL database service for the FastAPI application
  - Service name: `postgresql`
  - Database user: `fastapi`
  - Database name: `fastapi_db`
  - Database owner: `fastapi`
  - Connection host: `localhost`
  - Port/Socket: PostgreSQL's configured local listener, normally TCP port `5432`; no port or socket is explicitly configured by the cookbook
  - Connection string: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`

No collection attributes or `.each` iterations are used. No instance expansion is required.

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

No Chef templates are rendered. The `.env` file and systemd unit are created directly by `file` resources.

**Attributes:**
```text
```

No attribute files are used.

**Files:**
```text
```

No static files are deployed by `cookbook_file` or `remote_file`.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the seven system packages `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev` using one `package` resource.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes the Git repository `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates the virtual environment with `python3 -m venv /opt/fastapi-tutorial/venv`, guarded by `creates: /opt/fastapi-tutorial/venv`.
   - Installs dependencies from `/opt/fastapi-tutorial/requirements.txt` using `/opt/fastapi-tutorial/venv/bin/pip`.
   - Enables and starts the `postgresql` service.
   - Executes PostgreSQL commands as the `postgres` operating-system user to create role `fastapi`, create database `fastapi_db` owned by `fastapi`, and grant all privileges on `fastapi_db` to `fastapi`.
   - Preserves the original shell behavior in which each database command ends with `|| true`; existing roles, databases, or grants do not fail the Chef run.
   - Creates `/opt/fastapi-tutorial/.env` with owner `root`, group `root`, and mode `0644`, containing:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Creates `/etc/systemd/system/fastapi-tutorial.service` with owner `root`, group `root`, and mode `0644`, containing:
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
   - Immediately notifies `execute[systemd_reload]` when `/etc/systemd/system/fastapi-tutorial.service` changes.
   - Runs `systemctl daemon-reload` through `execute[systemd_reload]`, whose normal action is `nothing`.
   - Enables and starts the `fastapi-tutorial` service after the systemd unit is deployed and systemd has been reloaded.
   - Ansible equivalents should use `package`, `file`, `git`, `command` or `shell`, `pip`, `service` or `systemd`, PostgreSQL modules, and `copy` or `template` as appropriate.
   - For PostgreSQL migration, prefer `community.postgresql.postgresql_user`, `community.postgresql.postgresql_db`, and `community.postgresql.postgresql_privs` with `become_user: postgres`.
   - For the systemd unit, use `ansible.builtin.systemd` with `daemon_reload: true` or a handler notified by the unit-file deployment.
   - Iterations: none; there are no `.each` loops.

## Dependencies

**External cookbook dependencies**: None declared in the analyzed metadata.

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

The `fastapi-tutorial` systemd unit declares `After=network.target postgresql.service`. The application connects to PostgreSQL through the local host at `localhost`.

## Credentials

**Detection Summary**: 1 database credential detected in 1 file. The password is hardcoded in both the PostgreSQL creation command and the generated `.env` file.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None
- **Path**: None
- **Source file**: `cookbooks/fastapi-tutorial/recipes/default.rb`

### PostgreSQL application password

- **Variable(s)**: No named Chef attribute is used; the literal password is `fastapi_password`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the recipe and embedded in `/opt/fastapi-tutorial/.env`
- **Usage context**:
  - Creates the PostgreSQL role `fastapi`
  - Authenticates the FastAPI application to database `fastapi_db`
  - Appears in the connection string `postgresql://fastapi:fastapi_password@localhost/fastapi_db`

For the Ansible migration, store the password in Ansible Vault or an AAP credential, use a protected variable such as `fastapi_db_password`, construct `DATABASE_URL` from that variable, and apply `no_log: true` to tasks that handle the secret. The migrated `.env` file should preferably use mode `0600` instead of the Chef-defined `0644`.

No Chef data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, external secret manager, TLS certificate references, API keys, or environment-variable-based secret lookups were detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Database objects to verify**:

- PostgreSQL role `fastapi`
- PostgreSQL database `fastapi_db`
- Owner of `fastapi_db`: `fastapi`
- All privileges on `fastapi_db` granted to `fastapi`

**Service endpoints to check**:

- `fastapi-tutorial`: HTTP endpoint `0.0.0.0:8000`
- `postgresql`: local PostgreSQL listener, normally `localhost:5432`; the cookbook does not explicitly configure a port
- PostgreSQL default Unix socket, if enabled by the distribution configuration; no socket path is explicitly defined

**Templates rendered**:

- None; render count: `0`
- `/opt/fastapi-tutorial/.env`: created directly by one Chef `file` resource
- `/etc/systemd/system/fastapi-tutorial.service`: created directly by one Chef `file` resource

## Pre-flight checks

### Service status: `postgresql`

```bash
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
```

Expected result: `postgresql` is enabled and active.

### Service status: `fastapi-tutorial`

```bash
systemctl status fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
```

Expected result: `fastapi-tutorial` is enabled and active.

### Application directory and virtual environment

```bash
ls -ld /opt/fastapi-tutorial
ls -ld /opt/fastapi-tutorial/venv
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn
```

Expected result:

- `/opt/fastapi-tutorial` exists with root ownership and mode `0755`.
- The virtual environment exists.
- Python, pip, and Uvicorn executables are available.

### Repository and requirements

```bash
git -C /opt/fastapi-tutorial remote -v
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
test -f /opt/fastapi-tutorial/requirements.txt
```

Expected result:

- The repository points to `https://github.com/dibanez/fastapi_tutorial.git`.
- The checked-out revision is `main`.
- `/opt/fastapi-tutorial/requirements.txt` exists.

### PostgreSQL role and database

```bash
sudo -u postgres psql -tAc "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"
sudo -u postgres psql -tAc "SELECT datname, pg_catalog.pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"
sudo -u postgres psql -d fastapi_db -c "SELECT current_database(), current_user;"
sudo -u postgres psql -d fastapi_db -c "\l+ fastapi_db"
```

Expected result:

- Role `fastapi` exists.
- Database `fastapi_db` exists.
- Database owner is `fastapi`.
- A connection to `fastapi_db` succeeds.

### Application environment file

```bash
stat -c '%U:%G %a %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' /opt/fastapi-tutorial/.env
```

Expected configuration:

```text
PROJECT_NAME="FastAPI Tutorial"
API_VERSION=1.0.0
DATABASE_URL=postgresql://fastapi:...@localhost/fastapi_db
```

Do not print the unmasked password in operational logs or CI output.

### Systemd unit validation

```bash
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl cat fastapi-tutorial
systemctl show fastapi-tutorial -p User -p WorkingDirectory -p ExecStart -p Restart
```

Expected configuration:

- User: `root`
- Working directory: `/opt/fastapi-tutorial`
- Executable: `/opt/fastapi-tutorial/venv/bin/uvicorn`
- Application: `app.main:app`
- Bind address: `0.0.0.0`
- Port: `8000`
- Restart policy: `always`

### PostgreSQL listener

```bash
sudo -u postgres psql -tAc "SHOW port;"
sudo -u postgres psql -tAc "SHOW listen_addresses;"
```

Verify the configured listener rather than assuming a port, because the cookbook does not set a PostgreSQL port.

### FastAPI HTTP endpoint

The cookbook does not define a dedicated health endpoint. Validate the root endpoint:

```bash
curl -i http://127.0.0.1:8000/
curl -sS -o /dev/null -w 'HTTP status: %{http_code}\n' http://127.0.0.1:8000/
```

Expected result: the connection succeeds and the application returns an HTTP response. The exact status code depends on the repository's routes.

### Port verification for `fastapi-tutorial`

```bash
ss -tlnp | grep ':8000'
lsof -iTCP:8000 -sTCP:LISTEN
```

Expected result: a Uvicorn or Python process listens on TCP port `8000`, bound to `0.0.0.0` or an equivalent wildcard address.

### Application and PostgreSQL logs

```bash
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u postgresql --no-pager -n 100
```

Check for:

- Successful Uvicorn startup
- Successful import of `app.main:app`
- PostgreSQL connection errors
- Missing Python package errors
- Repeated service restarts

### Systemd reload behavior

After changing the unit file:

```bash
sudo systemctl daemon-reload
sudo systemctl restart fastapi-tutorial
systemctl is-active fastapi-tutorial
```

Expected result:

- Systemd accepts the unit.
- `fastapi-tutorial` returns to the `active` state.
- The application remains reachable on port `8000`.