---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` under `/opt/fastapi-tutorial`, installs Python, Git, and PostgreSQL dependencies, creates a Python virtual environment, installs application requirements, initializes and starts PostgreSQL, creates the `fastapi` role and `fastapi_db` database, writes the application environment file, and manages the `fastapi-tutorial` systemd service. The FastAPI application listens on `0.0.0.0:8000`. The cookbook supports RHEL/Fedora and Debian-family package layouts.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application served by Uvicorn
  - Location/Path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Service user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Start command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Port/Socket: `0.0.0.0:8000`
  - Restart policy: `always`
  - Database: `fastapi_db`
  - Database user: `fastapi`

- **postgresql**: PostgreSQL database service used by `fastapi-tutorial`
  - Service name: `postgresql`
  - Port/Socket: TCP port `5432` unless platform configuration changes it; local Unix socket is platform-dependent
  - Database: `fastapi_db`
  - Database role: `fastapi`
  - Database owner: `fastapi`

**Attributes**:

- `node['fastapi_tutorial']['app_path']`: `/opt/fastapi-tutorial`
- `node['fastapi_tutorial']['repository']`: `https://github.com/dibanez/fastapi_tutorial.git`
- `node['fastapi_tutorial']['revision']`: `main`
- `node['fastapi_tutorial']['service_port']`: `8000`

## File Structure

The following files are used by the cookbook.

```text
cookbooks/fastapi-tutorial/
├── attributes/
│   └── default.rb
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

No custom Chef resource providers are used.

**Templates:**

```text
```

No ERB templates are rendered. Configuration content is embedded directly in `file` resources.

**Attributes:**

```text
cookbooks/fastapi-tutorial/attributes/default.rb
```

**Files:**

```text
```

No static files are deployed by `cookbook_file` or `remote_file`.

## Module Explanation

The cookbook performs operations in the following order:

1. **Platform-dependent package installation** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Detects whether the platform family is RHEL/Fedora.
   - On RHEL/Fedora, installs `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, and `libpq-devel`.
   - On non-RHEL/Fedora systems, installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - On RHEL/Fedora, runs `postgresql-setup --initdb` through `execute[initialize_postgresql]` only when `/var/lib/pgsql/data/PG_VERSION` does not exist.
   - No `.each` loops or collection iterations are present.

2. **Create the application directory** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/opt/fastapi-tutorial`.
   - Sets owner and group to `root`.
   - Sets mode to `0755`.
   - Enables recursive creation.

3. **Synchronize the application repository** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` into `/opt/fastapi-tutorial`.
   - Checks out revision `main`.

4. **Create the Python virtual environment** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Runs `python3 -m venv /opt/fastapi-tutorial/venv`.
   - Creates the environment only when `/opt/fastapi-tutorial/venv` does not already exist.

5. **Install Python dependencies** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Runs `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt`.
   - Uses `/opt/fastapi-tutorial` as the working directory.
   - Runs after repository synchronization and virtual-environment creation.

6. **Enable and start PostgreSQL** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Enables the `postgresql` service.
   - Starts the `postgresql` service.

7. **Create the PostgreSQL role and database** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Executes PostgreSQL commands as the `postgres` system user.
   - Creates the `fastapi` role with password `fastapi_password`.
   - Creates the `fastapi_db` database owned by `fastapi`.
   - Grants `ALL` privileges on `fastapi_db` to `fastapi`.
   - The original commands use `|| true` so existing objects do not fail the run.
   - The migration should use idempotent `community.postgresql.postgresql_user`, `community.postgresql.postgresql_db`, and `community.postgresql.postgresql_privs` tasks.
   - Runs after `postgresql` has started.

8. **Create the application environment file** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/opt/fastapi-tutorial/.env`.
   - Sets owner and group to `root`.
   - The Chef mode is `0644`; `0600` is recommended for the migration because the file contains a database password.
   - Writes:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```

9. **Create the systemd unit** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/etc/systemd/system/fastapi-tutorial.service`.
   - Sets owner and group to `root`.
   - Sets mode to `0644`.
   - Configures a `simple` service running as `root`.
   - Sets the working directory to `/opt/fastapi-tutorial`.
   - Sets `PATH` to `/opt/fastapi-tutorial/venv/bin`.
   - Starts Uvicorn on `0.0.0.0:8000`.
   - Uses `Restart=always`.
   - Starts after `network.target` and `postgresql.service`.
   - Enables installation under `multi-user.target`.

10. **Reload systemd** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
    - Defines `execute[systemd_reload]` with command `systemctl daemon-reload`.
    - The resource has action `nothing`.
    - Runs immediately when `/etc/systemd/system/fastapi-tutorial.service` changes.
    - The migration should notify a `Reload systemd` handler with `daemon_reload: true`.

11. **Enable and start the FastAPI service** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
    - Enables the `fastapi-tutorial` systemd service.
    - Starts the `fastapi-tutorial` systemd service.
    - Starts after the unit file has been installed and systemd has been reloaded.

## Dependencies

**External cookbook dependencies**: None identified in `metadata.rb`.

**System package dependencies**:

- **RHEL/Fedora**:
  - `python3`
  - `python3-pip`
  - `git`
  - `postgresql-server`
  - `postgresql-contrib`
  - `libpq-devel`
- **Non-RHEL/Fedora**:
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

The `fastapi-tutorial` systemd unit starts after `postgresql.service`.

## Credentials

**Detection Summary**: 1 hardcoded database credential detected in 1 recipe file, with two usages: PostgreSQL role creation and the application `DATABASE_URL`.

**Source**:

- **Provider**: Hardcoded in Chef recipe
- **URL**: None
- **Path**: None

### PostgreSQL Database Password

- **Variable(s)**:
  - Literal password: `fastapi_password`
  - `DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the recipe
- **Usage context**:
  - Used by `CREATE USER fastapi WITH PASSWORD 'fastapi_password'`
  - Embedded in `/opt/fastapi-tutorial/.env`
- **Migration guidance**:
  - Store the password in Ansible Vault or an AAP credential-backed variable.
  - Do not commit the literal password to the playbook or template.
  - Use the same vaulted variable when creating the PostgreSQL role and rendering `DATABASE_URL`.

No Chef data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, AWS Secrets Manager, environment-variable secret lookups, TLS certificate references, or API keys were detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- `/var/lib/pgsql/data/PG_VERSION` on RHEL/Fedora

**Database objects to verify**:

- PostgreSQL role `fastapi`
- PostgreSQL database `fastapi_db`
- Owner of `fastapi_db`: `fastapi`
- `ALL` privileges on `fastapi_db` for `fastapi`

**Service endpoints to check**:

- `fastapi-tutorial`: TCP `0.0.0.0:8000`
- `postgresql`: TCP port `5432`, unless platform configuration changes it
- PostgreSQL local Unix socket

**Templates rendered**:

- None; render count: `0`
- The `.env` file and systemd unit are generated using inline Chef `file` resources.

## Pre-flight checks

```bash
# Verify platform and package tools
cat /etc/os-release
python3 --version
pip3 --version
git --version
```

```bash
# RHEL/Fedora package and initialization checks
rpm -q python3 python3-pip git postgresql-server postgresql-contrib libpq-devel
test -f /var/lib/pgsql/data/PG_VERSION
```

```bash
# Debian-family package checks
dpkg-query -W python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev
```

### fastapi-tutorial instance

```bash
# Verify application directory and permissions
stat /opt/fastapi-tutorial
stat -c '%A %U:%G' /opt/fastapi-tutorial

# Verify repository and revision
git -C /opt/fastapi-tutorial remote -v
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
git -C /opt/fastapi-tutorial rev-parse HEAD

# Verify application requirements
test -f /opt/fastapi-tutorial/requirements.txt

# Verify virtual environment
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip --version
/opt/fastapi-tutorial/venv/bin/pip freeze
```

```bash
# Verify the application environment file without exposing the password
test -f /opt/fastapi-tutorial/.env
stat -c '%A %U:%G %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION)=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env \
  | sed -E 's#(postgresql://[^:]+:)[^@]+#\1REDACTED#'
```

```bash
# Verify the systemd unit
test -f /etc/systemd/system/fastapi-tutorial.service
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
grep -E '^(Description|After|Type|User|WorkingDirectory|Environment|ExecStart|Restart|WantedBy)=' \
  /etc/systemd/system/fastapi-tutorial.service

systemctl daemon-reload
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl status fastapi-tutorial --no-pager
```

```bash
# Verify the FastAPI process and endpoint
ps aux | grep '[u]vicorn app.main:app'
ss -tlnp | grep ':8000'
curl -I http://127.0.0.1:8000/
curl -sS http://127.0.0.1:8000/
```

### postgresql instance

```bash
# Verify PostgreSQL service state
systemctl is-enabled postgresql
systemctl is-active postgresql
systemctl status postgresql --no-pager

# Verify PostgreSQL accepts local administrative connections
sudo -u postgres psql -c "SELECT version();"

# Verify the PostgreSQL listener
ss -tlnp | grep ':5432' || true
```

### fastapi_db database and fastapi role

```bash
# Verify the application role
sudo -u postgres psql -tAc \
  "SELECT rolname FROM pg_roles WHERE rolname='fastapi';"

# Verify the application database
sudo -u postgres psql -tAc \
  "SELECT datname FROM pg_database WHERE datname='fastapi_db';"

# Verify database ownership
sudo -u postgres psql -tAc \
  "SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname='fastapi_db';"

# Verify privileges
sudo -u postgres psql -tAc \
  "SELECT has_database_privilege('fastapi', 'fastapi_db', ' CONNECT');"
```

```bash
# Verify application-user connectivity.
# Supply the password through the migrated secret mechanism rather than shell history.
PGPASSWORD="$FASTAPI_DB_PASSWORD" \
psql -h localhost -U fastapi -d fastapi_db -c "SELECT current_database();"

PGPASSWORD="$FASTAPI_DB_PASSWORD" \
psql -h localhost -U fastapi -d fastapi_db -c "SELECT 1;"
```

### Service logs and restart behavior

```bash
# FastAPI service logs
journalctl -u fastapi-tutorial --no-pager -n 100
systemctl is-active fastapi-tutorial

# PostgreSQL service logs
journalctl -u postgresql --no-pager -n 100
```

### Resource and path checks

```bash
ls -lah /opt/fastapi-tutorial
ls -lah /opt/fastapi-tutorial/venv/bin
test -x /opt/fastapi-tutorial/venv/bin/uvicorn
test -x /opt/fastapi-tutorial/venv/bin/uvicorn
```