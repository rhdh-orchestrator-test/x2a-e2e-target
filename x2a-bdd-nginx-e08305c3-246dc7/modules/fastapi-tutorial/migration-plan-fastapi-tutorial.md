---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` under `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, and PostgreSQL development packages; creates a Python virtual environment; installs application dependencies; creates the PostgreSQL role and database; writes an environment file; and runs the application as the root-owned `fastapi-tutorial` systemd service on port `8000`. The PostgreSQL password is currently hardcoded in the Chef recipe and generated `.env` file and must be migrated to Ansible Vault.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application server
  - Location/Path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Port/Socket: `0.0.0.0:8000`
  - Startup command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Systemd service: `fastapi-tutorial`
  - Systemd user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Restart behavior: `Restart=always`
  - Environment PATH: `/opt/fastapi-tutorial/venv/bin`
  - Key configuration: `PROJECT_NAME="FastAPI Tutorial"`, `API_VERSION=1.0.0`

- **postgresql**: Local PostgreSQL database service
  - Location/Path: Local PostgreSQL installation
  - Port/Socket: `localhost:5432`
  - Database user: `fastapi`
  - Database name: `fastapi_db`
  - Database owner: `fastapi`
  - Key configuration: All privileges on `fastapi_db` granted to `fastapi`; no explicit port is included in the connection string, so the standard local PostgreSQL port `5432` is expected.

## File Structure

Only the recipe file is executed or referenced by the provided execution tree. No provider, template, attribute, or static file is used by the cookbook.

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

**Attributes:**
```text
None
```

**Files:**
```text
None
```

The cookbook writes the following files at runtime through Chef `file` resources rather than cookbook files:

```text
/opt/fastapi-tutorial/.env
/etc/systemd/system/fastapi-tutorial.service
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev` using one `package` resource.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes the Git repository `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates the virtual environment with `execute[create_venv]` using `python3 -m venv /opt/fastapi-tutorial/venv`, guarded by `creates: /opt/fastapi-tutorial/venv`.
   - Installs dependencies from `/opt/fastapi-tutorial/requirements.txt` with `execute[install_dependencies]` using `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt` from working directory `/opt/fastapi-tutorial`.
   - Enables and starts the `postgresql` service.
   - Runs `execute[create_db_user]` as the PostgreSQL operating-system user `postgres` to create:
     - PostgreSQL role `fastapi`
     - Database `fastapi_db`
     - Owner `fastapi`
     - All privileges on `fastapi_db` for `fastapi`
   - The database creation commands use `|| true`, suppressing errors when objects already exist. The migrated implementation should use `community.postgresql.postgresql_user`, `community.postgresql.postgresql_db`, and, if required, `community.postgresql.postgresql_privs` for proper idempotency.
   - Writes `/opt/fastapi-tutorial/.env` with owner `root`, group `root`, and Chef mode `0644`. The migrated implementation should preferably use mode `0600`.
   - The generated `.env` content is:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Writes `/etc/systemd/system/fastapi-tutorial.service` with owner `root`, group `root`, and mode `0644`.
   - The generated systemd unit configures:
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
   - Defines `execute[systemd_reload]` to run `systemctl daemon-reload` with action `nothing` unless notified.
   - The source analysis confirms the reload resource and command. Immediate notification from the systemd unit file must be verified in the source recipe before being asserted as a direct notification relationship. Regardless of notification metadata, the migrated deployment must reload systemd after the unit file is changed and before starting the service.
   - Enables and starts the `fastapi-tutorial` service after the unit is deployed and systemd has been reloaded.
   - Iterations: No collection attributes or `.each` loops are present. The recipe configures exactly `fastapi-tutorial`, `postgresql`, and `fastapi_db`.

## Dependencies

**External cookbook dependencies**: None listed in the provided metadata.

**Supported platforms**:
- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

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
- `/opt/fastapi-tutorial/requirements.txt`, obtained from the Git repository and installed into `/opt/fastapi-tutorial/venv`

## Credentials

**Detection Summary**: 2 sensitive values detected in 2 locations: the PostgreSQL password and the PostgreSQL connection string containing that password.

**Source**:
  - **Provider**: Hardcoded in `cookbooks/fastapi-tutorial/recipes/default.rb`; no Vault, CyberArk, data bag, encrypted data bag, or external secret manager integration detected.
  - **URL**: None detected.
  - **Path**: None detected.

### PostgreSQL Password

- **Variable(s)**: No Chef attribute variable is used; the literal value is `fastapi_password`.
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the `execute[create_db_user]` command.
- **Usage context**: Used to create the PostgreSQL role `fastapi`.
- **Migration requirement**: Store the value in Ansible Vault, for example:
  ```yaml
  vault_fastapi_db_password: <encrypted-value>
  ```

### PostgreSQL Database Connection String

- **Variable(s)**: `DATABASE_URL`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the generated environment file.
- **Generated destination**: `/opt/fastapi-tutorial/.env`
- **Current value**: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Usage context**: Provides the FastAPI application with PostgreSQL connection details.
- **Migration requirement**: Construct the value from vaulted Ansible variables rather than storing the password in plaintext in playbooks or committed variable files.

No Chef data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable lookups, TLS certificates, private keys, API tokens, or additional credential namespaces were detected.

## Checks for the Migration

**Files to verify**:
- `cookbooks/fastapi-tutorial/recipes/default.rb`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- FastAPI application source under `/opt/fastapi-tutorial`, including the module used by `app.main:app`

**Directories to verify**:
- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/venv`

**Database objects to verify**:
- PostgreSQL role `fastapi`
- PostgreSQL database `fastapi_db`
- Owner of `fastapi_db`: `fastapi`
- Privileges granted to `fastapi`

**Service endpoints to check**:
- FastAPI application: `0.0.0.0:8000`
- PostgreSQL: `localhost:5432`

**Templates rendered**:
- None. The Chef recipe uses inline `file` content rather than `.erb` templates.
- `/opt/fastapi-tutorial/.env`: written once by the recipe.
- `/etc/systemd/system/fastapi-tutorial.service`: written once by the recipe.

## Pre-flight checks

### Package and directory checks

```bash
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev 2>/dev/null || \
rpm -q python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

ls -ld /opt/fastapi-tutorial
ls -ld /opt/fastapi-tutorial/venv
ls -l /opt/fastapi-tutorial/requirements.txt
```

Expected results:

- All seven required packages are installed.
- `/opt/fastapi-tutorial` exists with root ownership and mode `0755`.
- `/opt/fastapi-tutorial/venv` exists.
- `/opt/fastapi-tutorial/requirements.txt` exists.

### Repository and Python dependency checks

```bash
cd /opt/fastapi-tutorial
git remote -v
git rev-parse --abbrev-ref HEAD
git rev-parse HEAD

/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip --version
/opt/fastapi-tutorial/venv/bin/pip check
```

Verify that the repository remote is:

```text
https://github.com/dibanez/fastapi_tutorial.git
```

Verify that the checked-out revision corresponds to `main`.

### PostgreSQL instance checks

```bash
systemctl status postgresql --no-pager
systemctl is-enabled postgresql
systemctl is-active postgresql
ss -tlnp | grep ':5432'
```

Expected results:

- `postgresql` is enabled and active.
- PostgreSQL listens on local standard port `5432`, subject to the installed distribution's configuration.

### PostgreSQL role and database checks

```bash
sudo -u postgres psql -tAc "SELECT usename FROM pg_user WHERE usename = 'fastapi';"
sudo -u postgres psql -tAc "SELECT datname FROM pg_database WHERE datname = 'fastapi_db';"
sudo -u postgres psql -tAc "SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"
sudo -u postgres psql -tAc "SELECT has_database_privilege('fastapi', 'fastapi_db', 'CONNECT');"
```

Expected results:

- The role query returns `fastapi`.
- The database query returns `fastapi_db`.
- The owner query returns `fastapi`.
- The privilege query returns `t`.

Test the database connection as an existing operating-system account while authenticating as the PostgreSQL role `fastapi`. The recipe does not create a Linux/Unix user named `fastapi`.

```bash
PGPASSWORD='fastapi_password' \
psql -h localhost -U fastapi -d fastapi_db -c "SELECT current_database(), current_user;"
```

Expected results:

- `current_database` is `fastapi_db`.
- `current_user` is `fastapi`.

Do not place the password directly in shell history or routine CI logs in production.

### Environment file checks

```bash
stat -c '%A %U:%G %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' /opt/fastapi-tutorial/.env
```

Expected configuration:

```text
PROJECT_NAME="FastAPI Tutorial"
API_VERSION=1.0.0
DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
```

The migrated Ansible implementation should preferably set `/opt/fastapi-tutorial/.env` to mode `0600`.

### FastAPI instance checks

```bash
systemctl status fastapi-tutorial --no-pager
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
ps aux | grep '[u]vicorn'
ss -tlnp | grep ':8000'
curl -I http://127.0.0.1:8000/
```

Expected results:

- `fastapi-tutorial` is enabled and active.
- A Uvicorn process is running from `/opt/fastapi-tutorial/venv/bin/uvicorn`.
- Port `8000` is listening.
- The HTTP request receives an application response rather than a connection-refused error.

If the cloned application exposes a health endpoint, validate it only when present:

```bash
curl -i http://127.0.0.1:8000/health
```

### Systemd unit checks

```bash
systemctl daemon-reload
systemctl cat fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl show fastapi-tutorial --property=User,WorkingDirectory,ExecStart,Restart
```

Verify that the unit contains:

```text
User=root
WorkingDirectory=/opt/fastapi-tutorial
Environment="PATH=/opt/fastapi-tutorial/venv/bin"
ExecStart=/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
```

Confirm that systemd is reloaded after changes to `/etc/systemd/system/fastapi-tutorial.service` and before the service is started.

### Application and service logs

```bash
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u postgresql --no-pager -n 100
```

Check for:

- Uvicorn startup errors.
- Python import errors.
- Database authentication failures.
- PostgreSQL startup errors.
- Repeated service restart loops.

### Network checks

```bash
ss -tlnp | grep ':8000'
ss -tlnp | grep ':5432'
```

Expected results:

- FastAPI listens on port `8000`.
- PostgreSQL listens on local port `5432`.

### Credential and permissions checks

```bash
stat -c '%A %U:%G %n' /opt/fastapi-tutorial/.env

PGPASSWORD='fastapi_password' \
psql -h localhost -U fastapi -d fastapi_db -c "SELECT 1;"
```

Run the PostgreSQL connection test from an existing operating-system account; do not use `sudo -u fastapi`, because no Linux/Unix user named `fastapi` is created by this cookbook.