---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI application from the `main` branch of `https://github.com/dibanez/fastapi_tutorial.git` into `/opt/fastapi-tutorial`, creates a Python virtual environment, installs the repository requirements, provisions a local PostgreSQL database and user, writes a database-backed `.env` file, and runs the application as a root-owned systemd service on port `8000`. It supports Fedora/RHEL and Debian/Ubuntu-style package names. One application instance named `fastapi-tutorial` and one PostgreSQL database named `fastapi_db` are configured.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application served by Uvicorn
  - Location/Path: `/opt/fastapi-tutorial`
  - Git repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Git revision: `main`
  - Python virtual environment: `/opt/fastapi-tutorial/venv`
  - Entry point: `app.main:app`
  - Bind address: `0.0.0.0`
  - Port/Socket: `8000`
  - Service user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Restart policy: `Restart=always`
  - Configuration file: `/opt/fastapi-tutorial/.env`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`

- **fastapi_db**: Local PostgreSQL database used by the FastAPI application
  - Database owner: `fastapi`
  - Database user: `fastapi`
  - Password: `fastapi_password`
  - Connection host: `localhost`
  - Port/Socket: `localhost:5432`
  - Connection URL: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
  - Privileges: All privileges on `fastapi_db` granted to `fastapi`

## File Structure

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

No custom resources, providers, attribute files, ERB templates, or static cookbook files are used. Configuration files are created with inline Chef `file` resources.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Detects the operating-system family with `platform_family?('fedora', 'rhel')`.
   - On Fedora/RHEL, installs `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, and `libpq-devel`.
   - On non-Fedora/RHEL systems, installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Initializes PostgreSQL on Fedora/RHEL with `postgresql-setup --initdb` when `/var/lib/pgsql/data/PG_VERSION` does not exist.
   - Creates `/opt/fastapi-tutorial` as a recursive root-owned directory with mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates the virtual environment with:
     ```bash
     python3 -m venv /opt/fastapi-tutorial/venv
     ```
     The virtual environment is created only when `/opt/fastapi-tutorial/venv` does not already exist.
   - Installs Python dependencies from `/opt/fastapi-tutorial/requirements.txt` using `/opt/fastapi-tutorial/venv/bin/pip`, with `/opt/fastapi-tutorial` as the working directory.
   - Enables and starts the `postgresql` service.
   - Creates the PostgreSQL role `fastapi`, database `fastapi_db`, and grants all privileges on `fastapi_db` to `fastapi`.
   - The original shell commands use `|| true`, which can hide failures. The Ansible migration should use explicit-state modules such as `community.postgresql.postgresql_user`, `community.postgresql.postgresql_db`, and `community.postgresql.postgresql_privs`.
   - Creates `/opt/fastapi-tutorial/.env` owned by `root:root` with mode `0644` and the following content:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Creates `/etc/systemd/system/fastapi-tutorial.service` owned by `root:root` with mode `0644`:
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
   - Triggers `systemctl daemon-reload` immediately when the systemd unit changes. The Ansible equivalent should deploy the unit and notify a handler that performs the reload only when the unit changes.
   - Enables and starts the `fastapi-tutorial` systemd service.
   - No `.each` loops or collection-based iterations are present.

## Dependencies

**External cookbook dependencies**: None listed in `metadata.rb`.

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

**Service dependencies**:

- `postgresql`
- `fastapi-tutorial`

**Supported platforms declared in metadata**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

## Credentials

**Detection Summary**: 2 credential references detected in 1 recipe file. Both are hardcoded in `cookbooks/fastapi-tutorial/recipes/default.rb` and written into the generated application configuration.

**Source**:

- **Provider**: Hardcoded
- **URL**: None
- **Path**: None
- **Secret managers**: No Chef Vault, encrypted data bag, data bag, CyberArk, Conjur, or external secret manager detected

### PostgreSQL Password

- **Variable/value**: `fastapi_password`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the PostgreSQL role-creation command
- **Usage context**: Password for the `fastapi` PostgreSQL role

The value appears in:

```bash
CREATE USER fastapi WITH PASSWORD 'fastapi_password';
```

### PostgreSQL Database Connection String

- **Variable(s)**: `DATABASE_URL`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in `/opt/fastapi-tutorial/.env`
- **Usage context**: FastAPI application database connection

The value is:

```text
postgresql://fastapi:fastapi_password@localhost/fastapi_db
```

The connection string embeds the PostgreSQL username, password, host, and database name. No TLS certificate paths, private keys, API keys, tokens, environment-based secrets, data bags, Chef Vault items, CyberArk references, Conjur variables, or additional database connection strings were detected.

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
- Database owner `fastapi`
- All privileges on `fastapi_db` for `fastapi`

**Service endpoints to check**:

- FastAPI: `0.0.0.0:8000`
- PostgreSQL: `localhost:5432`
- Unix sockets: no socket path explicitly configured

**Templates rendered**: None. No Chef templates are rendered.

**Static files deployed**: None. Application source is obtained from Git; `.env` and the systemd unit are generated from inline file content.

## Pre-flight checks:

```bash
# Verify package and tool availability
python3 --version
python3 -m pip --version
git --version
psql --version

# Verify the fastapi-tutorial application directory
stat -c '%U:%G %a %n' /opt/fastapi-tutorial
ls -ld /opt/fastapi-tutorial

# Verify the fastapi-tutorial repository checkout
git -C /opt/fastapi-tutorial remote -v
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
git -C /opt/fastapi-tutorial status --short

# Verify the fastapi-tutorial virtual environment
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip list

# Verify the fastapi_db PostgreSQL service
systemctl status postgresql --no-pager
systemctl is-enabled postgresql
systemctl is-active postgresql
ss -ltnp | grep ':5432'

# Verify the fastapi PostgreSQL role
sudo -u postgres psql -tAc \
  "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"

# Verify the fastapi_db database and owner
sudo -u postgres psql -tAc \
  "SELECT datname, pg_catalog.pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"

# Verify fastapi_db connectivity using the fastapi role
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_database(), current_user;"

# Verify fastapi privileges on fastapi_db
sudo -u postgres psql -tAc \
  "SELECT has_database_privilege('fastapi', 'fastapi_db', 'CONNECT');"

# Check PostgreSQL logs
journalctl -u postgresql --no-pager -n 100

# Verify the fastapi-tutorial environment file
stat -c '%U:%G %a %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' \
  /opt/fastapi-tutorial/.env

# Verify the fastapi-tutorial systemd unit
systemctl cat fastapi-tutorial
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
grep -E '^(Description|After|Type|User|WorkingDirectory|Environment|ExecStart|Restart|WantedBy)=' \
  /etc/systemd/system/fastapi-tutorial.service

# Verify the fastapi-tutorial service
systemctl status fastapi-tutorial --no-pager
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial

# Verify the fastapi-tutorial Uvicorn process and listener
ps -ef | grep '[u]vicorn app.main:app'
ss -ltnp | grep ':8000'

# Verify the fastapi-tutorial HTTP endpoint
curl -i http://127.0.0.1:8000/

# Verify optional FastAPI documentation endpoints
curl -i http://127.0.0.1:8000/docs
curl -i http://127.0.0.1:8000/openapi.json

# Inspect fastapi-tutorial logs
journalctl -u fastapi-tutorial --no-pager -n 100

# Confirm systemd recognizes the fastapi-tutorial unit
systemctl daemon-reload
systemctl show fastapi-tutorial \
  -p LoadState \
  -p ActiveState \
  -p UnitFileState

# Confirm fastapi-tutorial restarts successfully
systemctl restart fastapi-tutorial
systemctl is-active fastapi-tutorial
curl -i http://127.0.0.1:8000/
```

Expected results:

- The `fastapi` PostgreSQL role exists.
- The `fastapi_db` database exists and is owned by `fastapi`.
- The application user can connect to `fastapi_db`.
- The database privilege query returns `t`.
- The `fastapi-tutorial` service is `active` and `enabled`.
- The Uvicorn process uses `/opt/fastapi-tutorial/venv/bin/uvicorn`.
- Port `8000` is listening.
- The root endpoint returns an HTTP response rather than a connection failure.
- The `/docs` and `/openapi.json` endpoints return responses when exposed by the checked-out FastAPI application.
- The Ansible playbook reloads systemd through a handler triggered by changes to `/etc/systemd/system/fastapi-tutorial.service`.
