---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the `fastapi-tutorial` FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, and PostgreSQL development packages; creates a Python virtual environment; installs application requirements; initializes and manages PostgreSQL; creates the `fastapi` role and `fastapi_db` database; writes an environment file containing the database connection; and manages the application with a systemd service listening on `0.0.0.0:8000`. The current database password is hardcoded and must be moved to Ansible Vault during migration.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application server
  - Application path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Service user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Startup command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Listening address: `0.0.0.0:8000`
  - Restart policy: `always`
  - Environment file: `/opt/fastapi-tutorial/.env`

- **postgresql**: PostgreSQL database service used by `fastapi-tutorial`
  - Service name: `postgresql`
  - Database: `fastapi_db`
  - Role: `fastapi`
  - Host: `localhost`
  - Port: `5432`
  - Connection URL: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`

## File Structure

The following are the only cookbook files used in the migration.

**Recipes:**
```text
cookbooks/fastapi-tutorial/recipes/default.rb
```

**Providers:**
```text
```

No custom Chef providers are used.

**Templates:**
```text
```

No ERB templates are rendered. Configuration files are written using inline Chef `file` resources.

**Attributes:**
```text
cookbooks/fastapi-tutorial/attributes/default.rb
```

**Files:**
```text
```

No static files are deployed with `cookbook_file` or `remote_file`.

## Attributes

**Source file**: `cookbooks/fastapi-tutorial/attributes/default.rb`

| Chef attribute | Value | Ansible equivalent |
|---|---|---|
| `node['fastapi_tutorial']['app_path']` | `/opt/fastapi-tutorial` | `fastapi_tutorial_app_path` |
| `node['fastapi_tutorial']['repository']` | `https://github.com/dibanez/fastapi_tutorial.git` | `fastapi_tutorial_repository` |
| `node['fastapi_tutorial']['revision']` | `main` | `fastapi_tutorial_revision` |
| `node['fastapi_tutorial']['service_port']` | `8000` | `fastapi_tutorial_service_port` |

These are scalar attributes. No collection attributes or iterable instance definitions are present.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs platform-specific system packages.
   - On Fedora/RHEL, installs `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, and `libpq-devel`.
   - On Fedora/RHEL, runs `postgresql-setup --initdb` through `execute[initialize_postgresql]` only when `/var/lib/pgsql/data/PG_VERSION` does not exist.
   - On other supported platforms, installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Creates `/opt/fastapi-tutorial` as a recursive `0755` directory owned by `root:root`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial` using a `git` resource.
   - Creates `/opt/fastapi-tutorial/venv` with `python3 -m venv /opt/fastapi-tutorial/venv` when the directory does not exist.
   - Installs Python dependencies using `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt` from `/opt/fastapi-tutorial`. This runs during every Chef convergence.
   - Enables and starts the `postgresql` service.
   - Creates the PostgreSQL role `fastapi` with password `fastapi_password`, creates the `fastapi_db` database owned by `fastapi`, and grants all privileges on `fastapi_db` to `fastapi`.
   - The original database commands use `|| true`, allowing existing roles and databases to succeed. The Ansible migration should use idempotent `community.postgresql.postgresql_user`, `community.postgresql.postgresql_db`, and, if required, `community.postgresql.postgresql_privs` tasks.
   - Writes `/opt/fastapi-tutorial/.env` as `root:root` with mode `0644`:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Writes `/etc/systemd/system/fastapi-tutorial.service` as `root:root` with mode `0644`:
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
   - Immediately notifies `execute[systemd_reload]`, which runs `systemctl daemon-reload` only when the unit file changes.
   - Enables and starts the `fastapi-tutorial` service after the repository, virtual environment, Python dependencies, PostgreSQL service, database objects, environment file, systemd unit, and daemon reload are complete.
   - No `.each` loops are present. The only application instance is `fastapi-tutorial`; the only database service instance is `postgresql`.

## Dependencies

**External cookbook dependencies**: None declared in the analyzed metadata.

**System package dependencies**:

- Fedora/RHEL:
  - `python3`
  - `python3-pip`
  - `git`
  - `postgresql-server`
  - `postgresql-contrib`
  - `libpq-devel`
- Other supported platforms:
  - `python3`
  - `python3-pip`
  - `python3-venv`
  - `git`
  - `postgresql`
  - `postgresql-contrib`
  - `libpq-dev`

**Application dependencies**:

- `/opt/fastapi-tutorial/requirements.txt`
- Installed with `/opt/fastapi-tutorial/venv/bin/pip`

**Service dependencies**:

- `postgresql`
- `fastapi-tutorial`
- The FastAPI systemd unit declares ordering after `postgresql.service`.

## Credentials

**Detection Summary**: One hardcoded database password was detected in `cookbooks/fastapi-tutorial/recipes/default.rb` and duplicated in the generated `.env` configuration. The PostgreSQL username is also hardcoded but is an identifier rather than a secret. No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, or external secret-management integrations were detected.

**Source**:
  - **Provider**: Hardcoded in Chef recipe
  - **URL**: None
  - **Path**: None

### PostgreSQL application password

- **Variable(s)**: Password literal `fastapi_password`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
  - Generated `/opt/fastapi-tutorial/.env`
- **Current storage**: Hardcoded in the PostgreSQL `execute` resource and repeated in the database connection string
- **Usage context**:
  - Creates the `fastapi` PostgreSQL role:
    ```sql
    CREATE USER fastapi WITH PASSWORD 'fastapi_password';
    ```
  - Configures the application connection:
    ```text
    DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
    ```
- **Migration requirement**: Store the password in Ansible Vault and use the vaulted value both when creating the PostgreSQL role and when rendering `/opt/fastapi-tutorial/.env`.

### PostgreSQL username

- **Variable(s)**: `fastapi`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the recipe and connection string
- **Usage context**:
  - PostgreSQL role name
  - Owner of `fastapi_db`
  - Username in `DATABASE_URL`
- **Migration requirement**: Represent the value as a dedicated Ansible variable.

### TLS and certificate review

No `.pem`, `.key`, or `.crt` references were detected. The application uses an unencrypted local PostgreSQL connection over `localhost`; this cookbook does not create TLS configuration.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- Fedora/RHEL PostgreSQL data directory: `/var/lib/pgsql/data/`
- Distribution-specific PostgreSQL data directory on non-RHEL systems
- PostgreSQL database: `fastapi_db`
- PostgreSQL role: `fastapi`

**Service endpoints to check**:

- `fastapi-tutorial`: `0.0.0.0:8000`
- `postgresql`: `localhost:5432`
- PostgreSQL distribution-specific Unix socket

**Templates rendered**:

- No templates are rendered.
- `/opt/fastapi-tutorial/.env`: rendered once by an inline Chef `file` resource.
- `/etc/systemd/system/fastapi-tutorial.service`: rendered once by an inline Chef `file` resource.

## Pre-flight checks

### Application instance: fastapi-tutorial

```bash
# Verify the application directory
ls -ld /opt/fastapi-tutorial
stat -c '%U:%G %a %n' /opt/fastapi-tutorial

# Verify the repository
git -C /opt/fastapi-tutorial remote -v
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
git -C /opt/fastapi-tutorial rev-parse HEAD
ls -l /opt/fastapi-tutorial/requirements.txt

# Verify the virtual environment
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip list

# Verify the environment file without exposing the password
ls -l /opt/fastapi-tutorial/.env
stat -c '%U:%G %a %n' /opt/fastapi-tutorial/.env
grep '^PROJECT_NAME=' /opt/fastapi-tutorial/.env
grep '^API_VERSION=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env | sed 's/:[^@]*@/:REDACTED@/'

# Verify the systemd unit
ls -l /etc/systemd/system/fastapi-tutorial.service
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl status fastapi-tutorial --no-pager

# Verify service configuration
grep '^Description=' /etc/systemd/system/fastapi-tutorial.service
grep '^After=' /etc/systemd/system/fastapi-tutorial.service
grep '^User=' /etc/systemd/system/fastapi-tutorial.service
grep '^WorkingDirectory=' /etc/systemd/system/fastapi-tutorial.service
grep '^ExecStart=' /etc/systemd/system/fastapi-tutorial.service
grep '^Restart=' /etc/systemd/system/fastapi-tutorial.service

# Verify the FastAPI process and endpoint
ps -ww -C uvicorn -o pid,user,args
ss -ltnp | grep ':8000'
curl -I http://127.0.0.1:8000/
curl -sS http://127.0.0.1:8000/

# Review application logs and restart state
journalctl -u fastapi-tutorial --no-pager -n 100
systemctl show fastapi-tutorial \
  --property=ActiveState \
  --property=SubState \
  --property=ExecMainStatus \
  --property=NRestarts
```

The application must listen on TCP port `8000`. The exact HTTP status and response body depend on the tutorial routes, but the request must reach Uvicorn without a connection-refused error.

### Database instance: postgresql

```bash
# Verify PostgreSQL service state
systemctl status postgresql --no-pager
systemctl is-enabled postgresql
systemctl is-active postgresql

# Verify PostgreSQL client and listener
psql --version
ss -ltnp | grep ':5432'
sudo -u postgres pg_isready -h localhost -p 5432

# Verify the role and database
sudo -u postgres psql -d postgres -c "\du fastapi"
sudo -u postgres psql -d postgres -c "\l+ fastapi_db"

# Verify application credentials and connectivity
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_user, current_database();"

PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT 1;"

# Review PostgreSQL logs
journalctl -u postgresql --no-pager -n 100
```

### Operating system and package checks

```bash
cat /etc/os-release
python3 --version
python3 -m pip --version
git --version
psql --version

# Fedora/RHEL
rpm -q python3 python3-pip git postgresql-server postgresql-contrib libpq-devel

# Debian/Ubuntu and other non-RHEL platforms
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev
```

### Ordering and connectivity checks

```bash
# Reload systemd after validating the unit
systemctl daemon-reload

# Confirm the PostgreSQL dependency is active before the application
systemctl is-active postgresql
systemctl is-active fastapi-tutorial

# Confirm the application database URL exists without exposing its password
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env | sed 's/:[^@]*@/:REDACTED@/'

# Confirm the application can access its files
systemctl show fastapi-tutorial --property=WorkingDirectory
test -r /opt/fastapi-tutorial/.env
test -x /opt/fastapi-tutorial/venv/bin/uvicorn

# Review recent application failures
journalctl -u fastapi-tutorial --since "15 minutes ago" --no-pager \
  | grep -E 'ERROR|Traceback|failed'
```