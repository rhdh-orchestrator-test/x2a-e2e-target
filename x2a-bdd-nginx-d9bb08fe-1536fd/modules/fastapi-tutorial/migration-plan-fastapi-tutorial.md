---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys one FastAPI application instance, `fastapi-tutorial`, under `/opt/fastapi-tutorial` as a systemd-managed service. It installs Python, Git, PostgreSQL, and PostgreSQL development packages; synchronizes application source; creates a Python virtual environment; installs dependencies from `requirements.txt`; creates the PostgreSQL role and database; writes an application `.env` file and systemd unit; and enables and starts PostgreSQL and the FastAPI service. The PostgreSQL password is currently hardcoded in the Chef recipe and must be migrated to Ansible Vault or an approved AAP-managed credential. The FastAPI listen address, port, and systemd unit details must be confirmed from the original recipe before implementation.

## Service Type and Instances

**Service Type**: Application Server

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application server managed by systemd
  - Application directory: `/opt/fastapi-tutorial`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Dependency file: `/opt/fastapi-tutorial/requirements.txt`
  - Environment file: `/opt/fastapi-tutorial/.env`
  - systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Managed service: `fastapi-tutorial`
  - Database: `fastapi_db`
  - Database user: `fastapi`
  - PostgreSQL service: `postgresql`
  - Listen address and port: Not specified in the execution tree
  - Unix socket: None specified in the execution tree

No collection attributes or `.each` iterations are present. The cookbook configures exactly one application instance named `fastapi-tutorial`.

Ownership, group, and file modes are not available in the structured analysis and must be confirmed from the original Chef recipe before migration.

## File Structure

Only the recipe file shown in the execution tree is included.

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

No provider, template, attribute, or static cookbook file is shown as used by the execution tree. The `.env` file and systemd unit are generated inline by Chef `file` resources rather than rendered from `.erb` templates.

## Module Explanation

The cookbook performs operations in the following exact order:

1. **`default`** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the following system packages:
     - `python3`
     - `python3-pip`
     - `python3-venv`
     - `git`
     - `postgresql`
     - `postgresql-contrib`
     - `libpq-dev`
   - Uses the packages for the Python runtime, pip, virtual environments, Git synchronization, PostgreSQL server/client functionality, PostgreSQL extensions, and Python database-driver development libraries.
   - Creates `/opt/fastapi-tutorial`; ownership, group, and mode require confirmation from the original recipe.
   - Synchronizes application source into `/opt/fastapi-tutorial` using `git[/opt/fastapi-tutorial]` with action `sync`.
   - Preserves the repository URL, revision, branch, and checkout user from the original recipe; these values are not present in the execution tree.
   - Creates the virtual environment with:
     ```bash
     python3 -m venv /opt/fastapi-tutorial/venv
     ```
   - Installs Python dependencies with:
     ```bash
     /opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt
     ```
   - Starts and enables the `postgresql` service.
   - Executes PostgreSQL commands as the `postgres` operating-system user to create:
     - Role: `fastapi`
     - Database: `fastapi_db`
     - Database owner: `fastapi`
     - Privileges: all privileges on `fastapi_db` for `fastapi`
   - The original database commands end with `|| true`, suppressing existing-object errors and unrelated command failures. Replace these commands with idempotent PostgreSQL Ansible modules.
   - Writes `/opt/fastapi-tutorial/.env` using an inline Chef `file` resource. Its exact contents and mode require confirmation from the original recipe.
   - Writes `/etc/systemd/system/fastapi-tutorial.service` using an inline Chef `file` resource. Its exact contents and mode require confirmation from the original recipe.
   - The systemd unit must be checked for:
     - `ExecStart`
     - `WorkingDirectory`
     - Service user and group
     - Environment file usage
     - Listen address and port
     - Restart policy
     - PostgreSQL ordering dependencies
     - `WantedBy` target
     - Resource limits
   - Defines `execute[systemd_reload]` with command `systemctl daemon-reload` and action `nothing`. The execution tree does not show a notification relationship, so it does not run during normal convergence unless explicitly triggered.
   - Enables and starts the `fastapi-tutorial` service.
   - No `.each` loops, custom resources, recipe includes, or rendered templates are present.

## Dependencies

**External cookbook dependencies**: Not specified in the supplied metadata analysis.

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

**Application dependency source**:

```text
/opt/fastapi-tutorial/requirements.txt
```

The Python packages and versions are supplied by the checked-out application source and are not listed in the execution tree.

## Credentials

**Detection Summary**: 1 explicitly detected hardcoded credential, plus database identity values used in PostgreSQL setup commands.

**Source**:

- **Provider**: Hardcoded in Chef recipe
- **URL**: None detected
- **Path**: None detected
- **Secret management integration**: No Chef data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, or external secret manager references are shown.

### PostgreSQL password

- **Variable(s)**: Proposed Ansible variable `fastapi_db_password`; no named Chef variable exists
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded plaintext literal `'fastapi_password'` in the `execute[create_db_user]` command
- **Usage context**: Password for PostgreSQL user `fastapi`, used to access database `fastapi_db`
- **Migration handling**: Store the value in Ansible Vault or an approved AAP-managed credential. Do not reproduce the plaintext value in the Ansible playbook.

### PostgreSQL database identity

- **Variable(s)**:
  - `fastapi_db_user`: `fastapi`
  - `fastapi_db_name`: `fastapi_db`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded command arguments
- **Usage context**: Creates the PostgreSQL role and application database, assigns database ownership, grants privileges, and supplies application connection identity values
- **Sensitivity**: These are not passwords but must remain consistent with the `.env` file and systemd service configuration.

The `.env` inline content was not included in the supplied analysis and may contain additional credentials. Inspect the original Chef recipe before finalizing the Ansible secret inventory.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/venv/bin/python`
- `/opt/fastapi-tutorial/venv/bin/pip`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Database objects to verify**:

- PostgreSQL role `fastapi`
- PostgreSQL database `fastapi_db`
- Owner of `fastapi_db`: `fastapi`
- All privileges for `fastapi` on `fastapi_db`

**Service endpoints to check**:

- `fastapi-tutorial` FastAPI port: Not specified in the execution tree; extract it from the systemd unit or application configuration
- `fastapi-tutorial` bind address: Not specified in the execution tree
- `fastapi-tutorial` Unix socket: None specified
- PostgreSQL port: Normally `5432`; not explicitly configured by the cookbook

**Templates rendered**:

No `.erb` templates are listed or rendered.

- `/opt/fastapi-tutorial/.env`: generated once by an inline Chef `file` resource
- `/etc/systemd/system/fastapi-tutorial.service`: generated once by an inline Chef `file` resource

## Pre-flight checks

### Package and Python checks

```bash
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev
python3 --version
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip --version
```

### `fastapi-tutorial` application files and virtual environment

```bash
test -d /opt/fastapi-tutorial
test -f /opt/fastapi-tutorial/requirements.txt
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -f /opt/fastapi-tutorial/.env
stat -c '%A %U:%G %n' /opt/fastapi-tutorial
stat -c '%A %U:%G %n' /opt/fastapi-tutorial/.env
```

Verify the source revision:

```bash
git -C /opt/fastapi-tutorial status
git -C /opt/fastapi-tutorial rev-parse HEAD
```

### Python dependency checks for `fastapi-tutorial`

```bash
/opt/fastapi-tutorial/venv/bin/pip check
/opt/fastapi-tutorial/venv/bin/pip freeze
```

Confirm dependency installation used:

```text
/opt/fastapi-tutorial/requirements.txt
```

### PostgreSQL service checks

```bash
systemctl status postgresql --no-pager
systemctl is-enabled postgresql
systemctl is-active postgresql
```

### PostgreSQL role and database checks

```bash
sudo -u postgres psql -tAc "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"
```

Expected result:

```text
fastapi
```

```bash
sudo -u postgres psql -tAc "SELECT datname, pg_catalog.pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"
```

Expected result:

```text
fastapi_db|fastapi
```

Verify database connectivity using the migrated secret:

```bash
PGPASSWORD='<retrieve-from-Ansible-Vault>' \
psql -h 127.0.0.1 -U fastapi -d fastapi_db -c "SELECT version();"

PGPASSWORD='<retrieve-from-Ansible-Vault>' \
psql -h 127.0.0.1 -U fastapi -d fastapi_db -c "SELECT current_database(), current_user;"
```

Do not store the literal password in shell history or documentation.

### Environment file checks for `fastapi-tutorial`

```bash
test -f /opt/fastapi-tutorial/.env
sed -E 's/(=.*)$/=<redacted>/' /opt/fastapi-tutorial/.env
```

Confirm that the database configuration references:

- User `fastapi`
- Database `fastapi_db`
- The migrated secret source

### systemd unit checks for `fastapi-tutorial`

```bash
test -f /etc/systemd/system/fastapi-tutorial.service
stat -c '%A %U:%G %n' /etc/systemd/system/fastapi-tutorial.service
systemctl cat fastapi-tutorial
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
```

```bash
systemctl show fastapi-tutorial \
  -p LoadState \
  -p ActiveState \
  -p SubState \
  -p ExecStart \
  -p WorkingDirectory \
  -p EnvironmentFiles \
  -p User \
  -p Group
```

### `fastapi-tutorial` service status

```bash
systemctl daemon-reload
systemctl enable fastapi-tutorial
systemctl start fastapi-tutorial
systemctl status fastapi-tutorial --no-pager
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
```

### `fastapi-tutorial` service logs

```bash
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u fastapi-tutorial -p warning --no-pager
```

### `fastapi-tutorial` network verification

Extract the configured endpoint before running a port-specific test:

```bash
systemctl show fastapi-tutorial -p ExecStart
systemctl cat fastapi-tutorial
ss -tlnp
```

After identifying the configured port, test the application:

```bash
curl -i http://127.0.0.1:<configured-fastapi-port>/
```

If the application defines a health endpoint, test the configured path:

```bash
curl -i http://127.0.0.1:<configured-fastapi-port>/<configured-health-endpoint>
```

Do not assume a port, bind address, or health path that is not present in the original application configuration.