---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, and PostgreSQL development dependencies, creates a Python virtual environment, installs application requirements, creates the `fastapi_db` PostgreSQL database and `fastapi` user, writes an environment file, and manages the application with a systemd service listening on port `8000`. The cookbook configures one FastAPI application instance and one local PostgreSQL database service. It has no templates, providers, custom resources, attributes, or recipe iterations.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application server
  - Application Path: `/opt/fastapi-tutorial`
  - Git Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Git Revision: `main`
  - Virtual Environment: `/opt/fastapi-tutorial/venv`
  - Application Entry Point: `app.main:app`
  - Process Manager: systemd
  - Service Name: `fastapi-tutorial`
  - Runs As: `root`
  - Working Directory: `/opt/fastapi-tutorial`
  - Listening Address: `0.0.0.0`
  - Listening Port: `8000`
  - Startup Command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Restart Policy: `Restart=always`

- **postgresql**: Local PostgreSQL database service
  - Service Name: `postgresql`
  - Database Name: `fastapi_db`
  - Database User: `fastapi`
  - Database Owner: `fastapi`
  - Database Host: `localhost`
  - Database Port: `5432`
  - Database URL: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`

No collection attributes or `.each` loops are present in the execution tree. No iteration expansion is required.

## File Structure

The execution tree contains one executed recipe file. No provider, template, attribute, or static file is listed as used.

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

The cookbook creates the following configuration files using inline Chef `file` resources:

```text
/opt/fastapi-tutorial/.env
/etc/systemd/system/fastapi-tutorial.service
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Detects whether the platform family is Fedora/RHEL or non-Fedora/RHEL.
   - On Fedora/RHEL, installs `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, and `libpq-devel`.
   - On Fedora/RHEL, runs `postgresql-setup --initdb` only when `/var/lib/pgsql/data/PG_VERSION` does not exist.
   - On non-Fedora/RHEL systems, installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Runs `python3 -m venv /opt/fastapi-tutorial/venv` when `/opt/fastapi-tutorial/venv` does not exist.
   - Installs Python dependencies with `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt` from `/opt/fastapi-tutorial`.
   - Enables and starts the `postgresql` service.
   - Creates the PostgreSQL role `fastapi` with password `fastapi_password`.
   - Creates the `fastapi_db` database owned by `fastapi`.
   - Grants all privileges on `fastapi_db` to `fastapi`.
   - Creates `/opt/fastapi-tutorial/.env` with owner `root`, group `root`, and mode `0644`.
   - Writes `PROJECT_NAME="FastAPI Tutorial"`, `API_VERSION=1.0.0`, and the PostgreSQL `DATABASE_URL` to `/opt/fastapi-tutorial/.env`.
   - Creates `/etc/systemd/system/fastapi-tutorial.service` with owner `root`, group `root`, and mode `0644`.
   - Immediately notifies `execute[systemd_reload]` after creating or updating the systemd unit.
   - Reloads systemd with `systemctl daemon-reload` when notified.
   - Enables and starts the `fastapi-tutorial` service.
   - Resources include one platform-specific `package` resource, `execute[initialize_postgresql]` on Fedora/RHEL, one `directory`, one `git`, `execute[create_venv]`, `execute[install_dependencies]`, `service[postgresql]`, `execute[create_db_user]`, two inline `file` resources, notification-triggered `execute[systemd_reload]`, and `service[fastapi-tutorial]`.
   - Iterations: None. No `.each` loops are present.

## Dependencies

**External cookbook dependencies**: None declared in the provided metadata or execution tree.

**System package dependencies**:

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

**Source-code dependencies**:

- Repository: `https://github.com/dibanez/fastapi_tutorial.git`
- Revision: `main`
- Application requirements: `/opt/fastapi-tutorial/requirements.txt`

**Service dependencies**:

- `postgresql`
- `fastapi-tutorial`

**Dependency relationship**:

```text
postgresql → fastapi-tutorial
```

The FastAPI systemd unit declares `After=network.target postgresql.service`, and the recipe starts PostgreSQL before creating the database and starting `fastapi-tutorial`.

## Credentials

**Detection Summary**: One hardcoded database credential is detected across one recipe file and one generated configuration file.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None
- **Path**: None
- **Data bag, vault, or secret manager**: None detected

### PostgreSQL Password

- **Variable(s)**:
  - PostgreSQL password literal: `fastapi_password`
  - Database connection string: `DATABASE_URL`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
  - `/opt/fastapi-tutorial/.env`
- **Current storage**: Hardcoded in the recipe and written to `/opt/fastapi-tutorial/.env`
- **Usage context**:
  - Sets the password for PostgreSQL role `fastapi`.
  - Authenticates the FastAPI application to database `fastapi_db`.
- **References**:
  - `execute[create_db_user]`: `CREATE USER fastapi WITH PASSWORD 'fastapi_password';`
  - `file[/opt/fastapi-tutorial/.env]`: `DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db`

For the Ansible migration, store the password in Ansible Vault or another approved AAP secret mechanism. Do not commit the plaintext password to the playbook or role defaults.

No Chef data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, HashiCorp Vault, AWS Secrets Manager, environment-variable secret references, TLS certificates, private keys, or API tokens were detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- `/opt/fastapi-tutorial/venv`
- The repository's application source path containing `app.main:app`
- Fedora/RHEL PostgreSQL data directory: `/var/lib/pgsql/data`
- Non-Fedora/RHEL platform-managed PostgreSQL data directory

**Service endpoints to check**:

- FastAPI application instance `fastapi-tutorial`: `0.0.0.0:8000`
- PostgreSQL service `postgresql`: `localhost:5432`
- Platform-managed PostgreSQL local Unix socket, if enabled

**Templates rendered**:

- None. No Chef templates are used.
- `/opt/fastapi-tutorial/.env`: created once by an inline file resource
- `/etc/systemd/system/fastapi-tutorial.service`: created once by an inline file resource

## Pre-flight checks

```bash
# Verify installed packages and Python tooling
python3 --version
git --version
psql --version

# Verify the application directory and repository
test -d /opt/fastapi-tutorial
git -C /opt/fastapi-tutorial status
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
git -C /opt/fastapi-tutorial rev-parse HEAD

# Verify the application files and virtual environment
test -f /opt/fastapi-tutorial/requirements.txt
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn
test -f /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' /opt/fastapi-tutorial/.env

# Verify PostgreSQL instance: postgresql
systemctl status postgresql --no-pager
systemctl is-enabled postgresql
systemctl is-active postgresql
ss -ltnp | grep ':5432'
sudo -u postgres psql -tAc \
  "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"
sudo -u postgres psql -tAc \
  "SELECT datname, pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"

# Verify the fastapi role can connect to fastapi_db
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_database(), current_user;"

# Verify database privileges
sudo -u postgres psql -d fastapi_db -c "\l+ fastapi_db"

# Verify the FastAPI instance: fastapi-tutorial
systemctl cat fastapi-tutorial
systemctl show fastapi-tutorial \
  --property=LoadState,ActiveState,SubState,UnitFileState
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl status fastapi-tutorial --no-pager

# Verify systemd configuration and reload state
systemctl cat fastapi-tutorial | grep -E \
  'After=|User=|WorkingDirectory=|Environment=|ExecStart=|Restart='
systemctl show fastapi-tutorial --property=FragmentPath
systemctl daemon-reload

# Verify the FastAPI listener and process
ss -ltnp | grep ':8000'
ps aux | grep '[u]vicorn app.main:app'

# Verify FastAPI endpoints
curl -i http://127.0.0.1:8000/docs
curl -i http://127.0.0.1:8000/openapi.json
curl -i http://127.0.0.1:8000/

# Review FastAPI service logs
journalctl -u fastapi-tutorial --no-pager -n 100

# Verify application-to-database configuration
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env
PGPASSWORD='fastapi_password' psql \
  'postgresql://fastapi:fastapi_password@localhost/fastapi_db' \
  -c "SELECT 1 AS database_connection_test;"

# Review application logs for database failures
journalctl -u fastapi-tutorial --no-pager -n 100 | \
  grep -Ei 'database|postgres|connection|error|exception'
```

Expected results:

- `postgresql` is enabled and active.
- PostgreSQL is listening on port `5432` or its configured local equivalent.
- Role `fastapi` exists.
- Database `fastapi_db` exists and is owned by `fastapi`.
- The `fastapi` role can connect to `fastapi_db`.
- The `fastapi-tutorial` systemd unit is loaded from `/etc/systemd/system/fastapi-tutorial.service`.
- `fastapi-tutorial` is enabled and active.
- The service uses `/opt/fastapi-tutorial` as its working directory.
- `ExecStart` uses `/opt/fastapi-tutorial/venv/bin/uvicorn`.
- Uvicorn starts `app.main:app` and listens on port `8000`.
- The FastAPI `/docs` and `/openapi.json` endpoints return successful responses.
- The application can connect to `fastapi_db`.
