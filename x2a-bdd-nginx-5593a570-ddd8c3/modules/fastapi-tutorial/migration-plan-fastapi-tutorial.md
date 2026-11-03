---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI Tutorial application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` under `/opt/fastapi-tutorial`. It installs Python, virtual-environment, Git, PostgreSQL, PostgreSQL development packages, and application dependencies; creates a Python virtual environment; provisions the `fastapi_db` PostgreSQL database and `fastapi` user; writes an application environment file; and manages the `fastapi-tutorial` systemd service listening on `0.0.0.0:8000`. The PostgreSQL password is hardcoded in the Chef recipe and must be migrated to Ansible Vault, an AAP credential, or another secret-management system.

## Service Type and Instances

**Service Type**: Application Server

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application served by Uvicorn
  - Location/Path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Port/Socket: `0.0.0.0:8000`
  - Application command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Working directory: `/opt/fastapi-tutorial`
  - Service user: `root`
  - Restart policy: `Restart=always`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Key config: `Environment="PATH=/opt/fastapi-tutorial/venv/bin"`

- **postgresql**: Local PostgreSQL database service
  - Location/Path: Platform-managed PostgreSQL data directory
  - Port/Socket: `localhost:5432`; no explicit port or socket is configured
  - Service actions: enabled and started
  - Database: `fastapi_db`
  - Database user: `fastapi`
  - Database owner: `fastapi`
  - Key config: Database password is currently `fastapi_password`

## File Structure

Only the following executable cookbook file is present in the supplied execution tree.

```text
Recipes:
recipes/default.rb

Providers:
None

Templates:
None

Attributes:
None

Files:
None
```

The cookbook creates `/opt/fastapi-tutorial/.env` and `/etc/systemd/system/fastapi-tutorial.service` dynamically with Chef `file` resources. They are not static files in the cookbook `files/` directory.

## Module Explanation

The cookbook performs operations in this order. It has one recipe and no `include_recipe` calls.

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the following packages with `package`: `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Creates `/opt/fastapi-tutorial` as a recursive `0755` directory owned by `root:root`.
   - Synchronizes the Git repository `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates the Python virtual environment with `python3 -m venv /opt/fastapi-tutorial/venv`, guarded by the existence of `/opt/fastapi-tutorial/venv`.
   - Installs dependencies from `/opt/fastapi-tutorial/requirements.txt` using `/opt/fastapi-tutorial/venv/bin/pip`.
   - Enables and starts the `postgresql` service.
   - Executes PostgreSQL commands as the `postgres` operating-system user to create the `fastapi` user, create the `fastapi_db` database owned by `fastapi`, and grant all privileges on `fastapi_db` to `fastapi`.
   - The original PostgreSQL commands use `|| true`, which suppresses both already-exists errors and unrelated database errors. The Ansible migration should use `community.postgresql.postgresql_user`, `community.postgresql.postgresql_db`, and `community.postgresql.postgresql_privs` where required.
   - Creates `/opt/fastapi-tutorial/.env` with owner `root`, group `root`, and mode `0644`.
   - Writes the following environment values:
     - `PROJECT_NAME="FastAPI Tutorial"`
     - `API_VERSION=1.0.0`
     - `DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db`
   - The Ansible version must source the database password from Ansible Vault, an AAP credential, or another secret-management integration rather than storing it in the task or template.
   - Creates `/etc/systemd/system/fastapi-tutorial.service` with owner `root`, group `root`, and mode `0644`.
   - Configures the systemd unit to:
     - Start after `network.target` and `postgresql.service`
     - Run as `root`
     - Use `/opt/fastapi-tutorial` as its working directory
     - Set `/opt/fastapi-tutorial/venv/bin` as the first `PATH` entry
     - Execute `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
     - Use `Restart=always`
     - Enable through `multi-user.target`
   - Notifies `execute[systemd_reload]` immediately when the systemd unit file changes.
   - Runs `systemctl daemon-reload` through `execute[systemd_reload]`, whose action is otherwise `nothing`.
   - Enables and starts the `fastapi-tutorial` service after its unit file is created and systemd has reloaded its unit definitions.
   - No `.each` loops are present.

## Dependencies

**External cookbook dependencies**: None declared in `metadata.rb`.

**System package dependencies**: `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, `libpq-dev`.

**Source-code dependency**: Git repository `https://github.com/dibanez/fastapi_tutorial.git`, revision `main`.

**Service dependencies**:
- `postgresql` must be enabled and started before provisioning `fastapi_db` and `fastapi`.
- `fastapi-tutorial.service` declares `After=network.target postgresql.service`.

On Ubuntu, the listed package names apply directly. On CentOS 7 or later, platform-specific mappings may be required, particularly for `libpq-dev`, which corresponds to a PostgreSQL development package such as `postgresql-devel`.

## Credentials

**Detection Summary**: 2 credential references detected across 1 file.

**Source**:
  - **Provider**: Hardcoded in the Chef recipe
  - **URL**: None
  - **Path**: `cookbooks/fastapi-tutorial/recipes/default.rb`; credentials are embedded in the PostgreSQL command and database connection string

### PostgreSQL database password

- **Variable(s)**: Literal password `fastapi_password`; `DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`, including the PostgreSQL provisioning command and environment-file content
- **Current storage**: Hardcoded in the Chef recipe and written in plain text to `/opt/fastapi-tutorial/.env` with mode `0644`
- **Usage context**: Creates the PostgreSQL user `fastapi` and authenticates the FastAPI application to the `fastapi_db` database

### PostgreSQL database connection string

- **Variable(s)**: `DATABASE_URL`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Plain-text `/opt/fastapi-tutorial/.env`
- **Usage context**: Provides application database connectivity to `localhost/fastapi_db`
- **Sensitive value**: Contains the username `fastapi` and password `fastapi_password`

No Chef data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable lookups, TLS certificates, API keys, or tokens were detected.

The Ansible migration should use `fastapi_database_password: "{{ vault_fastapi_database_password }}"` or an equivalent protected credential and should prefer mode `0600` for `.env` unless broader access is required by the application.

## Checks for the Migration

**Files to verify**:
- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Database objects to verify**:
- PostgreSQL service `postgresql`
- PostgreSQL user `fastapi`
- PostgreSQL database `fastapi_db`
- Database owner `fastapi`

**Service endpoints to check**:
- `fastapi-tutorial`: `0.0.0.0:8000`
- `postgresql`: `localhost:5432`

**Unix sockets**: No socket path is explicitly configured. PostgreSQL may expose the platform-default local Unix socket.

**Templates rendered**:
- None. The cookbook has no static templates.
- `/opt/fastapi-tutorial/.env`: created once by an inline Chef `file` resource
- `/etc/systemd/system/fastapi-tutorial.service`: created once by an inline Chef `file` resource

## Pre-flight checks

### Package and application checks

```bash
dpkg-query -W python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev
```

On RPM-based systems:

```bash
rpm -q python3 python3-pip python3-venv git postgresql postgresql-server postgresql-devel
```

Verify the FastAPI Tutorial instance:

```bash
stat -c '%A %U:%G %n' /opt/fastapi-tutorial
test -f /opt/fastapi-tutorial/requirements.txt
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn

git -C /opt/fastapi-tutorial remote -v
git -C /opt/fastapi-tutorial branch --show-current
git -C /opt/fastapi-tutorial rev-parse --verify HEAD
```

The repository remote must be `https://github.com/dibanez/fastapi_tutorial.git`, and the intended revision is `main`.

### PostgreSQL instance checks

```bash
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
ss -ltnp | grep ':5432'
```

Verify the PostgreSQL user:

```bash
sudo -u postgres psql -tAc \
  "SELECT usename FROM pg_catalog.pg_user WHERE usename = 'fastapi';"
```

Expected output:

```text
fastapi
```

Verify the database:

```bash
sudo -u postgres psql -tAc \
  "SELECT datname FROM pg_database WHERE datname = 'fastapi_db';"
```

Expected output:

```text
fastapi_db
```

Verify database ownership:

```bash
sudo -u postgres psql -tAc \
  "SELECT pg_catalog.pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"
```

Expected output:

```text
fastapi
```

Test authentication without exposing the password in command output:

```bash
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_database(), current_user;"
```

Expected values:

```text
current_database | fastapi_db
current_user     | fastapi
```

### Environment and configuration checks

```bash
stat -c '%A %U:%G %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION)=' /opt/fastapi-tutorial/.env
grep -E '^DATABASE_URL=' /opt/fastapi-tutorial/.env \
  | sed -E 's#(postgresql://[^:]+:)[^@]+@#\1****@#'
```

Expected redacted database URL:

```text
DATABASE_URL=postgresql://fastapi:****@localhost/fastapi_db
```

Verify the application module and installed dependencies:

```bash
cd /opt/fastapi-tutorial
/opt/fastapi-tutorial/venv/bin/pip list
/opt/fastapi-tutorial/venv/bin/python -c "import app.main; print(app.main.app)"
```

### FastAPI Tutorial service checks

```bash
systemctl cat fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl status fastapi-tutorial
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
```

Confirm the configured execution details:

```bash
systemctl show fastapi-tutorial \
  --property=User,WorkingDirectory,ExecStart,Restart,ActiveState,SubState
```

Expected values include:

- `User=root`
- `WorkingDirectory=/opt/fastapi-tutorial`
- Uvicorn executable under `/opt/fastapi-tutorial/venv/bin/`
- `Restart=always`
- `ActiveState=active`
- `SubState=running`

Verify the FastAPI Tutorial endpoint and process:

```bash
ss -ltnp | grep ':8000'
curl -i http://127.0.0.1:8000/
curl -i http://127.0.0.1:8000/health
ps -ef | grep '[u]vicorn app.main:app'
journalctl -u fastapi-tutorial --no-pager -n 100
```

The root request must return an HTTP response from the FastAPI application. The `/health` request should be tested when that endpoint is present in the checked-out repository.