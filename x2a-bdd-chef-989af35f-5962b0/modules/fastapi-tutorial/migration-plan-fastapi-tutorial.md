---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys a FastAPI application backed by PostgreSQL. It installs Python, Python packaging and virtual-environment tools, Git, PostgreSQL, PostgreSQL development packages, and PostgreSQL contrib packages; checks out the application into `/opt/fastapi-tutorial`; creates a Python virtual environment; installs dependencies from `requirements.txt`; creates the PostgreSQL role `fastapi` and database `fastapi_db`; writes an inline `.env` file and systemd unit; reloads systemd when applicable; and enables and starts both PostgreSQL and `fastapi-tutorial`. The cookbook contains one executed recipe, no templates, no providers, no attribute files, and no static cookbook files.

## Service Type and Instances

**Service Type**: Application Server with PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application service
  - Location/Path: `/opt/fastapi-tutorial`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Dependency file: `/opt/fastapi-tutorial/requirements.txt`
  - Environment file: `/opt/fastapi-tutorial/.env`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Source management: Git synchronization into `/opt/fastapi-tutorial`
  - Service state: Enabled and started
  - Port/Socket: Not specified in the execution tree; obtain the listening port from the application repository or generated systemd unit rather than inventing one

- **PostgreSQL**: Database service for the FastAPI application
  - Service name: `postgresql`
  - Service state: Enabled and started
  - Database user: `fastapi`
  - Database password: `fastapi_password`
  - Database: `fastapi_db`
  - Database owner: `fastapi`
  - Privileges: `fastapi` receives all privileges on `fastapi_db`
  - Port/Socket: Not specified in the execution tree; use the PostgreSQL default only after confirming the target operating system and PostgreSQL configuration

## File Structure

Only the following recipe file is shown in the execution tree and directory listing.

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
None identified
```

**Templates:**

```text
None identified
```

**Attributes:**

```text
None identified
```

**Files:**

```text
None identified
```

The `.env` file and systemd unit are created from inline Chef `file` resources. They are not cookbook template or static files.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the seven system packages `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Creates `/opt/fastapi-tutorial` with mode `0755`.
   - Synchronizes the application source into `/opt/fastapi-tutorial` using the repository URL, branch or revision, and authentication behavior defined in the actual recipe. These values are not present in the supplied execution tree.
   - Creates the virtual environment with:
     ```bash
     python3 -m venv /opt/fastapi-tutorial/venv
     ```
   - Installs Python dependencies from `/opt/fastapi-tutorial/requirements.txt` using `/opt/fastapi-tutorial/venv/bin/pip`.
   - Enables and starts the `postgresql` service.
   - Executes the PostgreSQL setup commands:
     ```bash
     sudo -u postgres psql -c "CREATE USER fastapi WITH PASSWORD 'fastapi_password';" || true
     sudo -u postgres psql -c "CREATE DATABASE fastapi_db OWNER fastapi;" || true
     sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE fastapi_db TO fastapi;" || true
     ```
   - Creates `/opt/fastapi-tutorial/.env` with mode `0644` using inline Chef content. The exact variables are not included in the supplied execution tree and must be recovered from the actual recipe.
   - Creates `/etc/systemd/system/fastapi-tutorial.service` with mode `0644` using inline Chef content. The exact unit content, application command, user, group, restart policy, and port are not included in the supplied execution tree.
   - Defines `systemd_reload` as `execute[systemd_reload]` with command `systemctl daemon-reload` and action `nothing`. No invocation event is shown in the supplied execution flow. The Ansible migration should notify a systemd daemon-reload handler when the unit changes.
   - Enables and starts the `fastapi-tutorial` service after its systemd unit is deployed.
   - Iterations: None. No `.each` loops are present.

The execution tree contains 11 resources in order:

- One `package` resource installing seven packages
- One `directory` resource
- One `git` resource
- Three `execute` resources: `create_venv`, `install_dependencies`, and `create_db_user`
- Two `service` resources: `postgresql` and `fastapi-tutorial`
- Two `file` resources: `/opt/fastapi-tutorial/.env` and `/etc/systemd/system/fastapi-tutorial.service`
- One additional `execute` resource: `systemd_reload`, with action `nothing`

No `include_recipe` calls, custom resources, provider files, iterations, or template resources are present.

## Dependencies

**External cookbook dependencies**: Not provided by the supplied metadata analysis.

**System package dependencies**:

- `python3`
- `python3-pip`
- `python3-venv`
- `git`
- `postgresql`
- `postgresql-contrib`
- `libpq-dev`

**Service dependencies**:

- `postgresql`: must be enabled and started before database initialization
- `fastapi-tutorial`: must be enabled and started after its systemd unit is written and systemd has been reloaded

**Application dependency source**:

- `/opt/fastapi-tutorial/requirements.txt`

**Ansible collection dependencies**:

- `community.postgresql` for PostgreSQL user, database, and privilege management

## Credentials

**Detection Summary**: 1 explicitly detected hardcoded credential appears in the execution tree. The inline `.env` content may contain additional secrets, but its contents are not included in the supplied analysis and therefore cannot be enumerated.

**Source**:

- **Provider**: Hardcoded in Chef command
- **URL**: None detected
- **Path**: PostgreSQL user creation command in `cookbooks/fastapi-tutorial/recipes/default.rb`

### PostgreSQL password

- **Variable(s)**: No variable name; literal password `fastapi_password`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the `execute[create_db_user]` command
- **Usage context**: Password for PostgreSQL role `fastapi`, used by the FastAPI application to connect to `fastapi_db`
- **Migration handling**: Store the value in Ansible Vault or an approved secret-management system. Do not commit it to role defaults, plaintext variables, or task output.

### `.env` credentials

- **Variable(s)**: Not available in the supplied execution tree
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`, inline content for `/opt/fastapi-tutorial/.env`
- **Current storage**: Inline Chef file content
- **Usage context**: Application environment configuration; possible database or application secrets cannot be confirmed
- **Migration handling**: Inspect the actual file content before migration, classify every variable, and store sensitive values in Ansible Vault or an approved secret-management system.

No data bag, encrypted data bag, Chef Vault, CyberArk, Conjur, HashiCorp Vault, AWS Secrets Manager, TLS certificate, private key, or environment-variable secret reference is shown in the supplied analysis.

## Checks for the Migration

**Files to verify**:

- `cookbooks/fastapi-tutorial/recipes/default.rb`
- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv/`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- PostgreSQL data directory, which is distribution-dependent and not specified by the cookbook
- PostgreSQL logs through `journalctl -u postgresql`

**Database objects to verify**:

- PostgreSQL role: `fastapi`
- PostgreSQL database: `fastapi_db`
- Database owner: `fastapi`
- Database privileges: `ALL` for `fastapi` on `fastapi_db`

**Service endpoints to check**:

- PostgreSQL network port: Not specified by the cookbook
- FastAPI network port: Not specified by the cookbook
- Unix sockets: Not specified by the cookbook

**Templates rendered**:

- None; zero templates are rendered
- The cookbook uses two inline `file` resources instead of `.erb` templates:
  - `/opt/fastapi-tutorial/.env`
  - `/etc/systemd/system/fastapi-tutorial.service`

## Pre-flight checks

```bash
# Verify all required packages for fastapi-tutorial and PostgreSQL
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev
```

### fastapi-tutorial instance

```bash
# Verify the application directory and dependency files
ls -ld /opt/fastapi-tutorial
ls -l /opt/fastapi-tutorial/requirements.txt
ls -l /opt/fastapi-tutorial/venv/bin/python
ls -l /opt/fastapi-tutorial/venv/bin/pip

# Verify the Git checkout
git -C /opt/fastapi-tutorial status
git -C /opt/fastapi-tutorial rev-parse --show-toplevel
git -C /opt/fastapi-tutorial log -1 --oneline

# Verify the Python environment
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip list

# Verify the environment file without exposing values
stat -c '%a %n' /opt/fastapi-tutorial/.env
sed -n 's/^\([^#][^=]*\)=.*/\1=<redacted>/p' /opt/fastapi-tutorial/.env

# Verify the systemd unit
stat -c '%a %n' /etc/systemd/system/fastapi-tutorial.service
systemctl cat fastapi-tutorial.service
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service

# Verify the FastAPI service
systemctl daemon-reload
systemctl status fastapi-tutorial --no-pager
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl show fastapi-tutorial \
  --property=ExecStart,WorkingDirectory,Environment,EnvironmentFiles,MainPID,ActiveState,SubState

# Inspect the configured application command and port
grep -RniE 'uvicorn|hypercorn|host|port|listen' \
  /etc/systemd/system/fastapi-tutorial.service \
  /opt/fastapi-tutorial 2>/dev/null | head -100

# Verify application logs and process state
journalctl -u fastapi-tutorial --no-pager -n 100
ps aux | grep '[f]astapi'
```

The FastAPI listening port is not specified in the execution tree. After confirming it from the systemd unit or application configuration, perform the following check with the exact discovered port:

```bash
curl -i http://127.0.0.1:<CONFIRMED_FASTAPI_PORT>/
```

Do not select a port based solely on convention.

### PostgreSQL instance

```bash
# Verify the PostgreSQL service
systemctl status postgresql --no-pager
systemctl is-enabled postgresql
systemctl is-active postgresql

# Verify local administrative connectivity
sudo -u postgres psql -d postgres -c "SELECT version();"

# Verify the PostgreSQL role
sudo -u postgres psql -d postgres -c "\du fastapi"

# Verify the database and owner
sudo -u postgres psql -d postgres -c "\l+ fastapi_db"
sudo -u postgres psql -d fastapi_db -c "SELECT current_database(), current_user;"

# Verify database privileges
sudo -u postgres psql -d postgres -c \
  "SELECT datname, datacl FROM pg_database WHERE datname = 'fastapi_db';"

# Verify that PostgreSQL is accepting connections
pg_isready

# Verify application-role connectivity
PGPASSWORD='fastapi_password' psql \
  -h 127.0.0.1 \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_database(), current_user;"

# Verify PostgreSQL logs
journalctl -u postgresql --no-pager -n 100
```

Avoid placing the plaintext password in shell history in production. Replace the direct validation credential with a protected secret mechanism for operational use.

### Shared network and ownership checks

```bash
# Discover listening sockets because neither service port is specified
ss -ltnp
ss -lxnp

# Verify application directory permissions and ownership
find /opt/fastapi-tutorial -maxdepth 2 -type d \
  -printf '%M %u:%g %p\n'

# Verify unit and environment-file permissions
ls -l /etc/systemd/system/fastapi-tutorial.service
ls -l /opt/fastapi-tutorial/.env
```