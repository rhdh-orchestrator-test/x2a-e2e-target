---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys a FastAPI application from a Git repository into `/opt/fastapi-tutorial`, installs Python, Git, PostgreSQL, and related dependencies, creates a Python virtual environment, installs application requirements, provisions the PostgreSQL user `fastapi` and database `fastapi_db`, writes an application `.env` file, and manages the application with the `fastapi-tutorial` systemd service. The cookbook configures one application instance and one PostgreSQL database dependency. The application port, socket, Git source details, environment contents, systemd unit contents, file modes, and ownership values require verification from the original recipe.

## Service Type and Instances

**Service Type**: Application Server with PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application managed by systemd
  - Location/Path: `/opt/fastapi-tutorial`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Environment file: `/opt/fastapi-tutorial/.env`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Service name: `fastapi-tutorial`
  - Source: Git repository synchronized into `/opt/fastapi-tutorial`; repository URL, branch, and revision require verification
  - Python dependency file: `/opt/fastapi-tutorial/requirements.txt`
  - Port: Not specified in the supplied execution tree
  - Unix socket: Not specified in the supplied execution tree
  - Directory mode and ownership: Require verification from the original `recipes/default.rb`
  - Environment file mode: Requires verification from the original `recipes/default.rb`
  - Systemd unit mode: Requires verification from the original `recipes/default.rb`

- **postgresql**: Supporting database service
  - Service name: `postgresql`
  - Database user: `fastapi`
  - Database name: `fastapi_db`
  - Database owner: `fastapi`
  - Privileges: All privileges on `fastapi_db` granted to `fastapi`
  - Password: `fastapi_password`
  - Port: Not explicitly configured; verify the target PostgreSQL listener

No `.each` loops or collection iterations are present in the supplied execution tree.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

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

No provider files, templates, attribute files, or static files are shown as used. The `.env` file and systemd unit are generated inline by Chef `file` resources.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the system packages `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Creates `/opt/fastapi-tutorial` with the directory resource `directory[/opt/fastapi-tutorial]`.
   - Directory mode, owner, and group are not available from the supplied analysis and must be verified from the original Chef resource.
   - Synchronizes the Git repository into `/opt/fastapi-tutorial`; repository URL, branch, and revision are not exposed.
   - Creates the virtual environment with `execute[create_venv]`:
     ```bash
     python3 -m venv /opt/fastapi-tutorial/venv
     ```
   - Installs Python dependencies with `execute[install_dependencies]`:
     ```bash
     /opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt
     ```
   - Enables and starts `postgresql` with `service[postgresql]`.
   - Creates the PostgreSQL user, database, and privileges with `execute[create_db_user]`:
     ```bash
     sudo -u postgres psql -c "CREATE USER fastapi WITH PASSWORD 'fastapi_password';" || true
     sudo -u postgres psql -c "CREATE DATABASE fastapi_db OWNER fastapi;" || true
     sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE fastapi_db TO fastapi;" || true
     ```
   - Writes `/opt/fastapi-tutorial/.env` with `file[/opt/fastapi-tutorial/.env]`; the inline content and mode require verification from the original recipe.
   - Writes `/etc/systemd/system/fastapi-tutorial.service` with `file[/etc/systemd/system/fastapi-tutorial.service]`; the inline unit content and mode require verification from the original recipe.
   - Defines `execute[systemd_reload]` for:
     ```bash
     systemctl daemon-reload
     ```
     with action `nothing`; the supplied analysis does not show a notification relationship.
   - Enables and starts `fastapi-tutorial` with `service[fastapi-tutorial]`.
   - Iterations: None; there are no `.each` loops.

**Resource summary**:

- `package`: 1 resource containing 7 packages
- `directory`: 1 resource
- `git`: 1 resource
- `execute`: 4 resources
  - `create_venv`
  - `install_dependencies`
  - `create_db_user`
  - `systemd_reload`
- `service`: 2 resources
  - `postgresql`
  - `fastapi-tutorial`
- `file`: 2 resources
  - `/opt/fastapi-tutorial/.env`
  - `/etc/systemd/system/fastapi-tutorial.service`

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

**Service dependencies**:

- `postgresql`
- `fastapi-tutorial`

**Application dependencies**:

- Python packages listed in `/opt/fastapi-tutorial/requirements.txt`
- Exact package names are not exposed in the execution tree.
- PostgreSQL Ansible modules may require a Python PostgreSQL driver on the managed host; verify the target platform before adding a package.

## Credentials

**Detection Summary**: 1 hardcoded database credential detected in 1 recipe file.

**Source**:
  - **Provider**: Hardcoded in the Chef recipe
  - **URL**: None detected
  - **Path**: None detected
  - **Source file**: `cookbooks/fastapi-tutorial/recipes/default.rb`

### PostgreSQL Password

- **Variable(s)**: No variable name; the literal `fastapi_password` is embedded in the SQL command
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the inline `execute[create_db_user]` resource
- **Usage context**: Password for PostgreSQL user `fastapi`, associated with database `fastapi_db`
- **Associated service**: `postgresql`

The inline `.env` content may contain the same credential, but its variables are not exposed in the supplied analysis. Inspect the original recipe and migrate all duplicate references to Ansible Vault.

No Chef data bags, encrypted data bags, Chef Vault calls, CyberArk/Conjur integrations, environment-variable secret references, TLS certificate paths, or embedded database connection strings are shown.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial/`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv/`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Database objects to verify**:

- PostgreSQL role `fastapi`
- PostgreSQL database `fastapi_db`
- Owner `fastapi`
- All privileges for `fastapi` on `fastapi_db`

**Service endpoints to check**:

- `fastapi-tutorial`: application port not specified; obtain it from the deployed systemd unit or application configuration
- `fastapi-tutorial`: Unix socket not specified
- `postgresql`: listener port not explicitly configured; verify the target PostgreSQL configuration

**Templates rendered**:

- None

**Inline files rendered**:

- `/opt/fastapi-tutorial/.env`: rendered once
- `/etc/systemd/system/fastapi-tutorial.service`: rendered once

## Pre-flight checks:

```bash
# Verify required packages
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

# Verify the fastapi-tutorial instance
ls -ld /opt/fastapi-tutorial
test -d /opt/fastapi-tutorial
test -x /opt/fastapi-tutorial/venv/bin/python
test -f /opt/fastapi-tutorial/requirements.txt
test -f /opt/fastapi-tutorial/.env
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip check
systemctl status fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl cat fastapi-tutorial
systemctl show fastapi-tutorial \
  --property=ExecStart \
  --property=WorkingDirectory \
  --property=User \
  --property=Group \
  --property=Environment

# Protect environment values while checking variable names
sed -n 's/^\([^=]*\)=.*/\1=<redacted>/p' /opt/fastapi-tutorial/.env

# Identify the configured application listener
systemctl show fastapi-tutorial --property=ExecStart
ss -ltnp

# Verify the postgresql instance
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql

# Verify the PostgreSQL role
sudo -u postgres psql -tAc \
  "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"

# Verify the database and owner
sudo -u postgres psql -tAc \
  "SELECT datname, pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"

# Verify database connectivity
PGPASSWORD='fastapi_password' psql -h localhost -U fastapi -d fastapi_db \
  -c "SELECT current_user, current_database();"

# Verify database privileges
sudo -u postgres psql -c "\l+ fastapi_db"

# Reload systemd after unit deployment
systemctl daemon-reload

# Review service logs for both named services
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u postgresql --no-pager -n 100

# Final state verification for fastapi-tutorial
systemctl is-active fastapi-tutorial
test -f /opt/fastapi-tutorial/.env
test -f /etc/systemd/system/fastapi-tutorial.service

# Final state verification for postgresql
systemctl is-active postgresql
```

The FastAPI port and health endpoint must be obtained from the original systemd unit or application configuration; do not assume a port or endpoint that is not explicitly defined.