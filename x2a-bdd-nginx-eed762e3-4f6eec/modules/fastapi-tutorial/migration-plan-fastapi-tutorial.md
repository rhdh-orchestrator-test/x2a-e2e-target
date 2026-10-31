---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI Tutorial application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main`. It installs Python, PostgreSQL, Git, and PostgreSQL development packages; creates a Python virtual environment; installs application dependencies; creates the `fastapi` PostgreSQL role and `fastapi_db` database; writes an environment file; and manages the `fastapi-tutorial.service` systemd unit on port `8000`. The database password is hardcoded in the Chef recipe and must be migrated to an Ansible Vault-managed variable.

## Service Type and Instances

**Service Type**: Application Server with PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application server
  - Location/Path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Port/Socket: `0.0.0.0:8000`
  - Application command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Systemd unit: `fastapi-tutorial.service`
  - Service user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Restart policy: `Restart=always`
  - Environment PATH: `/opt/fastapi-tutorial/venv/bin`
  - Key configuration: Starts after `network.target` and `postgresql.service`; enabled through `multi-user.target`

- **postgresql**: PostgreSQL database service for the FastAPI application
  - Location/Path: Distribution-specific PostgreSQL data directory
  - Port/Socket: `localhost:5432` by default; local Unix socket is distribution-specific
  - Database role: `fastapi`
  - Database: `fastapi_db`
  - Database owner: `fastapi`
  - Privileges: All privileges on `fastapi_db` granted to `fastapi`
  - Key configuration: PostgreSQL is enabled and started before database provisioning

There are no collection attributes or `.each` iterations in the cookbook. The cookbook configures one FastAPI application instance and one PostgreSQL database instance.

## File Structure

Only files shown in the supplied execution tree and directory listing are included.

**Recipes:**
```text
recipes/default.rb
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

The `.env` file and systemd unit are generated inline by `recipes/default.rb`; they are not static cookbook files or ERB templates.

## Module Explanation

The cookbook performs operations in this order. It has one entry recipe and no `include_recipe` calls.

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the system packages `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev` using the platform package manager.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` into `/opt/fastapi-tutorial` at revision `main`.
   - Creates `/opt/fastapi-tutorial/venv` with `python3 -m venv /opt/fastapi-tutorial/venv` when the virtual-environment path does not exist.
   - Installs Python dependencies from `/opt/fastapi-tutorial/requirements.txt` using `/opt/fastapi-tutorial/venv/bin/pip`.
   - Enables and starts the `postgresql` service.
   - Creates the PostgreSQL role `fastapi` with the migrated secret password.
   - Creates the `fastapi_db` database owned by `fastapi`.
   - Grants all privileges on `fastapi_db` to `fastapi`.
   - Writes `/opt/fastapi-tutorial/.env` with:
     - `PROJECT_NAME="FastAPI Tutorial"`
     - `API_VERSION=1.0.0`
     - `DATABASE_URL=postgresql://fastapi:<vault-managed-password>@localhost/fastapi_db`
   - Preserves owner `root` and group `root`; the original mode is `0644`, but mode `0600` is recommended for the Ansible migration.
   - Writes `/etc/systemd/system/fastapi-tutorial.service` with owner `root`, group `root`, and mode `0644`.
   - Configures the systemd service to:
     - Run as `root`
     - Use `/opt/fastapi-tutorial` as its working directory
     - Use `/opt/fastapi-tutorial/venv/bin` in `PATH`
     - Execute `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
     - Restart automatically with `Restart=always`
     - Start after `network.target` and `postgresql.service`
   - Reloads systemd when `/etc/systemd/system/fastapi-tutorial.service` changes.
   - Enables and starts `fastapi-tutorial.service` after the repository, virtual environment, dependencies, PostgreSQL service, database, environment file, and systemd unit are ready.
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

**Ansible collection dependencies**:

- `community.postgresql` for declarative PostgreSQL role, database, and privilege management

**Service dependencies**:

- `postgresql`
- `fastapi-tutorial`

**Application source dependency**:

- Repository: `https://github.com/dibanez/fastapi_tutorial.git`
- Revision: `main`

**Supported operating systems from metadata**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

## Credentials

**Detection Summary**: 1 database credential detected in 1 recipe file. The credential is used in both the PostgreSQL role creation command and the application connection string.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None
- **Path**: None
- **Current storage**: Plaintext hardcoded password
- **Recommended storage**: Ansible Vault variable

### PostgreSQL password

- **Variable(s)**: `fastapi_password`; migrate to `vault_fastapi_db_password`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Occurrences**:
  - PostgreSQL role creation: `CREATE USER fastapi WITH PASSWORD 'fastapi_password';`
  - Application connection string: `DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Current storage**: Hardcoded plaintext in an `execute` resource and inline `.env` content
- **Usage context**:
  - Authenticates the `fastapi` PostgreSQL role
  - Allows the FastAPI application to connect to `fastapi_db`
- **Migration requirement**: Store the value in Ansible Vault as `vault_fastapi_db_password` and use it in both the PostgreSQL role task and generated `.env` file.

No Chef data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secret references, TLS certificates, private keys, API tokens, or other secret namespaces were detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/app/main.py` or the repository’s actual application entry point
- PostgreSQL data and log locations determined by the target distribution

**Service endpoints to check**:

- FastAPI HTTP endpoint: `0.0.0.0:8000`
- PostgreSQL endpoint: `localhost:5432`
- PostgreSQL Unix socket: distribution-specific; no explicit socket path is configured

**Templates rendered**: None. The cookbook uses inline file content rather than ERB templates.

**Template render counts**: None.

**Static files deployed**: None. The repository is retrieved using the Chef `git` resource.

## Pre-flight checks

### FastAPI application instance: `fastapi-tutorial`

```bash
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev 2>/dev/null \
  || rpm -q python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

stat -c '%A %U:%G %n' /opt/fastapi-tutorial
git -C /opt/fastapi-tutorial remote -v
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
git -C /opt/fastapi-tutorial rev-parse HEAD

test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip --version
/opt/fastapi-tutorial/venv/bin/pip check
/opt/fastapi-tutorial/venv/bin/pip show uvicorn

stat -c '%A %U:%G %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' /opt/fastapi-tutorial/.env

systemctl cat fastapi-tutorial.service
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl status fastapi-tutorial --no-pager

systemctl show fastapi-tutorial \
  -p User \
  -p WorkingDirectory \
  -p ExecStart \
  -p Restart

curl -i http://127.0.0.1:8000/
ss -ltnp | grep ':8000'
ps -ef | grep '[u]vicorn app.main:app'

journalctl -u fastapi-tutorial --no-pager -n 50
```

Expected results:

- All seven required packages are installed.
- `/opt/fastapi-tutorial` exists with owner `root`, group `root`, and mode `0755`.
- The Git remote is `https://github.com/dibanez/fastapi_tutorial.git`.
- The checked-out revision corresponds to `main`.
- The virtual environment and its Python and pip executables exist.
- `pip check` reports no broken dependencies.
- `uvicorn` is installed.
- `.env` contains `PROJECT_NAME`, `API_VERSION`, and `DATABASE_URL`.
- `fastapi-tutorial.service` is enabled and active.
- The service runs as `root` from `/opt/fastapi-tutorial`.
- Uvicorn uses `/opt/fastapi-tutorial/venv/bin/uvicorn`, binds to `0.0.0.0`, and listens on port `8000`.
- The application returns an HTTP response. The exact status code depends on the repository’s routes.
- Logs contain no import, permission, database authentication, or binding errors.

### PostgreSQL instance: `postgresql`

```bash
systemctl status postgresql --no-pager
systemctl is-enabled postgresql
systemctl is-active postgresql

sudo -u postgres psql -tAc \
  "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"

sudo -u postgres psql -tAc \
  "SELECT datname, pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"

PGPASSWORD="$vault_fastapi_db_password" \
psql -h localhost -U fastapi -d fastapi_db \
  -c "SELECT current_database(), current_user;"

ss -ltnp | grep ':5432'

journalctl -u postgresql --no-pager -n 50
```

Expected results:

- `postgresql` is enabled and active.
- The `fastapi` PostgreSQL role exists.
- `fastapi_db` exists and is owned by `fastapi`.
- The application credentials connect successfully.
- `current_database` is `fastapi_db`.
- `current_user` is `fastapi`.
- PostgreSQL listens on the local PostgreSQL port, normally `5432`.
- PostgreSQL logs contain no startup or authentication errors.

### Application-to-database connectivity

```bash
PGPASSWORD="$vault_fastapi_db_password" \
/opt/fastapi-tutorial/venv/bin/python - <<'PY'
import os
import psycopg2

connection = psycopg2.connect(
    "postgresql://fastapi:" + os.environ["PGPASSWORD"] + "@localhost/fastapi_db"
)
with connection.cursor() as cursor:
    cursor.execute("SELECT 1")
    print(cursor.fetchone())
connection.close()
PY
```

Expected output:

```text
(1,)
```

This verifies that the Python environment and PostgreSQL credentials work together independently of the systemd service.