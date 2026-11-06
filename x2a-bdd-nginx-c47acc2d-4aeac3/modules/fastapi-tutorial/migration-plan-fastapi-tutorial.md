---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the `main` branch of `https://github.com/dibanez/fastapi_tutorial.git` to `/opt/fastapi-tutorial`. It installs Python, PostgreSQL, Git, and build dependencies; creates a Python virtual environment; installs application requirements; creates the PostgreSQL role and database; writes the application environment file; and manages the FastAPI application with a systemd service listening on `0.0.0.0:8000`.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application served by Uvicorn
  - Location/Path: `/opt/fastapi-tutorial`
  - Source repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Repository revision: `main`
  - Python virtual environment: `/opt/fastapi-tutorial/venv`
  - Application entry point: `app.main:app`
  - Application server: Uvicorn
  - Bind address: `0.0.0.0`
  - Port: `8000`
  - Working directory: `/opt/fastapi-tutorial`
  - Service user: `root`
  - Restart policy: `Restart=always`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`

- **PostgreSQL**: Database service for the FastAPI application
  - Service name: `postgresql`
  - Database user: `fastapi`
  - Database password: `fastapi_password`
  - Database name: `fastapi_db`
  - Database owner: `fastapi`
  - Connection host: `localhost`
  - Connection URL: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
  - Explicit port override: None configured

No iterable collection attributes or `.each` loops are present.

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

**Templates:**
```text
```

**Attributes:**
```text
```

**Files:**
```text
```

The cookbook uses inline Chef content for `/opt/fastapi-tutorial/.env` and `/etc/systemd/system/fastapi-tutorial.service`. No cookbook templates or static files are deployed.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the system packages `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Uses one `package` resource containing seven packages.
   - Package versions are not pinned; platform repository versions are installed.
   - The cookbook supports Ubuntu `>= 18.04` and CentOS `>= 7.0`; PostgreSQL package names may require platform-specific mapping.

2. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/opt/fastapi-tutorial` recursively.
   - Sets owner and group to `root` and mode to `0755`.
   - Uses one `directory` resource.

3. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Uses one `git` resource with sync behavior.
   - The repository must be available before dependency installation because `/opt/fastapi-tutorial/requirements.txt` is required.

4. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/opt/fastapi-tutorial/venv` using:
     ```bash
     python3 -m venv /opt/fastapi-tutorial/venv
     ```
   - Uses `execute[create_venv]`.
   - The command is guarded by `/opt/fastapi-tutorial/venv` and is skipped when the directory exists.

5. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs Python dependencies from `/opt/fastapi-tutorial/requirements.txt` into `/opt/fastapi-tutorial/venv`.
   - Uses `execute[install_dependencies]` with working directory `/opt/fastapi-tutorial`.
   - The equivalent Ansible implementation should use `ansible.builtin.pip` with the requirements file and virtual environment.

6. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Enables and starts the `postgresql` service.
   - Uses one `service[postgresql]` resource with actions `enable` and `start`.
   - PostgreSQL must be running before database initialization.

7. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Runs `execute[create_db_user]` as the operating-system `postgres` user through:
     ```bash
     sudo -u postgres psql -c "CREATE USER fastapi WITH PASSWORD 'fastapi_password';" || true
     sudo -u postgres psql -c "CREATE DATABASE fastapi_db OWNER fastapi;" || true
     sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE fastapi_db TO fastapi;" || true
     ```
   - Creates the PostgreSQL role `fastapi`.
   - Sets the role password to `fastapi_password`.
   - Creates `fastapi_db` with `fastapi` as owner.
   - Grants all privileges on `fastapi_db` to `fastapi`.
   - Runs unconditionally and suppresses SQL errors with `|| true`.
   - The migration should use `community.postgresql.postgresql_user`, `community.postgresql.postgresql_db`, and, if required, `community.postgresql.postgresql_privs` for idempotent state management.
   - Database administration should run with `become: true` and `become_user: postgres`.

8. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/opt/fastapi-tutorial/.env` using one `file` resource.
   - Writes:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Sets owner and group to `root` and mode to `0644`.
   - The migration should store the password in Ansible Vault or an approved secret manager and should preferably use mode `0600` if supported by the application.

9. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/etc/systemd/system/fastapi-tutorial.service` using one `file` resource.
   - Deploys:
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
   - Sets owner and group to `root` and mode to `0644`.
   - Immediately notifies `execute[systemd_reload]` when the unit file changes.
   - The migration should manage this unit with `ansible.builtin.copy` or `ansible.builtin.template` and notify a systemd daemon-reload handler.

10. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
    - Defines `execute[systemd_reload]` with command:
      ```bash
      systemctl daemon-reload
      ```
    - Uses action `:nothing`.
    - Runs immediately only when `/etc/systemd/system/fastapi-tutorial.service` changes.

11. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
    - Enables and starts the `fastapi-tutorial` service.
    - Uses one `service[fastapi-tutorial]` resource with actions `enable` and `start`.
    - The service starts after the repository, virtual environment, Python dependencies, PostgreSQL service, database role, database, `.env` file, and systemd unit are ready.
    - The systemd daemon must be reloaded after unit creation or modification.

There are no `.each` loops to expand.

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

**Application dependencies**:

- Repository: `https://github.com/dibanez/fastapi_tutorial.git`
- Revision: `main`
- Requirements file: `/opt/fastapi-tutorial/requirements.txt`

**Service dependencies**:

- `postgresql`
- `fastapi-tutorial`

**Network endpoints**:

- FastAPI/Uvicorn: TCP `0.0.0.0:8000`
- PostgreSQL: `localhost`; no explicit port override is configured

## Credentials

**Detection Summary**: 1 credential detected in 1 source file.

**Source**:
  - **Provider**: Hardcoded in Chef source
  - **URL**: None
  - **Path**: `cookbooks/fastapi-tutorial/recipes/default.rb`

### PostgreSQL Database Password

- **Variable**: `fastapi_password`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded plaintext
- **Usage context**:
  - Sets the password for the PostgreSQL role `fastapi`.
  - Authenticates the application to the `fastapi_db` database.
  - Appears in the `DATABASE_URL` value in `/opt/fastapi-tutorial/.env`.
- **Occurrences**:
  ```bash
  CREATE USER fastapi WITH PASSWORD 'fastapi_password';
  ```
  ```text
  DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
  ```
- **Migration handling**:
  - Store the password in Ansible Vault or another approved secret-management system.
  - Use the vaulted value with `community.postgresql.postgresql_user`.
  - Construct `DATABASE_URL` from the vaulted value.
  - Avoid exposing the password in command-line arguments or task output.
  - Prefer mode `0600` for `.env` unless broader access is required.

No data bags, encrypted data bags, Chef Vault items, CyberArk integration, Conjur variables, environment-variable secret lookups, TLS certificate references, API keys, or tokens were detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/fastapi-tutorial/recipes/default.rb`
- `/opt/fastapi-tutorial/`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv/`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- PostgreSQL role `fastapi`
- PostgreSQL database `fastapi_db`

**Service endpoints to check**:

- FastAPI/Uvicorn: `0.0.0.0:8000`
- PostgreSQL: `localhost`, with no cookbook-defined explicit port

**Templates rendered**:

- None; inline Chef `file` resources create both configuration files.
- Template render count: `0`.

**Systemd reload behavior**:

- `systemd_reload` is notification-only.
- It runs immediately when `/etc/systemd/system/fastapi-tutorial.service` changes.

## Pre-flight checks:

```bash
# Verify packages and PostgreSQL tools
python3 --version
python3 -m pip --version
git --version
psql --version
pg_config --version
```

```bash
# Verify the fastapi-tutorial instance directory and repository
ls -ld /opt/fastapi-tutorial
git -C /opt/fastapi-tutorial status
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
test -f /opt/fastapi-tutorial/requirements.txt
```

Expected branch:

```text
main
```

```bash
# Verify the fastapi-tutorial Python environment
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip list
```

```bash
# Verify the PostgreSQL instance
systemctl status postgresql --no-pager
systemctl is-enabled postgresql
systemctl is-active postgresql
sudo -u postgres psql -tAc "SELECT version();"
```

```bash
# Verify the PostgreSQL fastapi role
sudo -u postgres psql -tAc \
  "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"
```

Expected result:

```text
fastapi
```

```bash
# Verify the PostgreSQL fastapi_db database and owner
sudo -u postgres psql -tAc \
  "SELECT datname FROM pg_database WHERE datname = 'fastapi_db';"
sudo -u postgres psql -tAc \
  "SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"
```

Expected results:

```text
fastapi_db
fastapi
```

```bash
# Verify PostgreSQL connectivity for the fastapi application
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT 1;"
```

The result should include `1`. Do not expose the password in production validation output.

```bash
# Verify the fastapi-tutorial environment file without exposing secrets
test -f /opt/fastapi-tutorial/.env
grep '^PROJECT_NAME=' /opt/fastapi-tutorial/.env
grep '^API_VERSION=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env
stat -c '%U:%G %a %n' /opt/fastapi-tutorial/.env
```

Expected configuration keys:

```text
PROJECT_NAME="FastAPI Tutorial"
API_VERSION=1.0.0
DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
```

Use redacted output when displaying the database URL.

```bash
# Verify the fastapi-tutorial systemd unit
systemctl cat fastapi-tutorial
grep '^Description=' /etc/systemd/system/fastapi-tutorial.service
grep '^After=' /etc/systemd/system/fastapi-tutorial.service
grep '^User=' /etc/systemd/system/fastapi-tutorial.service
grep '^WorkingDirectory=' /etc/systemd/system/fastapi-tutorial.service
grep '^ExecStart=' /etc/systemd/system/fastapi-tutorial.service
grep '^Restart=' /etc/systemd/system/fastapi-tutorial.service
```

Expected values:

```text
Description=FastAPI Tutorial Service
After=network.target postgresql.service
User=root
WorkingDirectory=/opt/fastapi-tutorial
ExecStart=/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
```

```bash
# Verify the fastapi-tutorial service state
systemctl daemon-reload
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl status fastapi-tutorial --no-pager
```

Expected service state:

```text
enabled
active
```

```bash
# Verify the fastapi-tutorial process and endpoint
pgrep -af 'uvicorn app.main:app'
curl -i http://127.0.0.1:8000/
```

The endpoint should connect to the FastAPI application without a connection-refused error. The exact HTTP status for `/` depends on the repository.

```bash
# Verify the fastapi-tutorial listening port
ss -tlnp | grep ':8000'
```

Expected result: Uvicorn listens on TCP port `8000`.

```bash
# Verify logs for both named service instances
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u postgresql --no-pager -n 100
```

Check for:

- Successful Uvicorn startup.
- No `app.main:app` import errors.
- No missing dependency errors.
- No database authentication failures.
- No PostgreSQL startup failures.

```bash
# Verify fastapi-tutorial restart behavior
sudo systemctl restart fastapi-tutorial
systemctl is-active fastapi-tutorial
curl -i http://127.0.0.1:8000/
```

The service should return to `active`, and the HTTP request should connect successfully after restart.