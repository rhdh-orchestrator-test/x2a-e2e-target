---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys a FastAPI application from a Git repository into `/opt/fastapi-tutorial`. It installs Python, PostgreSQL, Git, PostgreSQL development dependencies, and application requirements; creates a Python virtual environment; initializes the PostgreSQL role and database; writes an application `.env` file; installs a systemd unit; and enables and starts PostgreSQL and the FastAPI application service. One recipe is executed, and no `.each` loops or collection iterations are present.

## Service Type and Instances

**Service Type**: Application Server with PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application service
  - Location/Path: `/opt/fastapi-tutorial`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Dependency file: `/opt/fastapi-tutorial/requirements.txt`
  - Environment file: `/opt/fastapi-tutorial/.env`
  - systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Service actions: Enabled and started
  - Port/Socket: Not specified in the execution tree. Obtain the port from the systemd unit or application configuration before implementation and validation.
  - Key Config: Repository details, service command, working directory, service user, environment reference, restart policy, and network binding require confirmation from the recipe, repository, or deployed unit.

- **postgresql**: PostgreSQL database service supporting the FastAPI application
  - Service name: `postgresql`
  - Service actions: Enabled and started
  - Database user: `fastapi`
  - Database password: `fastapi_password`
  - Database name: `fastapi_db`
  - Database owner: `fastapi`
  - Privileges: `fastapi` receives all privileges on `fastapi_db`
  - Port/Socket: Not specified in the execution tree. Verify the target system's PostgreSQL configuration and defaults.

**Iterations**: No `.each` loops or collection iterations are present in the execution tree.

## File Structure

The execution tree contains one recipe file. No provider, template, attribute, or static file paths are listed in the supplied analysis.

**Recipes:**
```text
recipes/default.rb
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

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the system packages `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev` using a Chef package resource.
   - Creates `/opt/fastapi-tutorial` using `directory[/opt/fastapi-tutorial]`. The directory mode is reported as `0755`; ownership and group values require confirmation from the recipe source.
   - Synchronizes a Git repository into `/opt/fastapi-tutorial` using `git[/opt/fastapi-tutorial]` with action `sync`. The repository URL, branch, revision, and authentication settings are not present in the supplied execution tree and must be read from the recipe before migration.
   - Creates the Python virtual environment with `execute[create_venv]`:
     ```bash
     python3 -m venv /opt/fastapi-tutorial/venv
     ```
   - Installs Python dependencies with `execute[install_dependencies]`:
     ```bash
     /opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt
     ```
     The Ansible equivalent should use `ansible.builtin.pip` with the requirements file and virtual environment after the Git checkout and virtual environment creation.
   - Enables and starts `postgresql` using `service[postgresql]` with actions `enable` and `start`.
   - Creates the PostgreSQL role and database with `execute[create_db_user]`:
     ```bash
     sudo -u postgres psql -c "CREATE USER fastapi WITH PASSWORD 'fastapi_password';" || true
     sudo -u postgres psql -c "CREATE DATABASE fastapi_db OWNER fastapi;" || true
     sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE fastapi_db TO fastapi;" || true
     ```
     The commands suppress failures with `|| true` and are not fully idempotent. Use `community.postgresql.postgresql_user`, `community.postgresql.postgresql_db`, and, if required, `community.postgresql.postgresql_privs` in Ansible.
   - Deploys `/opt/fastapi-tutorial/.env` using `file[/opt/fastapi-tutorial/.env]`. The execution tree does not provide its content, mode, owner, or group; these values must be confirmed from the recipe. Any credentials in the file must be stored securely in Ansible Vault.
   - Deploys `/etc/systemd/system/fastapi-tutorial.service` using `file[/etc/systemd/system/fastapi-tutorial.service]`. The execution tree does not provide its content, mode, owner, or group. Confirm the exact `ExecStart`, working directory, service user, environment file, restart policy, dependencies, network binding, port, and resource limits before migration.
   - Defines `execute[systemd_reload]` with command `systemctl daemon-reload` and action `nothing`. The execution tree does not show a notification relationship, so this resource is not automatically executed unless notified by another resource.
   - Enables and starts `fastapi-tutorial` using `service[fastapi-tutorial]` with actions `enable` and `start`.
   - No `.each` loops or collection iterations require expansion.

## Dependencies

**External cookbook dependencies**: None are listed in the supplied execution tree or directory analysis. The detailed contents of `metadata.rb` were not provided.

**System package dependencies**: `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, `libpq-dev`

**Service dependencies**: `postgresql`, `fastapi-tutorial`

**Application dependency source**: `/opt/fastapi-tutorial/requirements.txt`

## Credentials

**Detection Summary**: 1 explicit credential detected across 1 analyzed recipe file. The `.env` content is unavailable and may contain additional credentials that require inspection.

**Source**:
  - **Provider**: Hardcoded in Chef command
  - **URL**: None detected
  - **Path**: PostgreSQL database `fastapi_db`

### PostgreSQL database password

- **Variable(s)**: No variable name is shown; the literal value is `fastapi_password`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded plaintext in the `execute[create_db_user]` command
- **Usage context**: Password assigned to PostgreSQL role `fastapi`
- **Migration handling**: Store the value in Ansible Vault, reference it through a vaulted variable, and prevent it from appearing in task output.

### Potential `.env` credentials

- **Variable(s)**: Not available in the supplied execution tree
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Content embedded in a Chef `file` resource
- **Usage context**: FastAPI application environment configuration
- **Migration handling**: Inspect the recipe and classify all passwords, tokens, API keys, database URLs, and other secrets before migration.

No data bags, encrypted data bags, Chef Vault calls, CyberArk integrations, Conjur calls, or external secret-manager references are shown in the supplied analysis.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/venv/bin/python`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Database objects to verify**:

- PostgreSQL role `fastapi`
- PostgreSQL database `fastapi_db`
- Owner of `fastapi_db`: `fastapi`
- All privileges on `fastapi_db` granted to `fastapi`

**Service endpoints to check**:

- **fastapi-tutorial**: Port is not specified in the execution tree. Obtain it from `/etc/systemd/system/fastapi-tutorial.service` or the application configuration.
- **postgresql**: Port and socket are not specified in the execution tree. Verify the target PostgreSQL configuration.

**Templates rendered**: None. No `.erb` templates are listed. The `.env` file and systemd unit are deployed by Chef `file` resources with inline content.

## Pre-flight checks

```bash
# Verify required packages
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

# On RPM-based systems, use the equivalent package query command.

# Verify the FastAPI application instance
ls -ld /opt/fastapi-tutorial
test -f /opt/fastapi-tutorial/requirements.txt
test -x /opt/fastapi-tutorial/venv/bin/python
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip check
systemctl status fastapi-tutorial
systemctl is-enabled fastapi-tutorial
journalctl -u fastapi-tutorial --no-pager -n 100

# Verify the application environment and systemd unit
stat -c '%a %U %G %n' /opt/fastapi-tutorial/.env
stat -c '%a %U %G %n' /etc/systemd/system/fastapi-tutorial.service
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl daemon-reload
grep -E '^(User|WorkingDirectory|Environment|EnvironmentFile|ExecStart|Restart|After|Requires)=' \
  /etc/systemd/system/fastapi-tutorial.service

# Determine and check the FastAPI listening port
grep -Eo -- '--(host|port)[= ][^ ]+' /etc/systemd/system/fastapi-tutorial.service
grep -E 'listen|bind|port|uvicorn|gunicorn' /etc/systemd/system/fastapi-tutorial.service
ss -tlnp

# Verify the PostgreSQL instance
systemctl status postgresql
systemctl is-enabled postgresql
sudo -u postgres psql -c "SELECT version();"
sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname = 'fastapi';"
sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname = 'fastapi_db';"
sudo -u postgres psql -tAc "SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"
sudo -u postgres psql -d fastapi_db -c "\du fastapi"
sudo -u postgres psql -d fastapi_db -c "SELECT current_database(), current_user;"
sudo -u postgres psql -tAc "SHOW port;"
sudo -u postgres psql -tAc "SHOW unix_socket_directories;"
```

The PostgreSQL role check must find `fastapi`; the database check must find `fastapi_db`; and the owner query must return `fastapi`. Confirm the FastAPI port and health endpoint from the deployed systemd unit or application source before running an application-specific `curl` check.