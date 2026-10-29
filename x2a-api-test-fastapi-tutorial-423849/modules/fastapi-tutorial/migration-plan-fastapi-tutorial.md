---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys one FastAPI application under `/opt/fastapi-tutorial` with PostgreSQL as its database dependency. It installs Python, Git, PostgreSQL, PostgreSQL development libraries, and related packages; synchronizes application source; creates a Python virtual environment; installs `requirements.txt`; creates the PostgreSQL role and database; creates an application environment file and systemd unit; reloads systemd when required; and enables and starts PostgreSQL and the `fastapi-tutorial` service. The application port, repository details, file contents, and resource modes must be confirmed from the original recipe before migration.

## Service Type and Instances

**Service Type**: Application Server with PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application service backed by PostgreSQL
  - Location/Path: `/opt/fastapi-tutorial`
  - Port/Socket: Not specified in the execution tree; determine from the systemd unit or application configuration
  - Key Config:
    - Virtual environment: `/opt/fastapi-tutorial/venv`
    - Requirements file: `/opt/fastapi-tutorial/requirements.txt`
    - Environment file: `/opt/fastapi-tutorial/.env`
    - systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
    - Application service: `fastapi-tutorial`
    - Database service: `postgresql`
    - Database name: `fastapi_db`
    - Database owner/user: `fastapi`
    - Database password: `fastapi_password`
    - Application port and bind address: Not specified
    - Directory and file modes: Identified in the original plan as `0755` and `0644`, respectively, but not verified by the structured analysis

No multiple application instances or `.each` iterations are configured.

## File Structure

Only files shown as executed or referenced by the supplied execution tree are listed.

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

The `.env` file and systemd unit are created dynamically by recipe resources if confirmed by the original recipe. Their inline content or heredoc implementation is not present in the structured execution tree.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the following seven system packages:
     - `python3`
     - `python3-pip`
     - `python3-venv`
     - `git`
     - `postgresql`
     - `postgresql-contrib`
     - `libpq-dev`
   - Creates `/opt/fastapi-tutorial`; the original plan identifies mode `0755`, but the mode requires confirmation from the original recipe.
   - Synchronizes the Git repository into `/opt/fastapi-tutorial`.
   - Requires the repository URL, branch, tag, revision, and Git authentication details to be obtained from the original recipe; none are specified in the execution tree.
   - Creates the virtual environment with:
     ```bash
     python3 -m venv /opt/fastapi-tutorial/venv
     ```
   - Installs Python dependencies from `/opt/fastapi-tutorial/requirements.txt` using:
     ```bash
     /opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt
     ```
   - Enables and starts the `postgresql` service.
   - Creates PostgreSQL role `fastapi` with password `fastapi_password`.
   - Creates database `fastapi_db` owned by `fastapi`.
   - Grants all privileges on `fastapi_db` to `fastapi`.
   - Uses shell commands ending in `|| true`, causing failures such as existing roles or databases to be ignored; the migration should use PostgreSQL modules for stronger idempotency.
   - Creates `/opt/fastapi-tutorial/.env`; the destination is known, but its content, heredoc implementation, and mode require confirmation from the original recipe.
   - Creates `/etc/systemd/system/fastapi-tutorial.service`; the destination is known, but its content, heredoc implementation, mode, `ExecStart`, working directory, user, environment handling, restart policy, and listening port require confirmation from the original recipe.
   - Declares `execute[systemd_reload]` with `systemctl daemon-reload` and action `nothing`. No notification relationship is shown in the supplied execution tree.
   - Enables and starts the `fastapi-tutorial` service after the application files and systemd unit are deployed.
   - There are no `include_recipe` calls, providers, attributes, static files, Chef templates, or `.each` loops shown.

## Dependencies

**External cookbook dependencies**: None shown

**System package dependencies**:
- `python3`
- `python3-pip`
- `python3-venv`
- `git`
- `postgresql`
- `postgresql-contrib`
- `libpq-dev`

**Service dependencies**:
- `postgresql`: must be enabled and started before PostgreSQL role and database initialization
- `fastapi-tutorial`: must start after application source, the virtual environment, `.env`, and the systemd unit are deployed

**Execution dependency chain**:
1. Install system packages.
2. Create `/opt/fastapi-tutorial`.
3. Synchronize application source.
4. Create `/opt/fastapi-tutorial/venv`.
5. Install `/opt/fastapi-tutorial/requirements.txt`.
6. Enable and start `postgresql`.
7. Create PostgreSQL role `fastapi`.
8. Create database `fastapi_db` owned by `fastapi`.
9. Grant privileges on `fastapi_db` to `fastapi`.
10. Create `/opt/fastapi-tutorial/.env`.
11. Create `/etc/systemd/system/fastapi-tutorial.service`.
12. Reload systemd when the unit changes.
13. Enable and start `fastapi-tutorial`.

## Credentials

**Detection Summary**: 1 hardcoded database credential detected in 1 file

**Source**:
  - **Provider**: Hardcoded in Chef; no external secrets provider detected
  - **URL**: Not applicable
  - **Path**: `cookbooks/fastapi-tutorial/recipes/default.rb`

### PostgreSQL Password

- **Variable(s)**: No named variable is shown; the literal `fastapi_password` is embedded in the database command
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded plaintext in `execute[create_db_user]`
- **Usage context**: Password for PostgreSQL role `fastapi`, used with database `fastapi_db`
- **Migration handling**: Store the password in Ansible Vault and pass it to `community.postgresql.postgresql_user`

The contents of `/opt/fastapi-tutorial/.env` and `/etc/systemd/system/fastapi-tutorial.service` are not present in the structured analysis. Inspect both files for additional credentials, database URLs, tokens, `Environment`, and `EnvironmentFile` entries before finalizing the migration.

## Checks for the Migration

**Files to verify**:
- `cookbooks/fastapi-tutorial/recipes/default.rb`
- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Database objects to verify**:
- PostgreSQL role `fastapi`
- PostgreSQL database `fastapi_db`
- Database owner `fastapi`
- Privileges granted to `fastapi` on `fastapi_db`

**Service endpoints to check**:
- `postgresql` service
- `fastapi-tutorial` service
- Application port: not specified; determine it from the systemd unit or application configuration
- Unix sockets: none specified
- Network bind address: not specified

**Templates rendered**:
- Chef templates: none
- `/opt/fastapi-tutorial/.env`: one file resource, with inline content or heredoc implementation requiring confirmation
- `/etc/systemd/system/fastapi-tutorial.service`: one file resource, with inline content or heredoc implementation requiring confirmation

## Pre-flight checks:

```bash
# Verify all required packages for the fastapi-tutorial instance
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

# Verify the fastapi-tutorial application layout
test -d /opt/fastapi-tutorial
stat -c '%A %n' /opt/fastapi-tutorial
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -f /opt/fastapi-tutorial/requirements.txt
test -f /opt/fastapi-tutorial/.env

# Verify the PostgreSQL dependency for fastapi-tutorial
systemctl status postgresql --no-pager
systemctl is-enabled postgresql
systemctl is-active postgresql

# Verify PostgreSQL role and database for fastapi-tutorial
sudo -u postgres psql -d postgres -c "\du fastapi"
sudo -u postgres psql -d postgres -c "\l fastapi_db"
sudo -u postgres psql -d fastapi_db -c "SELECT current_database();"
sudo -u postgres psql -d fastapi_db -c "SELECT current_user;"

# Verify the fastapi-tutorial systemd unit
systemctl daemon-reload
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
test -f /etc/systemd/system/fastapi-tutorial.service
cat /etc/systemd/system/fastapi-tutorial.service

# Verify the fastapi-tutorial service
systemctl status fastapi-tutorial --no-pager
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl show fastapi-tutorial \
  --property=ExecStart,Environment,EnvironmentFile,WorkingDirectory

# Verify logs for the fastapi-tutorial instance and PostgreSQL
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u postgresql --no-pager -n 100

# Identify the configured application endpoint
systemctl show fastapi-tutorial --property=ExecStart
grep -E 'ExecStart|Environment|EnvironmentFile' \
  /etc/systemd/system/fastapi-tutorial.service

# Confirm the listening port after identifying it from the deployed configuration
ss -tlnp

# Run this only after confirming the exact configured port and endpoint
curl -f http://127.0.0.1:<CONFIRMED_PORT>/
```

Verify that `fastapi-tutorial` is enabled and active, its `ExecStart` uses the intended virtual environment or application command, its working directory is correct, and its environment configuration references the expected `.env` file if applicable.