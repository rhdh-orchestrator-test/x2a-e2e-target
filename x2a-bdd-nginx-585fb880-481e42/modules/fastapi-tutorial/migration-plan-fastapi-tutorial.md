---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook provisions the `fastapi-tutorial` FastAPI application under `/opt/fastapi-tutorial`, installs Python, virtual-environment, Git, PostgreSQL, PostgreSQL development packages, synchronizes application source, creates a Python virtual environment, installs `requirements.txt`, creates the PostgreSQL `fastapi` role and `fastapi_db` database, writes the application `.env` file, installs a systemd unit, and enables and starts PostgreSQL and `fastapi-tutorial`. The FastAPI port is not available in the supplied execution analysis and must be obtained from the systemd unit or application configuration. The migration deliberately reloads systemd before starting the application so the newly installed unit is recognized; this is an intentional improvement over the analyzed Chef behavior, where `execute[systemd_reload]` has `action: nothing` and no notification relationship.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application server
  - Location/Path: `/opt/fastapi-tutorial`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Dependency file: `/opt/fastapi-tutorial/requirements.txt`
  - Environment file: `/opt/fastapi-tutorial/.env`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Service actions: Enable and start
  - Source management: Git synchronization into `/opt/fastapi-tutorial`
  - Port/Socket: Not specified in the supplied execution analysis; obtain it from the rendered systemd unit or application configuration
  - Key configuration: Python virtual environment, `requirements.txt`, inline `.env`, and inline systemd service definition

- **postgresql**: PostgreSQL database service
  - Location/Path: Platform-default PostgreSQL installation and data directory
  - Port/Socket: Not explicitly configured by the cookbook; verify the target platform configuration and PostgreSQL default
  - Service actions: Enable and start
  - Database role: `fastapi`
  - Database password: `fastapi_password`
  - Database name: `fastapi_db`
  - Database owner: `fastapi`
  - Database privileges: `fastapi` receives all privileges on `fastapi_db`

## File Structure

**Recipes:**
```text
cookbooks/fastapi-tutorial/recipes/default.rb
```

**Providers:**
```text
```

No custom Chef providers or custom resources are present in the execution tree.

**Templates:**
```text
```

No ERB templates are present. The `.env` file and systemd unit are created with inline Chef `file` resources.

**Attributes:**
```text
```

No attribute files are present in the supplied directory listing or execution analysis.

**Files:**
```text
```

No static files deployed by `cookbook_file` or `remote_file` are present.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the seven system packages `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Creates `/opt/fastapi-tutorial` with mode `0755`.
   - Synchronizes the Git repository into `/opt/fastapi-tutorial`.
   - The supplied execution analysis does not expose the repository URL, revision, branch, or ownership settings; these values must be obtained from the original recipe or deployment variables.
   - Creates the virtual environment with:
     ```bash
     python3 -m venv /opt/fastapi-tutorial/venv
     ```
   - Installs Python dependencies from `/opt/fastapi-tutorial/requirements.txt` using `/opt/fastapi-tutorial/venv/bin/pip`.
   - Enables and starts the `postgresql` service.
   - Creates the PostgreSQL role `fastapi` with password `fastapi_password`.
   - Creates the PostgreSQL database `fastapi_db` owned by `fastapi`.
   - Grants all privileges on `fastapi_db` to `fastapi`.
   - Creates `/opt/fastapi-tutorial/.env` with mode `0644` and inline Chef content. The exact content is not exposed in the supplied analysis and must be preserved from the original recipe.
   - Creates `/etc/systemd/system/fastapi-tutorial.service` with mode `0644` and inline Chef content. The exact unit content is not exposed and must be retrieved from the original recipe.
   - The unit must preserve its original `ExecStart`, working directory, user and group, environment-file reference, restart policy, bind address, application port, and resource limits.
   - Deliberately reloads systemd after installing or changing `/etc/systemd/system/fastapi-tutorial.service`. This is an intentional migration improvement because the analyzed Chef `execute[systemd_reload]` resource uses `action: nothing` and has no shown notification relationship.
   - Enables and starts the `fastapi-tutorial` systemd service after the application source, virtual environment, dependencies, PostgreSQL service, database objects, `.env` file, and systemd unit are available.

### Expanded package items

The package resource contains these seven concrete package names:

- `python3`
- `python3-pip`
- `python3-venv`
- `git`
- `postgresql`
- `postgresql-contrib`
- `libpq-dev`

No `.each` loops or collection iterations are present. There are no additional application instances, sites, database collections, or service-instance loops to expand.

## Dependencies

**External cookbook dependencies**: None listed in the supplied metadata analysis.

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

The `fastapi-tutorial` service depends operationally on PostgreSQL being started and on the `fastapi` role and `fastapi_db` database being available.

## Credentials

**Detection Summary**: One hardcoded database credential is explicitly confirmed in `cookbooks/fastapi-tutorial/recipes/default.rb`. The inline `.env` content is not exposed, so additional credentials may exist there but cannot be confirmed from the supplied analysis.

**Source**:
  - **Provider**: Hardcoded in the Chef recipe
  - **URL**: None detected
  - **Path**: PostgreSQL role `fastapi`

### PostgreSQL password for the `fastapi` role

- **Variable(s)**: Password literal `fastapi_password`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the `execute[create_db_user]` command
- **Usage context**: Sets the password for PostgreSQL role `fastapi`, which owns the `fastapi_db` database
- **Migration handling**: Store the value in Ansible Vault, such as a vaulted variable named `fastapi_db_password`; do not retain the literal in plaintext task files

### Application `.env` credentials

- **Variable(s)**: Not identifiable from the supplied analysis
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Inline content in `file[/opt/fastapi-tutorial/.env]`
- **Usage context**: Application environment configuration that may contain database connection details or other secrets
- **Migration handling**: Inspect the original inline content and move sensitive values into Ansible Vault before creating `/opt/fastapi-tutorial/.env`

No Chef data bags, encrypted data bags, Chef Vault calls, CyberArk integration, Conjur calls, or explicit TLS certificate references are shown in the supplied execution tree.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Service endpoints to check**:

- `fastapi-tutorial`: Application port is not available in the supplied execution analysis; obtain it from `/etc/systemd/system/fastapi-tutorial.service` or application configuration
- `postgresql`: Port is not explicitly configured by this cookbook; verify the target PostgreSQL configuration before testing

**Database objects to verify**:

- PostgreSQL role `fastapi`
- PostgreSQL database `fastapi_db`
- Database owner `fastapi`
- All intended privileges for `fastapi` on `fastapi_db`

**Templates rendered**:

- No ERB templates rendered
- `/opt/fastapi-tutorial/.env`: created once by an inline Chef `file` resource
- `/etc/systemd/system/fastapi-tutorial.service`: created once by an inline Chef `file` resource

## Pre-flight checks

```bash
# Verify required system packages
if command -v dpkg >/dev/null 2>&1; then
  dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev
else
  rpm -q python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev
fi

# Verify the fastapi-tutorial application instance
ls -ld /opt/fastapi-tutorial
ls -ld /opt/fastapi-tutorial/venv
test -f /opt/fastapi-tutorial/requirements.txt
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -f /opt/fastapi-tutorial/.env
stat -c '%a %n' /opt/fastapi-tutorial/.env

/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip check
/opt/fastapi-tutorial/venv/bin/pip freeze

# Avoid exposing secrets while checking the environment file
grep -vE 'PASSWORD|SECRET|TOKEN|KEY' /opt/fastapi-tutorial/.env

# Verify the PostgreSQL instance
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql

sudo -u postgres psql -tAc \
  "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"

sudo -u postgres psql -tAc \
  "SELECT datname, pg_catalog.pg_get_userbyid(datdba)
   FROM pg_database WHERE datname = 'fastapi_db';"

sudo -u postgres psql -d fastapi_db -tAc \
  "SELECT current_database(), current_user;"

sudo -u postgres psql -d fastapi_db -c "\l+ fastapi_db"

# Verify the fastapi-tutorial systemd unit
test -f /etc/systemd/system/fastapi-tutorial.service
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl daemon-reload
systemctl cat fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl status fastapi-tutorial

grep -E '^(ExecStart|WorkingDirectory|User|Group|Environment|EnvironmentFile|Restart)=' \
  /etc/systemd/system/fastapi-tutorial.service

# Identify the configured FastAPI port before running endpoint checks
grep -Eo -- '--(host|port)[= ]+[0-9.]+' \
  /etc/systemd/system/fastapi-tutorial.service || true

# Replace <FASTAPI_PORT> with the port found in the systemd unit or application configuration
curl -i "http://127.0.0.1:<FASTAPI_PORT>/"
curl -i "http://127.0.0.1:<FASTAPI_PORT>/docs"
curl -i "http://127.0.0.1:<FASTAPI_PORT>/openapi.json"
ss -tlnp | grep ":<FASTAPI_PORT>"

# Verify service logs
journalctl -u postgresql --no-pager -n 100
journalctl -u fastapi-tutorial --no-pager -n 100
```

Use an Ansible Vault-provided credential or another protected mechanism when testing PostgreSQL password authentication. Do not place the password in shell history or shared logs.