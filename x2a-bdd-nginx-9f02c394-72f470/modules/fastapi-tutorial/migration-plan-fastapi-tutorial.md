---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI tutorial application from the `main` branch of `https://github.com/dibanez/fastapi_tutorial.git` into `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, and related dependencies; creates a Python virtual environment; installs application requirements; configures the `fastapi` PostgreSQL user and `fastapi_db` database; writes the application environment file; and manages the application with the `fastapi-tutorial` systemd service listening on TCP port `8000`. One FastAPI application instance and one PostgreSQL database instance are configured.

## Service Type and Instances

**Service Type**: Application Server with PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application served by Uvicorn
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Location/Path: `/opt/fastapi-tutorial`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Working directory: `/opt/fastapi-tutorial`
  - Process user: `root`
  - Executable: `/opt/fastapi-tutorial/venv/bin/uvicorn`
  - Application target: `app.main:app`
  - Bind address: `0.0.0.0`
  - Port/Socket: TCP `8000`
  - Restart policy: `Restart=always`
  - systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Environment file: `/opt/fastapi-tutorial/.env`

- **postgresql**: PostgreSQL database service for the FastAPI application
  - Database user: `fastapi`
  - Database name: `fastapi_db`
  - Database owner: `fastapi`
  - Database host: `localhost`
  - Database connection: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
  - Privileges: `fastapi` receives all privileges on `fastapi_db`
  - Port/Socket: Distribution-default PostgreSQL port; no cookbook-specific port is configured

No collection iteration or `.each` loop is present. The cookbook configures one `fastapi-tutorial` application service and one `postgresql` database service.

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

The cookbook writes configuration using inline `file` resources. No `.erb` templates, `cookbook_file` resources, or `remote_file` resources are used. Application source is retrieved by a `git` resource from the external Git repository.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev` with one `package` resource.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates the virtual environment with:
     ```bash
     python3 -m venv /opt/fastapi-tutorial/venv
     ```
     guarded by the existence of `/opt/fastapi-tutorial/venv`.
   - Installs application dependencies with:
     ```bash
     /opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt
     ```
     using `/opt/fastapi-tutorial` as the working directory.
   - Enables and starts the `postgresql` service.
   - Creates the PostgreSQL user `fastapi`, database `fastapi_db`, database owner relationship, and database privileges. The original Chef command uses `|| true` to tolerate existing objects; the Ansible migration should use PostgreSQL-specific idempotent modules.
   - Writes `/opt/fastapi-tutorial/.env` with owner `root`, group `root`, and mode `0644`:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Writes `/etc/systemd/system/fastapi-tutorial.service` with owner `root`, group `root`, and mode `0644`:
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
   - Defines `execute[systemd_reload]` with action `nothing` to run:
     ```bash
     systemctl daemon-reload
     ```
     The source-level notification relationship from the systemd unit file resource requires verification; the structured analysis confirms the action-`nothing` resource but does not independently confirm its notification.
   - Enables and starts the `fastapi-tutorial` service after the repository, virtual environment, Python requirements, PostgreSQL service, database objects, `.env` file, and systemd unit are available.
   - Resource counts: one `package`, one `directory`, one `git`, four `execute` resources, two `file` resources, and two `service` resources.
   - Execute resources:
     - `execute[create_venv]`
     - `execute[install_dependencies]`
     - `execute[create_db_user]`
     - `execute[systemd_reload]`
   - File resources:
     - `file[/opt/fastapi-tutorial/.env]`
     - `file[/etc/systemd/system/fastapi-tutorial.service]`
   - Service resources:
     - `service[postgresql]`
     - `service[fastapi-tutorial]`

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

**Application source dependencies**:

- Git repository: `https://github.com/dibanez/fastapi_tutorial.git`
- Branch/revision: `main`
- Application requirements: `/opt/fastapi-tutorial/requirements.txt`
- Python runtime: `/opt/fastapi-tutorial/venv`

**Service dependencies**:

- `postgresql`
- `fastapi-tutorial`

The FastAPI systemd unit declares:

```ini
After=network.target postgresql.service
```

## Credentials

**Detection Summary**: One hardcoded database password is detected and used in two contexts within `cookbooks/fastapi-tutorial/recipes/default.rb`: PostgreSQL user creation and the `DATABASE_URL` environment value. No external secret-management integration is present.

**Source**:

- **Provider**: Hardcoded
- **URL**: None
- **Path**: None
- **Secret value**: `fastapi_password`

### PostgreSQL database password

- **Variable(s)**: No Chef attribute variable is used; the literal password is `fastapi_password`.
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the `execute[create_db_user]` command.
- **Usage context**: Sets the PostgreSQL password for user `fastapi`.

The source command contains:

```bash
CREATE USER fastapi WITH PASSWORD 'fastapi_password';
```

### PostgreSQL database connection string

- **Variable(s)**: `DATABASE_URL`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in `/opt/fastapi-tutorial/.env`.
- **Usage context**: Supplies the FastAPI application with its PostgreSQL connection string.

The configured value is:

```text
postgresql://fastapi:fastapi_password@localhost/fastapi_db
```

The Ansible migration should replace the hardcoded password with an Ansible Vault variable or AAP credential-backed variable and use the same variable when creating the PostgreSQL user and rendering `DATABASE_URL`.

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, `conjur_variable`, CyberArk data bags, Vault attribute namespaces, environment-variable secret lookups, TLS certificate resources, AWS Secrets Manager references, HashiCorp Vault references, or other external secret-provider references were detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/venv/bin/python`
- `/opt/fastapi-tutorial/venv/bin/pip`
- `/opt/fastapi-tutorial/venv/bin/uvicorn`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Service endpoints to check**:

- FastAPI HTTP endpoint: `127.0.0.1:8000`
- FastAPI bind address: `0.0.0.0:8000`
- PostgreSQL: distribution-default configuration; no explicit cookbook port
- Unix sockets: not explicitly configured

**Templates rendered**:

- No `.erb` templates are rendered.
- `/opt/fastapi-tutorial/.env`: inline file content, render count `1`
- `/etc/systemd/system/fastapi-tutorial.service`: inline file content, render count `1`

## Pre-flight checks

```bash
# Verify required packages
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev 2>/dev/null || \
rpm -q python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

# Verify the fastapi-tutorial application instance
test -d /opt/fastapi-tutorial
test -f /opt/fastapi-tutorial/requirements.txt
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn
git -C /opt/fastapi-tutorial remote -v
git -C /opt/fastapi-tutorial branch --show-current
git -C /opt/fastapi-tutorial rev-parse --verify HEAD
/opt/fastapi-tutorial/venv/bin/pip check
/opt/fastapi-tutorial/venv/bin/pip show fastapi
/opt/fastapi-tutorial/venv/bin/pip show uvicorn

# Verify the postgresql database instance
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
sudo -u postgres psql -tAc "SELECT usename FROM pg_user WHERE usename = 'fastapi';"
sudo -u postgres psql -tAc "SELECT datname, pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"

# Verify PostgreSQL authentication and database access
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d postgres \
  -c "SELECT current_user;"

PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_database(), current_user;"

# Verify the application environment file without exposing its secret
grep '^PROJECT_NAME=' /opt/fastapi-tutorial/.env
grep '^API_VERSION=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env
stat -c '%U:%G %a %n' /opt/fastapi-tutorial/.env

# Verify the fastapi-tutorial systemd instance
systemctl cat fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl show fastapi-tutorial \
  --property=User,WorkingDirectory,ExecStart,Restart,Environment
grep '^After=.*postgresql.service' /etc/systemd/system/fastapi-tutorial.service
grep '^User=root' /etc/systemd/system/fastapi-tutorial.service
grep '^WorkingDirectory=/opt/fastapi-tutorial' /etc/systemd/system/fastapi-tutorial.service
grep '^ExecStart=/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000' \
  /etc/systemd/system/fastapi-tutorial.service
grep '^Restart=always' /etc/systemd/system/fastapi-tutorial.service
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl daemon-reload

# Verify the FastAPI process and endpoint
ps aux | grep '[u]vicorn'
curl -i http://127.0.0.1:8000/
ss -tlnp | grep ':8000'

# Review application logs
journalctl -u fastapi-tutorial -n 100 --no-pager
journalctl -u fastapi-tutorial -f

# Verify restart behavior for the fastapi-tutorial instance
systemctl restart fastapi-tutorial
systemctl is-active fastapi-tutorial
curl -i http://127.0.0.1:8000/
```

Expected results include:

- `postgresql` is enabled and active.
- User `fastapi` exists and can authenticate locally.
- Database `fastapi_db` exists and is owned by `fastapi`.
- `/opt/fastapi-tutorial/.env` is owned by `root:root` with mode `0644`.
- `fastapi-tutorial` is enabled and active.
- Uvicorn listens on TCP port `8000`.
- `http://127.0.0.1:8000/` returns an HTTP response.
- The application logs contain successful Uvicorn startup without import errors, database authentication failures, missing dependency errors, or port-binding failures.