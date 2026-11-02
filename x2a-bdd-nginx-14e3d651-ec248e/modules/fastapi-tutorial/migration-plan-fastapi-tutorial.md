---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI tutorial application from `https://github.com/dibanez/fastapi_tutorial.git` to `/opt/fastapi-tutorial`, creates a Python virtual environment, installs application dependencies, installs and starts PostgreSQL, creates the `fastapi` database user and `fastapi_db` database, writes the database connection configuration to `.env`, and manages the application with a systemd service named `fastapi-tutorial` listening on `0.0.0.0:8000`. The cookbook contains one recipe and configures one application instance.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application server running under Uvicorn
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Location/Path: `/opt/fastapi-tutorial`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Dependency file: `/opt/fastapi-tutorial/requirements.txt`
  - Application entry point: `app.main:app`
  - Process command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Port/Socket: `0.0.0.0:8000`
  - Runtime user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Service name: `fastapi-tutorial`
  - Restart behavior: `Restart=always`

- **postgresql**: Backing PostgreSQL database service
  - Service name: `postgresql`
  - Host: `localhost`
  - Port/Socket: `localhost:5432`, using the default PostgreSQL port
  - Database: `fastapi_db`
  - Database owner: `fastapi`
  - Database user: `fastapi`
  - Password: `fastapi_password`
  - Connection URL: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`

There are no collection attributes or `.each` iterations in the recipe.

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

No custom resources or provider files are used.

**Templates:**

```text
```

No `.erb` templates are used. Configuration is written with inline Chef `file` resources.

**Attributes:**

```text
```

No attribute files are used.

**Files:**

```text
```

No static files from `files/default/` or `files/` are deployed.

## Module Explanation

The cookbook performs operations in the following order. It has one entry recipe and no `include_recipe` calls.

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the operating-system packages `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Creates `/opt/fastapi-tutorial` with owner `root`, group `root`, mode `0755`, and recursive creation enabled.
   - Synchronizes the Git repository `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates the virtual environment with `python3 -m venv /opt/fastapi-tutorial/venv`, using `/opt/fastapi-tutorial/venv` as the idempotency marker.
   - Installs dependencies from `/opt/fastapi-tutorial/requirements.txt` using `/opt/fastapi-tutorial/venv/bin/pip`.
   - Enables and starts the `postgresql` service.
   - Creates the PostgreSQL user `fastapi` with password `fastapi_password`.
   - Creates the PostgreSQL database `fastapi_db` owned by `fastapi`.
   - Grants all privileges on `fastapi_db` to `fastapi`.
   - Performs database setup using the PostgreSQL administrative account, normally the operating-system `postgres` user.
   - Creates `/opt/fastapi-tutorial/.env` with owner `root`, group `root`, and mode `0644`, containing:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Creates `/etc/systemd/system/fastapi-tutorial.service` with owner `root`, group `root`, and mode `0644`.
   - Configures the systemd unit with:
     - Description: `FastAPI Tutorial Service`
     - Ordering after `network.target` and `postgresql.service`
     - `Type=simple`
     - `User=root`
     - `WorkingDirectory=/opt/fastapi-tutorial`
     - `Environment="PATH=/opt/fastapi-tutorial/venv/bin"`
     - `ExecStart=/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
     - `Restart=always`
     - `WantedBy=multi-user.target`
   - Notifies `execute[systemd_reload]` when `/etc/systemd/system/fastapi-tutorial.service` changes.
   - Reloads systemd with `systemctl daemon-reload` when the unit file changes.
   - Enables and starts the `fastapi-tutorial` service after the application dependencies, database service, database user, database, environment file, and systemd unit are ready.
   - Iterations: None. No `.each` loops are present.

## Dependencies

**External cookbook dependencies**: None listed in `metadata.rb`.

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

**Application source dependency**:

- Repository: `https://github.com/dibanez/fastapi_tutorial.git`
- Revision: `main`

## Credentials

**Detection Summary**: 1 logical database credential detected in `cookbooks/fastapi-tutorial/recipes/default.rb`. The same password is used in the PostgreSQL user-creation command and the generated database connection URL.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: No external secret-management URL detected
- **Path**: No data bag, vault path, or secret-manager path detected

### PostgreSQL `fastapi` User Password

- **Variable(s)**:
  - No Chef attribute variable is used.
  - Literal password: `fastapi_password`
  - Connection string: `DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded inline in the recipe and written to `/opt/fastapi-tutorial/.env`
- **Usage context**:
  - Sets the password for PostgreSQL user `fastapi`.
  - Authenticates the FastAPI application to database `fastapi_db`.
- **Ansible migration recommendation**:
  - Store the password in Ansible Vault.
  - Use the vaulted value in the PostgreSQL user task.
  - Render the same value into `DATABASE_URL`.
  - Apply `no_log: true` to tasks that could expose the password.

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, `conjur_variable`, CyberArk integration, environment-variable secret lookup, certificate, private key, API token, or external database connection credential was detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Database objects to verify**:

- PostgreSQL role: `fastapi`
- PostgreSQL database: `fastapi_db`
- Database owner: `fastapi`
- All privileges on `fastapi_db` granted to `fastapi`

**Service endpoints to check**:

- `fastapi-tutorial`: HTTP endpoint `0.0.0.0:8000`
- `postgresql`: `localhost:5432`

**Unix sockets**:

- No application Unix socket is configured.
- PostgreSQL may expose its platform-default local Unix socket, but the cookbook does not specify a socket path.

**Templates rendered**:

- No templates are rendered.
- `/opt/fastapi-tutorial/.env`: written once by the inline `file` resource.
- `/etc/systemd/system/fastapi-tutorial.service`: written once by the inline `file` resource.

## Pre-flight checks

Run these checks after applying the Ansible role.

### `fastapi-tutorial` instance

```bash
test -d /opt/fastapi-tutorial
stat -c '%U:%G %a %n' /opt/fastapi-tutorial

test -f /opt/fastapi-tutorial/requirements.txt
test -d /opt/fastapi-tutorial/venv
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn

stat -c '%U:%G %a %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' /opt/fastapi-tutorial/.env

stat -c '%U:%G %a %n' /etc/systemd/system/fastapi-tutorial.service
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl daemon-reload
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl status fastapi-tutorial --no-pager

ss -tlnp | grep ':8000'
curl -I http://127.0.0.1:8000/
ps aux | grep '[u]vicorn app.main:app'
```

Expected systemd properties include:

- `User=root`
- `WorkingDirectory=/opt/fastapi-tutorial`
- Uvicorn executable `/opt/fastapi-tutorial/venv/bin/uvicorn`
- Application `app.main:app`
- Bind address `0.0.0.0`
- Port `8000`
- `Restart=always`

If the checked-out application defines a health route, verify it with:

```bash
curl -i http://127.0.0.1:8000/health
```

The cookbook does not define a health-route path, so `/health` should only be tested when that route exists.

### `postgresql` instance

```bash
dpkg-query -W python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

systemctl is-enabled postgresql
systemctl is-active postgresql
systemctl status postgresql --no-pager
ss -tlnp | grep ':5432'
```

Verify the PostgreSQL role:

```bash
sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='fastapi';"
```

Expected result:

```text
1
```

Verify the database and owner:

```bash
sudo -u postgres psql -tAc "SELECT datname, pg_get_userbyid(datdba) FROM pg_database WHERE datname='fastapi_db';"
```

Expected result:

```text
fastapi_db | fastapi
```

Verify application credentials and database connectivity:

```bash
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_user, current_database();"
```

Expected values:

- `current_user` is `fastapi`.
- `current_database` is `fastapi_db`.

### Logs and failure diagnostics

```bash
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u postgresql --no-pager -n 100

journalctl -u fastapi-tutorial --no-pager | \
  grep -E 'ERROR|Traceback|Listening|Application startup'

systemctl show fastapi-tutorial --property=MainPID
lsof -iTCP:8000 -sTCP:LISTEN
```

Do not print the complete `.env` file in normal CI logs because it contains the database password. A successful migration should show `postgresql` and `fastapi-tutorial` enabled and active, database `fastapi_db` available to user `fastapi`, and Uvicorn listening on port `8000`.