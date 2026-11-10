---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: The `fastapi-tutorial` cookbook deploys one FastAPI application from the `main` branch of `https://github.com/dibanez/fastapi_tutorial.git` at `/opt/fastapi-tutorial`. It installs platform-specific Python, Git, PostgreSQL, and PostgreSQL development packages; initializes PostgreSQL on Fedora/RHEL; creates a Python virtual environment; installs application dependencies; enables and starts PostgreSQL; creates the `fastapi` PostgreSQL role and `fastapi_db` database; writes the application environment file; and manages a systemd service listening on `0.0.0.0:8000`.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application server
  - Application path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Python virtual environment: `/opt/fastapi-tutorial/venv`
  - Application command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app`
  - Application entry point: `app.main:app`
  - Bind address: `0.0.0.0`
  - Port: `8000`
  - Working directory: `/opt/fastapi-tutorial`
  - Service user: `root`
  - Restart policy: `always`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`

- **postgresql**: PostgreSQL database service
  - Service action: enabled and started
  - Database role: `fastapi`
  - Database: `fastapi_db`
  - Database owner: `fastapi`
  - Database connection host: `localhost`
  - Default port: `5432`

There are no Chef attribute collections or `.each` loops. The cookbook configures one FastAPI application instance and one PostgreSQL system service.

## File Structure

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

No ERB templates are used. Configuration files are created directly with Chef `file` resources.

**Attributes:**
```text
```

No attribute files are used.

**Files:**
```text
```

No static files are deployed with `cookbook_file` or `remote_file`.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Evaluates `platform_family?('fedora', 'rhel')`.
   - On Fedora/RHEL, declares a package resource for:
     - `python3`
     - `python3-pip`
     - `git`
     - `postgresql-server`
     - `postgresql-contrib`
     - `libpq-devel`
   - On other supported platforms, including Ubuntu, declares a separate package resource for:
     - `python3`
     - `python3-pip`
     - `python3-venv`
     - `git`
     - `postgresql`
     - `postgresql-contrib`
     - `libpq-dev`
   - Only one of the two branch-specific package resources executes, depending on the platform.
   - On Fedora/RHEL, runs `execute[initialize_postgresql]` with `postgresql-setup --initdb`, guarded by `/var/lib/pgsql/data/PG_VERSION`.
   - Creates `directory[/opt/fastapi-tutorial]` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `git[/opt/fastapi-tutorial]` from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main`.
   - Runs `execute[create_venv]` with `python3 -m venv /opt/fastapi-tutorial/venv`, guarded by `/opt/fastapi-tutorial/venv`.
   - Runs `execute[install_dependencies]` with `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt` from `/opt/fastapi-tutorial`.
   - Enables and starts `service[postgresql]`.
   - Runs `execute[create_db_user]` as the PostgreSQL operating-system user to create the `fastapi` role, assign its password, create `fastapi_db` owned by `fastapi`, and grant the role all privileges on the database. The original commands use `|| true`, suppressing errors on repeated or failed operations.
   - Creates `file[/opt/fastapi-tutorial/.env]` with owner `root`, group `root`, and mode `0644`, containing:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Creates `file[/etc/systemd/system/fastapi-tutorial.service]` with owner `root`, group `root`, and mode `0644`.
   - The systemd unit:
     - Describes `FastAPI Tutorial Service`.
     - Starts after `network.target` and `postgresql.service`.
     - Uses `Type=simple`.
     - Runs as `root`.
     - Uses `/opt/fastapi-tutorial` as its working directory.
     - Sets `PATH=/opt/fastapi-tutorial/venv/bin`.
     - Executes `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`.
     - Uses `Restart=always`.
     - Is enabled through `multi-user.target`.
   - Immediately notifies `execute[systemd_reload]`.
   - Runs `execute[systemd_reload]` with `systemctl daemon-reload`; the resource has action `nothing` and runs only when notified.
   - Enables and starts `service[fastapi-tutorial]`.
   - Iterations: None. No `.each` loops or collection-based instance definitions are present.

## Dependencies

**External cookbook dependencies**: None declared in the supplied metadata or execution tree.

**System package dependencies**:

- Fedora/RHEL package resource:
  - `python3`
  - `python3-pip`
  - `git`
  - `postgresql-server`
  - `postgresql-contrib`
  - `libpq-devel`
- Other supported platform package resource:
  - `python3`
  - `python3-pip`
  - `python3-venv`
  - `git`
  - `postgresql`
  - `postgresql-contrib`
  - `libpq-dev`

**Application dependency source**: `/opt/fastapi-tutorial/requirements.txt`, installed into `/opt/fastapi-tutorial/venv`.

**Service dependencies**:

- `postgresql`
- `fastapi-tutorial`

**Execution dependencies**:

1. Install system packages.
2. Initialize PostgreSQL on Fedora/RHEL.
3. Create `/opt/fastapi-tutorial`.
4. Synchronize the Git repository.
5. Create the Python virtual environment.
6. Install Python dependencies.
7. Enable and start PostgreSQL.
8. Create the PostgreSQL role and database.
9. Write `/opt/fastapi-tutorial/.env`.
10. Write `/etc/systemd/system/fastapi-tutorial.service`.
11. Reload systemd.
12. Enable and start `fastapi-tutorial`.

## Credentials

**Detection Summary**: 1 credential detected across 1 recipe file. The same credential is used for PostgreSQL provisioning and the application connection string.

**Source**:
  - **Provider**: Hardcoded
  - **URL**: None
  - **Path**: None

### PostgreSQL Password

- **Variable(s)**: No separate Chef variable; literal value `fastapi_password`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the recipe and written in plaintext into `/opt/fastapi-tutorial/.env`
- **Usage context**:
  - PostgreSQL role creation:
    ```sql
    CREATE USER fastapi WITH PASSWORD 'fastapi_password';
    ```
  - Application database URL:
    ```text
    postgresql://fastapi:fastapi_password@localhost/fastapi_db
    ```

The Ansible migration should replace the literal with an Ansible Vault variable or another approved secret backend. No Chef data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secret lookups, TLS certificates, API keys, or tokens were detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- `/var/lib/pgsql/data/PG_VERSION` on Fedora/RHEL

**Database objects to verify**:

- PostgreSQL role `fastapi`
- PostgreSQL database `fastapi_db`
- Database owner `fastapi`
- All required privileges for `fastapi` on `fastapi_db`

**Service endpoints to check**:

- FastAPI instance `fastapi-tutorial`: `http://localhost:8000/`
- FastAPI TCP port: `8000`
- PostgreSQL instance `postgresql`: `localhost:5432`

**Templates rendered**: None. No templates are present or rendered. Both configuration files are created directly by Chef `file` resources.

**Systemd notifications**:

- Changes to `/etc/systemd/system/fastapi-tutorial.service` immediately trigger `systemctl daemon-reload`.
- The original cookbook does not explicitly restart `fastapi-tutorial` after a unit-file change. The Ansible migration should consider notifying a service restart after the unit file changes.

## Pre-flight checks:

```bash
# Verify the postgresql instance individually
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
ss -tlnp | grep ':5432'
sudo -u postgres psql -tAc "SELECT version();"

# Verify the fastapi-tutorial instance individually
systemctl status fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl cat fastapi-tutorial
pgrep -af '/opt/fastapi-tutorial/venv/bin/uvicorn'
ss -tlnp | grep ':8000'
curl -i http://localhost:8000/
journalctl -u fastapi-tutorial --no-pager -n 100

# Verify the application directory and repository
ls -ld /opt/fastapi-tutorial
git -C /opt/fastapi-tutorial status --short
git -C /opt/fastapi-tutorial branch --show-current
test -f /opt/fastapi-tutorial/requirements.txt

# Verify the Python virtual environment
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn

# Verify the application environment file
stat -c '%U:%G %a %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' /opt/fastapi-tutorial/.env

# Verify the systemd unit and configuration
grep -E '^(Description|After|Type|User|WorkingDirectory|Environment|ExecStart|Restart|WantedBy)=' \
  /etc/systemd/system/fastapi-tutorial.service
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl daemon-reload

# Verify the PostgreSQL role
sudo -u postgres psql -tAc \
  "SELECT 1 FROM pg_roles WHERE rolname = 'fastapi';"
# Expected output: 1

# Verify the PostgreSQL database and owner
sudo -u postgres psql -tAc \
  "SELECT datname || ':' || pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"
# Expected output: fastapi_db:fastapi

# Verify database connectivity with the application role
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_database(), current_user;"
# Expected database: fastapi_db
# Expected user: fastapi

# Verify database privileges
sudo -u postgres psql -tAc \
  "SELECT has_database_privilege('fastapi', 'fastapi_db', 'CONNECT');"
# Expected output: t

sudo -u postgres psql -d fastapi_db -c \
  "SELECT grantee, privilege_type FROM information_schema.role_table_grants WHERE grantee = 'fastapi';"

# Verify Fedora/RHEL PostgreSQL initialization marker
test -f /var/lib/pgsql/data/PG_VERSION

# Review PostgreSQL logs
journalctl -u postgresql --no-pager -n 100
```