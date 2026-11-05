---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main`. It installs Python, Git, PostgreSQL, and PostgreSQL development packages; creates a Python virtual environment; installs application dependencies; provisions the PostgreSQL `fastapi` user and `fastapi_db` database; writes an environment file containing the database connection string; and manages a systemd service listening on port `8000`. The cookbook configures one application instance: **fastapi-tutorial**.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application server
  - Application path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Requirements file: `/opt/fastapi-tutorial/requirements.txt`
  - Application command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app`
  - Bind address: `0.0.0.0`
  - Port: `8000`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Run user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Restart policy: `Restart=always`
  - Dependency ordering: after `network.target` and `postgresql.service`

**PostgreSQL resources configured for the application**:

- Service: `postgresql`
- Database user: `fastapi`
- Database name: `fastapi_db`
- Database owner: `fastapi`
- Database privilege: `ALL PRIVILEGES` on `fastapi_db`
- Database host: `localhost`

There are no collection attributes or `.each` loops in the analyzed recipe. No repeated instance items require expansion.

## File Structure

Only one recipe file is used by the execution tree.

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

No Chef templates are rendered. Configuration files are written with inline `file` resources.

**Attributes:**
```text
```

No attribute files are used by the analyzed execution tree.

**Files:**
```text
```

No static files are deployed with `cookbook_file` or `remote_file`.

## Module Explanation

The cookbook performs operations in the following order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the system packages `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Supports Ubuntu `>= 18.04` and CentOS `>= 7.0`. Package names may require platform-specific mapping on CentOS; `python3-venv` and `libpq-dev` are Debian-family names.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `/opt/fastapi-tutorial` from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main`.
   - Creates `/opt/fastapi-tutorial/venv` with `python3 -m venv /opt/fastapi-tutorial/venv` only when the virtual environment does not already exist.
   - Installs dependencies using `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt` with `/opt/fastapi-tutorial` as the working directory.
   - Enables and starts the `postgresql` service.
   - Executes PostgreSQL initialization as the operating-system `postgres` user:
     - Creates the `fastapi` role with password `fastapi_password`.
     - Creates the `fastapi_db` database owned by `fastapi`.
     - Grants `ALL PRIVILEGES` on `fastapi_db` to `fastapi`.
   - The Chef database command appends `|| true` to each SQL operation, so existing users, databases, or privileges do not fail the overall command. The Ansible migration should use idempotent `community.postgresql` modules instead.
   - Writes `/opt/fastapi-tutorial/.env` with owner `root`, group `root`, and current mode `0644`:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Deploys `/etc/systemd/system/fastapi-tutorial.service` with owner `root`, group `root`, and mode `0644`:
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
   - Notifies `execute[systemd_reload]` when the systemd unit changes.
   - Runs `systemctl daemon-reload` through `execute[systemd_reload]`; this resource has action `nothing` and runs only when notified.
   - Enables and starts the `fastapi-tutorial` systemd service after the repository, virtual environment, dependencies, PostgreSQL resources, `.env` file, unit file, and systemd reload are complete.
   - The Chef recipe does not explicitly restart the application when `.env` changes. A secure Ansible migration should preserve the daemon reload behavior for unit changes and may notify an application restart when environment configuration changes.

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

**Source code dependency**:

- Repository: `https://github.com/dibanez/fastapi_tutorial.git`
- Revision: `main`

**Ansible collection dependency for the preferred database implementation**:

- `community.postgresql`

**Service dependencies**:

- `postgresql`
- `fastapi-tutorial`

**Runtime dependency relationship**:

- `fastapi-tutorial.service` declares `After=postgresql.service`.
- The FastAPI application uses PostgreSQL through `/opt/fastapi-tutorial/.env`.
- PostgreSQL must be running before the `fastapi` role and `fastapi_db` database are created.
- The application service must start after its repository, virtual environment, Python dependencies, database resources, environment file, and systemd unit are available.

## Credentials

**Detection Summary**: 1 credential detected across 1 file.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None
- **Path**: None
- **Current storage**: Inline plaintext and embedded in a database connection string

### PostgreSQL application password

- **Variable(s)**:
  - No Chef attribute variable is used.
  - Inline password literal: `fastapi_password`
  - Database URL: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**:
  - Hardcoded in the `execute[create_db_user]` command
  - Repeated in the inline `/opt/fastapi-tutorial/.env` file content
- **Usage context**:
  - Authenticates PostgreSQL user `fastapi`
  - Provides the FastAPI application connection to database `fastapi_db`
- **Migration recommendation**:
  - Store the value in Ansible Vault or an approved external secret-management system.
  - Reference it through a protected variable such as `fastapi_db_password`.
  - Do not place the plaintext password in role defaults or task files.
  - Deploy the environment file with mode `0600` unless broader read access is explicitly required.
  - Avoid exposing the password in command-line arguments where possible.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secret lookups, TLS certificate references, API keys, or tokens were detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial/`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv/`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Database objects to verify**:

- PostgreSQL service: `postgresql`
- PostgreSQL role: `fastapi`
- PostgreSQL database: `fastapi_db`
- Database owner: `fastapi`
- Database privileges: `ALL`

**Service endpoints to check**:

- **fastapi-tutorial**: `0.0.0.0:8000`
- PostgreSQL application connection: `localhost`
- PostgreSQL Unix socket: distribution default may be present, but the application explicitly uses host `localhost`

**Templates rendered**:

- No Chef templates are rendered.
- `/opt/fastapi-tutorial/.env`: rendered once by an inline `file` resource
- `/etc/systemd/system/fastapi-tutorial.service`: rendered once by an inline `file` resource

## Pre-flight checks

Run these checks after the Ansible role completes.

### fastapi-tutorial instance

Verify installed packages on Debian-family systems:

```bash
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev
```

On CentOS or another RPM-based system, verify the platform-mapped packages:

```bash
rpm -q python3 git postgresql postgresql-contrib
```

Verify the application layout:

```bash
ls -ld /opt/fastapi-tutorial
ls -l /opt/fastapi-tutorial/requirements.txt
ls -ld /opt/fastapi-tutorial/venv
```

Verify the repository and revision:

```bash
git -C /opt/fastapi-tutorial remote -v
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
git -C /opt/fastapi-tutorial log -1 --oneline
```

The repository branch should be `main`.

Verify the Python environment and dependencies:

```bash
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip list
/opt/fastapi-tutorial/venv/bin/uvicorn --version
```

Validate the application import without starting a second server:

```bash
cd /opt/fastapi-tutorial
/opt/fastapi-tutorial/venv/bin/python -c "from app.main import app; print(app)"
```

### PostgreSQL service and database

```bash
systemctl status postgresql --no-pager
systemctl is-enabled postgresql
systemctl is-active postgresql
sudo -u postgres psql -c "SELECT version();"
```

Verify the application role:

```bash
sudo -u postgres psql -tAc "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"
```

Expected result:

```text
fastapi
```

Verify the application database:

```bash
sudo -u postgres psql -tAc "SELECT datname FROM pg_database WHERE datname = 'fastapi_db';"
```

Expected result:

```text
fastapi_db
```

Verify database ownership:

```bash
sudo -u postgres psql -tAc "SELECT datname, pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"
```

Expected owner:

```text
fastapi
```

Test application authentication. Supply the protected password without exposing it in shared logs:

```bash
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_user, current_database();"
```

Expected values:

```text
current_user     | fastapi
current_database | fastapi_db
```

### Environment configuration

Verify ownership and permissions:

```bash
ls -l /opt/fastapi-tutorial/.env
```

Verify non-secret settings:

```bash
grep -E '^(PROJECT_NAME|API_VERSION)=' /opt/fastapi-tutorial/.env
```

Verify the database URL structure without printing the password:

```bash
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env | \
  sed -E 's#://[^:]+:[^@]+@#://REDACTED:REDACTED@#'
```

The redacted value should identify:

```text
localhost/fastapi_db
```

### fastapi-tutorial systemd service

```bash
systemctl daemon-reload
systemctl status fastapi-tutorial --no-pager
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl cat fastapi-tutorial
```

Check the key service properties:

```bash
systemctl show fastapi-tutorial \
  --property=User,WorkingDirectory,ExecStart,Restart,After
```

Expected values include:

- `User=root`
- `WorkingDirectory=/opt/fastapi-tutorial`
- `Restart=always`
- `ExecStart` referencing `/opt/fastapi-tutorial/venv/bin/uvicorn`
- `After` including `postgresql.service`
- Port `8000`
- Application target `app.main:app`

Verify the running process and listener:

```bash
ps aux | grep '[u]vicorn'
ss -tlnp | grep ':8000'
```

The service should be listening on port `8000` on the configured bind address.

### FastAPI HTTP endpoints

```bash
curl -i http://127.0.0.1:8000/
```

The response should be an HTTP response from the FastAPI application. The exact status code depends on the repository route definitions.

```bash
curl -i http://127.0.0.1:8000/openapi.json
```

The endpoint should return an HTTP success response and JSON if the standard FastAPI OpenAPI route is enabled.

```bash
curl -i http://127.0.0.1:8000/docs
```

The endpoint should return an HTTP response if the FastAPI documentation route is enabled.

### Logs

```bash
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u postgresql --no-pager -n 100
```

Follow the application journal during troubleshooting:

```bash
journalctl -u fastapi-tutorial -f
```

Search for common deployment failures:

```bash
journalctl -u fastapi-tutorial --no-pager -n 100 | \
  grep -E 'ERROR|Traceback|Exception|failed|database|5432|8000'
```

### Systemd reload behavior

Modify or redeploy:

```text
/etc/systemd/system/fastapi-tutorial.service
```

Verify that the Ansible handler performs:

```bash
systemctl daemon-reload
```

After the reload, verify that the instance remains operational:

```bash
systemctl is-active fastapi-tutorial
curl -i http://127.0.0.1:8000/
```

The Ansible implementation should preserve the Chef behavior that a systemd unit change triggers a daemon reload before the `fastapi-tutorial` service is enabled and started.