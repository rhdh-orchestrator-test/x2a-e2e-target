---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys one FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` to `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, and platform-specific PostgreSQL development packages; creates a Python virtual environment; installs dependencies from `requirements.txt`; initializes and starts PostgreSQL; creates the `fastapi` PostgreSQL role and `fastapi_db` database; writes the application `.env` file; and runs `app.main:app` with Uvicorn through systemd on port `8000`. The cookbook contains one recipe, no custom resources, no templates, no attributes, no static files, and no iterable instance collections.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application server
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Application directory: `/opt/fastapi-tutorial`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Application entry point: `app.main:app`
  - Process manager: systemd
  - ASGI server: Uvicorn
  - Bind address: `0.0.0.0`
  - Port: `8000`
  - Runtime user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Restart policy: `always`
  - Environment file: `/opt/fastapi-tutorial/.env`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`

- **PostgreSQL**: Local database service for the FastAPI application
  - Chef service resource name: `postgresql`
  - Database role: `fastapi`
  - Database: `fastapi_db`
  - Password: stored as `fastapi_password` in the original Chef recipe; use an Ansible Vault variable after migration
  - Connection host: `localhost`
  - Default port: `5432`
  - Database URL: `postgresql://fastapi:<vaulted-password>@localhost/fastapi_db`

**Iterations**: No `.each` loops or collection-based iterations are present.

## File Structure

Only one recipe file is executed by the cookbook. No providers, templates, attributes, or static files are used.

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

The `.env` file and systemd unit are created directly with Chef `file` resources rather than rendered from `.erb` templates.

## Module Explanation

The cookbook performs operations in this order:

1. **`default`** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Executes the complete deployment flow with no `include_recipe` calls or dependency recipe chain.
   - On Fedora, RHEL, CentOS, and other platforms matching `platform_family?('fedora', 'rhel')`, installs:
     - `python3`
     - `python3-pip`
     - `git`
     - `postgresql-server`
     - `postgresql-contrib`
     - `libpq-devel`
   - On non-RedHat-family platforms, installs:
     - `python3`
     - `python3-pip`
     - `python3-venv`
     - `git`
     - `postgresql`
     - `postgresql-contrib`
     - `libpq-dev`
   - On RedHat-family platforms, initializes PostgreSQL with `postgresql-setup --initdb` using `execute[initialize_postgresql]`, guarded by `creates: /var/lib/pgsql/data/PG_VERSION`.
   - Creates `/opt/fastapi-tutorial` with owner `root`, group `root`, mode `0755`, and recursive creation enabled.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial` using `git[/opt/fastapi-tutorial]`.
   - Creates `/opt/fastapi-tutorial/venv` with:
     ```text
     python3 -m venv /opt/fastapi-tutorial/venv
     ```
     using `execute[create_venv]`, guarded by `creates: /opt/fastapi-tutorial/venv`.
   - Installs Python dependencies with `execute[install_dependencies]`:
     ```text
     /opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt
     ```
     from working directory `/opt/fastapi-tutorial`.
   - Enables and starts the `postgresql` service with `service[postgresql]`.
   - Creates the PostgreSQL role and database using `execute[create_db_user]`. The original commands run as the `postgres` OS user and create:
     - Role: `fastapi`
     - Password: `fastapi_password`
     - Database: `fastapi_db`
     - Owner: `fastapi`
     - Privileges: `ALL`
   - Migrates the database setup to idempotent `community.postgresql.postgresql_user`, `community.postgresql.postgresql_db`, and, if required, `community.postgresql.postgresql_privs` tasks. Database administration runs as the `postgres` OS user, and the password is stored in Ansible Vault with `no_log: true`.
   - Creates `/opt/fastapi-tutorial/.env` using `file[/opt/fastapi-tutorial/.env]`, owned by `root:root` with mode `0644`, containing:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:<vaulted-password>@localhost/fastapi_db
     ```
     The migrated implementation must construct `DATABASE_URL` from the vaulted password rather than embedding the plaintext password.
   - Creates `/etc/systemd/system/fastapi-tutorial.service` using `file[/etc/systemd/system/fastapi-tutorial.service]`, owned by `root:root` with mode `0644`. The unit runs:
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
   - Notifies `execute[systemd_reload]` to run `systemctl daemon-reload` immediately when the systemd unit changes. The resource has action `nothing`.
   - Enables and starts `fastapi-tutorial` with `service[fastapi-tutorial]`.
   - Ensures the FastAPI service starts after the repository, virtual environment, dependencies, PostgreSQL service, PostgreSQL role and database, `.env` file, systemd unit, and systemd daemon reload are available.
   - No `.each` loops are present; there are no additional iteration names to expand.

## Dependencies

**External cookbook dependencies**: None listed in `metadata.rb`.

**Supported operating systems**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**System package dependencies**:

RedHat-family platforms:

- `python3`
- `python3-pip`
- `git`
- `postgresql-server`
- `postgresql-contrib`
- `libpq-devel`

Non-RedHat-family platforms:

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

**Application dependency source**: `/opt/fastapi-tutorial/requirements.txt`

## Credentials

**Detection Summary**: 1 database credential detected in 1 recipe file. The same credential is used in the PostgreSQL role creation command and the application database connection string.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None
- **Path**: None
- **Recommended migrated storage**: Ansible Vault

### PostgreSQL Database Password

- **Variable**: `fastapi_password`
- **Source file**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded plaintext
- **Usage context**:
  - PostgreSQL role creation for `fastapi`
  - Application connection string for `fastapi_db`
- **Migrated storage**: Ansible Vault variable such as `vault_fastapi_db_password`
- **Migration requirements**:
  - Use the vaulted variable with `community.postgresql.postgresql_user`.
  - Construct the `.env` `DATABASE_URL` from the vaulted variable.
  - Mark password-related tasks with `no_log: true`.
  - Do not place the plaintext password in inventory, defaults, task files, or verification documentation.
  - Use an interactive credential mechanism or a runtime vaulted variable for connectivity checks.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, HashiCorp Vault, AWS Secrets Manager, TLS certificates, private keys, API tokens, or other credential namespaces were detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- `/var/lib/pgsql/data/PG_VERSION` on RedHat-family platforms

**Database objects to verify**:

- PostgreSQL role: `fastapi`
- PostgreSQL database: `fastapi_db`
- Database owner: `fastapi`

**Service endpoints to check**:

- FastAPI: `http://127.0.0.1:8000`
- FastAPI listening port: `8000`
- PostgreSQL TCP port: `5432`, if TCP listening is enabled
- PostgreSQL local Unix socket: platform-specific socket directory

**Templates rendered**:

- None
- Render count: `0`

The cookbook uses direct `file` resources for both `.env` and the systemd unit.

**Service restart/reload behavior**:

- Changes to `/etc/systemd/system/fastapi-tutorial.service` trigger `systemctl daemon-reload` immediately.
- Changes to `.env` do not explicitly restart `fastapi-tutorial`.
- PostgreSQL is not explicitly restarted after package installation or database creation.

## Pre-flight checks

### Platform and package checks

```bash
python3 --version
python3 -m pip --version
git --version
psql --version

# RedHat-family platforms only
test -f /var/lib/pgsql/data/PG_VERSION && echo "PostgreSQL initialized"
```

### PostgreSQL instance checks

```bash
systemctl status postgresql --no-pager
systemctl is-enabled postgresql
systemctl is-active postgresql

sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='fastapi';"

sudo -u postgres psql -tAc \
  "SELECT datname, pg_catalog.pg_get_userbyid(datdba) FROM pg_database WHERE datname='fastapi_db';"

# Supply the vaulted password at runtime; do not commit a literal password.
read -s FASTAPI_DB_PASSWORD
PGPASSWORD="$FASTAPI_DB_PASSWORD" psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_database(), current_user;"
unset FASTAPI_DB_PASSWORD

ss -tlnp | grep ':5432' || true
```

Expected PostgreSQL service state:

```text
enabled
active
```

Expected role result:

```text
1
```

Expected database result:

```text
fastapi_db|fastapi
```

Expected connectivity result:

```text
fastapi_db | fastapi
```

### `fastapi-tutorial` application instance checks

```bash
stat -c '%A %U:%G %n' /opt/fastapi-tutorial
git -C /opt/fastapi-tutorial status --short --branch
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD

test -f /opt/fastapi-tutorial/requirements.txt && echo "requirements.txt exists"
test -x /opt/fastapi-tutorial/venv/bin/python && echo "virtual environment exists"
test -x /opt/fastapi-tutorial/venv/bin/uvicorn && echo "uvicorn exists"

/opt/fastapi-tutorial/venv/bin/pip list

stat -c '%A %U:%G %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION)=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env \
  | sed -E 's#(postgresql://[^:]+:)[^@]+#\1********#'
```

Expected Git branch:

```text
main
```

Expected non-secret environment values:

```text
PROJECT_NAME="FastAPI Tutorial"
API_VERSION=1.0.0
```

### Systemd unit checks for `fastapi-tutorial`

```bash
test -f /etc/systemd/system/fastapi-tutorial.service && echo "unit file exists"

systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service

grep -E '^(Description|After|Type|User|WorkingDirectory|Environment|ExecStart|Restart|WantedBy)=' \
  /etc/systemd/system/fastapi-tutorial.service

systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl status fastapi-tutorial --no-pager
```

Expected key values:

```text
User=root
WorkingDirectory=/opt/fastapi-tutorial
Environment="PATH=/opt/fastapi-tutorial/venv/bin"
ExecStart=/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
```

Expected service state:

```text
enabled
active
```

### FastAPI endpoint and process checks

```bash
ps aux | grep '[u]vicorn app.main:app'

ss -tlnp | grep ':8000'

curl -i http://127.0.0.1:8000/
curl -I http://127.0.0.1:8000/
```

The process should include:

```text
/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Expected results:

- A process listens on TCP port `8000`.
- The root endpoint returns an application response rather than a connection-refused error.
- The exact HTTP status for `/` depends on the repository implementation.

### FastAPI logs

```bash
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u fastapi-tutorial -f
```

Check for:

- Uvicorn startup messages.
- Successful binding to `0.0.0.0:8000`.
- Database connection errors.
- Python import errors.
- Missing dependency errors.
- Repeated restart cycles.

### Network checks

```bash
ss -tlnp | grep ':8000'
ss -tlnp | grep ':5432' || true
```

FastAPI must listen on port `8000`. PostgreSQL must be reachable through its configured local socket and, when TCP is enabled, through port `5432`.