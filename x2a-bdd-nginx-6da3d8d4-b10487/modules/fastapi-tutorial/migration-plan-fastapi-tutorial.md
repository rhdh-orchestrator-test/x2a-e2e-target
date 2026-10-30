---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys a FastAPI application from a Git repository into `/opt/fastapi-tutorial`, creates a Python virtual environment, installs dependencies from `requirements.txt`, installs and starts PostgreSQL, creates the `fastapi` PostgreSQL user and `fastapi_db` database, writes an application `.env` file and a systemd unit, declares a non-running systemd reload action, and enables and starts the `fastapi-tutorial` service. The application port is not specified in the supplied execution analysis and must be obtained from the systemd unit or application configuration before implementation.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application service
  - Location/Path: `/opt/fastapi-tutorial`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Requirements file: `/opt/fastapi-tutorial/requirements.txt`
  - Environment file: `/opt/fastapi-tutorial/.env`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Source: Git repository synchronized into `/opt/fastapi-tutorial`
  - Service actions: Enable and start
  - Port/Socket: Not specified; obtain the value from the systemd unit or application configuration
  - Key Config: Python virtual environment, installed requirements, inline `.env` configuration, and inline systemd unit

- **postgresql**: PostgreSQL database service
  - Location/Path: System package and platform-default data directories
  - Port/Socket: Not explicitly configured; use the PostgreSQL package default, normally port `5432`
  - Service actions: Enable and start
  - Database user: `fastapi`
  - Database: `fastapi_db`
  - Database owner: `fastapi`
  - Database password: Hardcoded literal `fastapi_password` in the Chef recipe
  - Key Config: `fastapi` receives all privileges on `fastapi_db`

## File Structure

Only the recipe file is present in the supplied cookbook directory and execution analysis.

**Recipes:**
```text
cookbooks/fastapi-tutorial/recipes/default.rb
```

**Providers:**
```text
```

No custom resources or provider files are shown.

**Templates:**
```text
```

No `.erb` templates are shown. Configuration is written using inline Chef `file` resources.

**Attributes:**
```text
```

No attribute files are shown.

**Files:**
```text
```

No static files deployed by `cookbook_file` or `remote_file` are shown.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the packages `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev` through one Chef `package` resource.
   - Creates `/opt/fastapi-tutorial` with mode `0755`.
   - Synchronizes the configured Git repository into `/opt/fastapi-tutorial`. The repository URL, branch, tag, commit, and credentials are not exposed in the execution analysis and must be obtained from the recipe or deployment variables.
   - Runs `python3 -m venv /opt/fastapi-tutorial/venv`.
   - Runs `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt`.
   - Enables and starts the `postgresql` service.
   - Executes PostgreSQL commands as the `postgres` operating-system user to create the `fastapi` user, create the `fastapi_db` database owned by `fastapi`, and grant all privileges on `fastapi_db` to `fastapi`. Each command uses `|| true`, so failures are ignored.
   - Creates `/opt/fastapi-tutorial/.env` with mode `0644` using inline content. The complete content is not exposed in the analysis and must be obtained from the recipe.
   - Creates `/etc/systemd/system/fastapi-tutorial.service` with mode `0644` using inline content. The exact `ExecStart`, user, working directory, environment handling, restart policy, and application port are not exposed.
   - Declares `execute[systemd_reload]` with `systemctl daemon-reload` and `action: nothing`. The analysis does not show a notification, subscription, or other trigger, so this Chef resource does not run based on the supplied execution data.
   - Enables and starts the `fastapi-tutorial` service after the unit resource is declared.
   - Iterations: None. No `.each` loops are present in the analyzed recipe.

For the Ansible migration:

- Use `ansible.builtin.package` for the complete package list.
- Use `ansible.builtin.file` for `/opt/fastapi-tutorial`.
- Use `ansible.builtin.git` with the exact repository URL and revision from the Chef recipe.
- Create the virtual environment idempotently, checking for `/opt/fastapi-tutorial/venv/bin/python`.
- Prefer `ansible.builtin.pip` with the requirements file and virtual environment.
- Use `ansible.builtin.service` or `ansible.builtin.systemd` to enable and start PostgreSQL.
- Use `community.postgresql.postgresql_user`, `community.postgresql.postgresql_db`, and `community.postgresql.postgresql_privs` for database initialization.
- Use `ansible.builtin.copy` for the inline `.env` and systemd unit content after obtaining the complete Chef content.
- Because the Chef reload resource has no demonstrated trigger, adding an Ansible systemd daemon-reload handler and ensuring it runs before starting `fastapi-tutorial` is an intentional migration design improvement, not behavior confirmed from the original execution analysis.
- Use `ansible.builtin.systemd` with `enabled: true` and `state: started` for `fastapi-tutorial` after the daemon reload has been performed.

## Dependencies

**External cookbook dependencies**: None listed in the supplied execution analysis.

**System package dependencies**:

- `python3`
- `python3-pip`
- `python3-venv`
- `git`
- `postgresql`
- `postgresql-contrib`
- `libpq-dev`

**Python dependency source**:

- `/opt/fastapi-tutorial/requirements.txt`
- Installed into `/opt/fastapi-tutorial/venv`

**Service dependencies**:

- `postgresql` must be enabled and started before database initialization.
- `fastapi-tutorial` depends on the application source, virtual environment, installed Python dependencies, `.env` file, and systemd unit.
- The application port is not specified.
- The `community.postgresql` Ansible collection is required for idempotent database management.

## Credentials

**Detection Summary**: 1 explicitly detected hardcoded credential in 1 analyzed file. The inline `.env` content may contain additional sensitive values, but its complete content was not exposed.

**Source**:
  - **Provider**: Hardcoded and inline Chef configuration
  - **URL**: Not applicable
  - **Path**: `cookbooks/fastapi-tutorial/recipes/default.rb`

### PostgreSQL password for the `fastapi` database user

- **Variable(s)**: Hardcoded password literal `fastapi_password`; migration variable should be `fastapi_db_password`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the `execute[create_db_user]` shell command
- **Usage context**: PostgreSQL authentication for user `fastapi`, which owns the `fastapi_db` database
- **Migration handling**: Store `fastapi_db_password` in Ansible Vault or an AAP credential, pass it to `community.postgresql.postgresql_user`, and use `no_log: true` where appropriate

### Application environment configuration

- **Variable(s)**: Not exposed by the supplied analysis
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Inline content written to `/opt/fastapi-tutorial/.env`
- **Usage context**: Runtime configuration for the FastAPI application
- **Migration handling**: Inspect the complete Chef content before migration. Treat database URLs, passwords, tokens, API keys, and other sensitive values as secrets and move them to Ansible Vault or an AAP credential. The original mode is `0644`; use `0600` unless compatibility requires preserving the original mode.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Database objects to verify**:

- PostgreSQL user `fastapi`
- PostgreSQL database `fastapi_db`
- Owner of `fastapi_db`: `fastapi`
- All privileges for `fastapi` on `fastapi_db`

**Service endpoints to check**:

- PostgreSQL instance `postgresql`: platform-configured port, normally `5432`
- FastAPI instance `fastapi-tutorial`: port must be determined from the systemd unit or application configuration
- Unix sockets: none specified

**Templates rendered**:

- None; no templates are present or rendered
- Inline file resources: `/opt/fastapi-tutorial/.env` rendered once and `/etc/systemd/system/fastapi-tutorial.service` rendered once

## Pre-flight checks:

```bash
# Verify required packages for the postgresql instance and fastapi-tutorial instance
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

# Verify the fastapi-tutorial application directory
stat -c '%A %U:%G %n' /opt/fastapi-tutorial

# Verify the Git checkout and requirements file
git -C /opt/fastapi-tutorial status --short
test -f /opt/fastapi-tutorial/requirements.txt

# Verify the fastapi-tutorial virtual environment
test -x /opt/fastapi-tutorial/venv/bin/python
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip --version
/opt/fastapi-tutorial/venv/bin/pip check

# Verify the fastapi-tutorial environment file without exposing its contents
test -f /opt/fastapi-tutorial/.env
stat -c '%A %U:%G %n' /opt/fastapi-tutorial/.env

# Verify the postgresql instance
systemctl status postgresql --no-pager
systemctl is-enabled postgresql
systemctl is-active postgresql
ss -ltnp | grep ':5432'

# Verify the fastapi PostgreSQL user
sudo -u postgres psql -tAc \
  "SELECT usename FROM pg_user WHERE usename = 'fastapi';"

# Verify the fastapi_db database and owner
sudo -u postgres psql -tAc \
  "SELECT datname, pg_catalog.pg_get_userbyid(datdba)
   FROM pg_database WHERE datname = 'fastapi_db';"

# Verify fastapi privileges on fastapi_db
sudo -u postgres psql -d fastapi_db -c "\dp"
sudo -u postgres psql -d fastapi_db -c \
  "SELECT has_database_privilege('fastapi', 'fastapi_db', 'CONNECT');"

# Verify the fastapi-tutorial systemd unit
test -f /etc/systemd/system/fastapi-tutorial.service
stat -c '%A %U:%G %n' /etc/systemd/system/fastapi-tutorial.service
systemctl cat fastapi-tutorial

# Verify the systemd unit configuration
grep -E 'ExecStart|Environment|WorkingDirectory|User' \
  /etc/systemd/system/fastapi-tutorial.service

# Perform the migration-intended daemon reload before starting fastapi-tutorial
systemctl daemon-reload

# Verify the fastapi-tutorial instance
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl status fastapi-tutorial --no-pager
systemctl show fastapi-tutorial \
  --property=ExecMainPID,ActiveState,SubState,User,WorkingDirectory

# Verify the FastAPI process
ps aux | grep '[f]astapi'

# Determine and verify the FastAPI port
# Replace <FASTAPI_PORT> with the value found in the systemd unit or application configuration.
ss -ltnp | grep ':<FASTAPI_PORT>'
curl -i http://127.0.0.1:<FASTAPI_PORT>/

# Review FastAPI service logs
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u fastapi-tutorial -p err --no-pager

# Confirm Python packages were installed
/opt/fastapi-tutorial/venv/bin/pip list

# Check configuration references without printing secret values
grep -E '^(DATABASE|DB_|POSTGRES)' /opt/fastapi-tutorial/.env \
  | sed -E 's/(PASSWORD|PASS|SECRET|TOKEN)=.*/\1=[REDACTED]/'
```