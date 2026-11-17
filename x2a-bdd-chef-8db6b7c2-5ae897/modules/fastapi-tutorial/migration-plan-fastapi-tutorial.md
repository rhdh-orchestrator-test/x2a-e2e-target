---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI Tutorial application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` to `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, and PostgreSQL development dependencies; creates a Python virtual environment; installs application requirements; initializes and starts PostgreSQL; creates the `fastapi` PostgreSQL role and `fastapi_db` database; writes an environment file containing the database connection string; and manages the `fastapi-tutorial` systemd service on port `8000`. The source contains one hardcoded PostgreSQL password that must be migrated to secure Ansible Vault or AAP credential storage.

## Service Type and Instances

**Service Type**: Application Server backed by PostgreSQL

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application service
  - Application path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Service unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Listening address: `0.0.0.0`
  - Port: `8000`
  - Startup command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Service user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Restart policy: `always`
  - Dependency: `postgresql.service`

- **postgresql**: PostgreSQL database service
  - Database user: `fastapi`
  - Database name: `fastapi_db`
  - Database owner: `fastapi`
  - Host: `localhost`
  - Port: PostgreSQL default port; no explicit port is configured
  - Database URL: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`

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

No ERB templates are used. Configuration files are created with inline Chef `file` resources.

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

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Selects a platform-specific package branch.
   - On Fedora/RHEL systems, installs `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, and `libpq-devel`.
   - On Fedora/RHEL systems, runs `postgresql-setup --initdb` when `/var/lib/pgsql/data/PG_VERSION` does not exist.
   - On non-Fedora/RHEL systems, installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Requires `/opt/fastapi-tutorial/requirements.txt` and the application module `app.main` for the configured Uvicorn command.
   - Creates `/opt/fastapi-tutorial/venv` with `python3 -m venv` when the virtual-environment directory does not exist.
   - Installs dependencies using `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt` with `/opt/fastapi-tutorial` as the working directory. The source command runs on every Chef convergence.
   - Enables and starts the `postgresql` service.
   - Creates the PostgreSQL role `fastapi`, database `fastapi_db`, and database privileges using commands executed as the `postgres` user. The source commands use `|| true`, suppressing errors when objects already exist.
   - Creates `/opt/fastapi-tutorial/.env` with owner `root`, group `root`, and mode `0644`.
   - Writes the following environment values:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Creates `/etc/systemd/system/fastapi-tutorial.service` with owner `root`, group `root`, and mode `0644`.
   - Configures the systemd unit to run as `root`, use `/opt/fastapi-tutorial` as its working directory, set `PATH` to `/opt/fastapi-tutorial/venv/bin`, execute Uvicorn on `0.0.0.0:8000`, restart automatically, start after `network.target` and `postgresql.service`, and enable through `multi-user.target`.
   - Runs `systemctl daemon-reload` immediately when the systemd unit file changes.
   - Enables and starts the `fastapi-tutorial` service.

   **Attributes used:**
   - `node['fastapi_tutorial']['app_path']`: `/opt/fastapi-tutorial`
   - `node['fastapi_tutorial']['repository']`: `https://github.com/dibanez/fastapi_tutorial.git`
   - `node['fastapi_tutorial']['revision']`: `main`
   - `node['fastapi_tutorial']['service_port']`: `8000`

   **Iterations:** No `.each` loops or collection-valued attributes are defined. No collection instances require expansion.

## Dependencies

**External cookbook dependencies**: None are listed in the supplied metadata or execution tree.

**System package dependencies:**

- Fedora/RHEL:
  - `python3`
  - `python3-pip`
  - `git`
  - `postgresql-server`
  - `postgresql-contrib`
  - `libpq-devel`
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

**Application dependencies**:

- `/opt/fastapi-tutorial/requirements.txt`
- Python packages installed into `/opt/fastapi-tutorial/venv`

## Credentials

**Detection Summary**: 1 credential detected in 2 source references within `cookbooks/fastapi-tutorial/recipes/default.rb`.

**Source**:
  - **Provider**: Hardcoded in the Chef recipe
  - **URL**: None detected
  - **Path**: None detected
  - **Secret-management integration**: No Chef Vault, encrypted data bag, data bag, CyberArk, Conjur, or environment-variable secret lookup was detected.

### PostgreSQL password for the `fastapi` database user

- **Variable(s)**:
  - Source variable: none; the source uses the hardcoded literal `fastapi_password`
  - Target migration variable: `fastapi_db_password`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded plaintext in a PostgreSQL `execute` command and the inline `.env` file
- **Usage context**:
  - Creates the PostgreSQL role:
    ```sql
    CREATE USER fastapi WITH PASSWORD 'fastapi_password';
    ```
  - Configures the application connection:
    ```text
    DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
    ```
- **Migration requirement**:
  - Store `fastapi_db_password` in Ansible Vault or an AAP credential.
  - Use the secured variable in both the PostgreSQL role task and `.env` deployment task.
  - Do not place the plaintext password in role defaults, task files, Git, or generated logs.

No TLS certificates, private keys, API keys, tokens, or other credentials were detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- `/var/lib/pgsql/data/PG_VERSION` on Fedora/RHEL systems

**Service endpoints to check**:

- **fastapi-tutorial**: `http://127.0.0.1:8000`
- **fastapi-tutorial listening socket**: TCP `0.0.0.0:8000`
- **postgresql**: `localhost` on the PostgreSQL default port
- **fastapi_db**: Database `fastapi_db`, role `fastapi`

**Templates rendered**:

- None; 0 templates rendered.
- `/opt/fastapi-tutorial/.env` is created with an inline file resource.
- `/etc/systemd/system/fastapi-tutorial.service` is created with an inline file resource.

## Pre-flight checks:

```bash
# Verify the application service instance
systemctl status fastapi-tutorial.service
systemctl is-enabled fastapi-tutorial.service
systemctl show fastapi-tutorial.service \
  --property=ActiveState,SubState,ExecMainPID,Restart
test -d /opt/fastapi-tutorial
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn
test -f /opt/fastapi-tutorial/requirements.txt
test -f /opt/fastapi-tutorial/.env
ss -tlnp | grep ':8000'
curl -I http://127.0.0.1:8000
curl -sS http://127.0.0.1:8000
journalctl -u fastapi-tutorial.service --no-pager -n 100

# Verify the PostgreSQL service instance
systemctl status postgresql
systemctl is-enabled postgresql
sudo -u postgres psql -d postgres -c "SELECT version();"
sudo -u postgres psql -d postgres -c "SELECT 1;"
sudo -u postgres psql -d postgres -c \
  "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"
sudo -u postgres psql -d postgres -c \
  "SELECT datname, pg_catalog.pg_get_userbyid(datdba) AS owner
   FROM pg_database
   WHERE datname = 'fastapi_db';"
PGPASSWORD='<secure-fastapi-password>' \
psql -h localhost -U fastapi -d fastapi_db -c "SELECT 1;"
journalctl -u postgresql --no-pager -n 100

# Verify the FastAPI systemd unit
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
grep -E '^(Description|After|Type|User|WorkingDirectory|Environment|ExecStart|Restart|WantedBy)=' \
  /etc/systemd/system/fastapi-tutorial.service

# Verify application configuration
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' \
  /opt/fastapi-tutorial/.env

# Verify installed application dependencies
/opt/fastapi-tutorial/venv/bin/pip list

# Verify Fedora/RHEL PostgreSQL initialization
test -f /var/lib/pgsql/data/PG_VERSION
```

Expected results:

- `postgresql` is enabled and active.
- `fastapi-tutorial.service` is enabled and active.
- Uvicorn listens on `0.0.0.0:8000`.
- The FastAPI endpoint returns an HTTP response.
- PostgreSQL contains role `fastapi` and database `fastapi_db` owned by `fastapi`.
- The application user can connect to `fastapi_db`.
- On Fedora/RHEL systems, `/var/lib/pgsql/data/PG_VERSION` exists after initialization.
- The systemd unit contains:
  ```text
  WorkingDirectory=/opt/fastapi-tutorial
  Environment="PATH=/opt/fastapi-tutorial/venv/bin"
  ExecStart=/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
  Restart=always
  ```

Use secure environment injection for PostgreSQL password testing; do not place the literal password in shell history.