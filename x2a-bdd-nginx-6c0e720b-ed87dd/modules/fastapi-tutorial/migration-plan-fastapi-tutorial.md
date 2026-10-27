---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI application from the `main` branch of `https://github.com/dibanez/fastapi_tutorial.git` into `/opt/fastapi-tutorial`. It installs Python, PostgreSQL, Git, and development packages; creates a Python virtual environment; installs application dependencies; creates the PostgreSQL `fastapi` user and `fastapi_db` database; writes an environment file containing the database connection string; and manages a systemd service listening on port `8000`. The cookbook configures one FastAPI application instance and one PostgreSQL database instance.

## Service Type and Instances

**Service Type**: Application Server with PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application launched with Uvicorn
  - Location/Path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Port/Socket: `0.0.0.0:8000`
  - Application command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Runtime user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Restart policy: `Restart=always`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Environment file: `/opt/fastapi-tutorial/.env`
  - Key Config: `After=network.target postgresql.service`, virtual-environment `PATH`, `Type=simple`

- **postgresql**: PostgreSQL database service and FastAPI persistence backend
  - Location/Path: Local PostgreSQL installation
  - Port/Socket: Default PostgreSQL endpoint; no port or socket override configured
  - Database user: `fastapi`
  - Database: `fastapi_db`
  - Database owner: `fastapi`
  - Password: `fastapi_password`
  - Connection host: `localhost`
  - Connection URL: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
  - Key Config: `ALL PRIVILEGES` on `fastapi_db` granted to `fastapi`

There are no iterable collection attributes or `.each` loops in the supplied execution tree. No collection items require expansion.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

Recipes:

```text
recipes/default.rb
```

Providers:

```text
```

No custom resources or provider files are used.

Templates:

```text
```

No Chef templates are rendered. The `.env` and systemd unit are created with inline `file` resources.

Attributes:

```text
```

No attribute files are shown or used.

Files:

```text
```

No static files from `files/default/*` or `files/*` are deployed.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the following seven system packages: `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates the virtual environment with `python3 -m venv /opt/fastapi-tutorial/venv`, guarded by `creates: /opt/fastapi-tutorial/venv`.
   - Installs dependencies from `/opt/fastapi-tutorial/requirements.txt` using `/opt/fastapi-tutorial/venv/bin/pip`.
   - Enables and starts the `postgresql` service.
   - Executes PostgreSQL commands as the `postgres` operating-system user to create the `fastapi` role, create the `fastapi_db` database owned by `fastapi`, and grant `ALL PRIVILEGES` to `fastapi`. Each command uses `|| true`, suppressing errors.
   - Creates `/opt/fastapi-tutorial/.env` with owner `root`, group `root`, and mode `0644`, containing:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Creates `/etc/systemd/system/fastapi-tutorial.service` with owner `root`, group `root`, and mode `0644`. The unit runs Uvicorn as `root`, uses `/opt/fastapi-tutorial` as its working directory, binds to `0.0.0.0:8000`, uses `Restart=always`, and starts after `network.target` and `postgresql.service`.
   - Immediately notifies `execute[systemd_reload]` when the systemd unit changes.
   - Declares `execute[systemd_reload]` with action `:nothing`; it runs `systemctl daemon-reload` only after notification.
   - Enables and starts the `fastapi-tutorial` systemd service.
   - Iterations: None; no `.each` loops or collection resources are present.

## Dependencies

**External cookbook dependencies**: None declared in `metadata.rb`.

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

**Application dependency source**: `/opt/fastapi-tutorial/requirements.txt`, supplied by the synchronized Git repository and installed into the virtual environment.

The cookbook metadata supports Ubuntu `>= 18.04` and CentOS `>= 7.0`. The listed package names are Debian/Ubuntu-style and require platform-specific mapping on CentOS.

## Credentials

**Detection Summary**: 2 plaintext credential references detected in 1 recipe file. Both references represent the same PostgreSQL password.

**Source**:

- **Provider**: Hardcoded
- **URL**: None detected
- **Path**: None detected
- **Storage**: Inline recipe content and generated `.env` content

### PostgreSQL password used during database creation

- **Variable(s)**: `fastapi_password`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the `execute[create_db_user]` command
- **Usage context**: Creates the PostgreSQL role with `CREATE USER fastapi WITH PASSWORD 'fastapi_password';`
- **Migration handling**: Store the password in Ansible Vault or an approved external secret provider and pass it to `community.postgresql.postgresql_user`.

### PostgreSQL password embedded in `DATABASE_URL`

- **Variable(s)**: `DATABASE_URL`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the inline `.env` file content
- **Usage context**: Connects the FastAPI application to `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Migration handling**: Generate the `.env` file from a template using the same vaulted password. Use `no_log: true` for tasks handling the secret.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secret lookups, TLS certificates, private keys, API keys, or tokens were detected.

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
- Ownership of `fastapi_db` by `fastapi`
- `ALL PRIVILEGES` on `fastapi_db` granted to `fastapi`

**Service endpoints to check**:

- `fastapi-tutorial`: TCP `0.0.0.0:8000`
- `postgresql`: local PostgreSQL service using its default port and socket configuration

**Templates rendered**:

- None; 0 templates rendered. The cookbook uses inline `file` resources.

**Unix sockets**:

- No application Unix socket is configured.
- PostgreSQL socket path is not explicitly configured.

## Pre-flight checks:

```bash
# Verify required packages on Debian/Ubuntu
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

# Verify the FastAPI application directory
stat -c '%A %U:%G %n' /opt/fastapi-tutorial
git -C /opt/fastapi-tutorial remote -v
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
test -f /opt/fastapi-tutorial/requirements.txt

# Verify the FastAPI virtual environment and dependencies
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip list
/opt/fastapi-tutorial/venv/bin/pip check

# Verify the postgresql instance
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
sudo -u postgres psql -tAc "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"
sudo -u postgres psql -tAc "SELECT datname, pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"
sudo -u postgres psql -d postgres -c "\l+ fastapi_db"

# Verify PostgreSQL connectivity for the fastapi database user
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT version();"

# Verify the FastAPI environment file without exposing the password
stat -c '%A %U:%G %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION)=' /opt/fastapi-tutorial/.env
sed -E 's#(postgresql://[^:]+:)[^@]+@#\1******@#' \
  /opt/fastapi-tutorial/.env

# Verify the FastAPI systemd unit
systemctl cat fastapi-tutorial
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl daemon-reload
systemctl status fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl show fastapi-tutorial \
  --property=User,WorkingDirectory,ExecStart,Restart,Environment

# Confirm the FastAPI instance is listening on port 8000
ss -ltnp | grep ':8000'
curl -i http://127.0.0.1:8000/
curl -i http://localhost:8000/
ps aux | grep '[u]vicorn'

# Review service logs
journalctl -u postgresql --no-pager -n 100
journalctl -u fastapi-tutorial --no-pager -n 100

# Verify restart behavior for the FastAPI instance
sudo systemctl restart fastapi-tutorial
systemctl is-active fastapi-tutorial
curl -i http://127.0.0.1:8000/
```

Expected FastAPI service properties include `User=root`, `WorkingDirectory=/opt/fastapi-tutorial`, `Restart=always`, and a Uvicorn executable under `/opt/fastapi-tutorial/venv/bin/` bound to port `8000`. The migration is complete when the application directory, virtual environment, `.env` file, PostgreSQL role and database, systemd unit, enabled services, and port `8000` match the specified behavior.