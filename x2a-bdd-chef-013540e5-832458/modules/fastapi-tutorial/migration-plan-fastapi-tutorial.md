---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the `fastapi-tutorial` FastAPI application under `/opt/fastapi-tutorial`, synchronizes its source repository, creates a Python virtual environment, installs dependencies from `requirements.txt`, installs and starts PostgreSQL, creates the `fastapi` PostgreSQL user and `fastapi_db` database, writes an inline application environment file, installs a systemd unit, and enables and starts the application. The cookbook contains one recipe and no separate templates, providers, attribute files, or static files.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application service
  - Location/Path: `/opt/fastapi-tutorial`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Dependency file: `/opt/fastapi-tutorial/requirements.txt`
  - Environment file: `/opt/fastapi-tutorial/.env`
  - systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Port/Socket: Not specified in the supplied execution tree; inspect the systemd unit and application configuration after migration.
  - Service state: Enabled and started
  - Source: Chef `git` resource synchronizes a repository into `/opt/fastapi-tutorial`; repository URL, revision, branch, and credentials are not present in the supplied analysis.

- **postgresql**: PostgreSQL database service for the FastAPI application
  - Location/Path: Distribution-managed PostgreSQL data directory
  - Port/Socket: Not specified in the supplied execution tree; determine the active values from PostgreSQL configuration.
  - Service state: Enabled and started
  - Initialization: Runs `postgresql-setup --initdb` on Fedora/RHEL systems
  - Database user: `fastapi`
  - Database password: `fastapi_password`
  - Database: `fastapi_db`
  - Database owner: `fastapi`
  - Privileges: `fastapi` receives all privileges on `fastapi_db`

## File Structure

**MANDATORY: Preserve this section from the original plan.**

Only one recipe file is shown in the execution tree. No provider, template, attribute, or static file is shown as being used.

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

The `.env` file and systemd unit are created from inline Chef content, not from cookbook template or static files.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - On Fedora/RHEL systems, installs `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, and `libpq-devel`.
   - On non-Fedora/RHEL systems, installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - On Fedora/RHEL systems, runs `postgresql-setup --initdb` through `execute[initialize_postgresql]`. The migration should add an idempotence guard based on the PostgreSQL data directory or cluster state.
   - Creates `/opt/fastapi-tutorial` with the directory behavior defined by the original recipe. The supplied structured analysis does not confirm a directory mode.
   - Synchronizes the application repository into `/opt/fastapi-tutorial` using `git[/opt/fastapi-tutorial]`. The repository URL, revision, branch, and credentials must be obtained from the original recipe or migration input.
   - Creates the Python virtual environment with `execute[create_venv]`:
     ```bash
     python3 -m venv /opt/fastapi-tutorial/venv
     ```
     The migration must guard this operation so an existing environment is not unnecessarily recreated.
   - Installs Python dependencies with `execute[install_dependencies]`:
     ```bash
     /opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt
     ```
     This occurs after repository synchronization and virtual-environment creation.
   - Enables and starts `postgresql` through `service[postgresql]`.
   - Creates PostgreSQL user `fastapi`, assigns password `fastapi_password`, creates database `fastapi_db` owned by `fastapi`, and grants all privileges on `fastapi_db` to `fastapi` through `execute[create_db_user]`.
   - Writes `/opt/fastapi-tutorial/.env` using inline Chef file content. The exact content and file mode are not exposed by the supplied structured analysis and must be obtained from the original recipe.
   - Writes `/etc/systemd/system/fastapi-tutorial.service` using inline Chef file content. The exact unit content and file mode are not exposed by the supplied structured analysis and must be obtained from the original recipe.
   - Declares `execute[systemd_reload]` with:
     ```bash
     systemctl daemon-reload
     ```
     and `action: nothing`. No notification or subscription triggering this resource is shown. An Ansible handler that reloads systemd when the unit changes is an intentional correctness and idempotence improvement, not strict behavioral equivalence.
   - Enables and starts `fastapi-tutorial` through `service[fastapi-tutorial]`, after the systemd unit is deployed.

No custom resources, provider files, templates, attribute files, loops, or included recipes are present.

## Dependencies

**External cookbook dependencies**: Not specified in the supplied execution analysis.

**System package dependencies**:

- **Fedora/RHEL**:
  - `python3`
  - `python3-pip`
  - `git`
  - `postgresql-server`
  - `postgresql-contrib`
  - `libpq-devel`

- **Debian-family platforms**:
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

**Application source dependencies**:

- Git repository synchronized into `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`

## Credentials

**Detection Summary**: 1 hardcoded database credential detected in `cookbooks/fastapi-tutorial/recipes/default.rb`.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None detected
- **Path**: None detected
- **Data bag/Vault integration**: None detected
- **Environment-variable secret lookup**: Not shown in the supplied analysis

### PostgreSQL Password

- **Variable(s)**: No Chef variable is used; the literal password is embedded in the database command:
  `fastapi_password`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in an `execute` resource
- **Usage context**: Password assigned to PostgreSQL user `fastapi`
- **Related database identity**:
  - User: `fastapi`
  - Database: `fastapi_db`
- **Migration handling**: Store the password in Ansible Vault and pass it to `community.postgresql.postgresql_user`. If `/opt/fastapi-tutorial/.env` contains the same password, protect that content with Ansible Vault or a securely managed secret variable.

No Chef data bags, encrypted data bags, Chef Vault calls, CyberArk integration, Conjur calls, cloud secret manager references, TLS certificate references, or API tokens are shown.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- `cookbooks/fastapi-tutorial/recipes/default.rb`

**Directories to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/venv`

**Database objects to verify**:

- PostgreSQL role `fastapi`
- PostgreSQL database `fastapi_db`
- Owner of `fastapi_db`: `fastapi`
- All privileges granted to `fastapi` on `fastapi_db`

**Services to verify**:

- `postgresql`
- `fastapi-tutorial`

**Service endpoints to check**:

- FastAPI listening port: Not specified; inspect the deployed systemd unit and application configuration.
- PostgreSQL port: Not specified; query the active PostgreSQL configuration.
- PostgreSQL Unix socket: Not specified; query `unix_socket_directories`.

**Templates rendered**:

- None. No cookbook templates are present or rendered.
- `/opt/fastapi-tutorial/.env`: 0 cookbook template renders; generated from inline Chef content.
- `/etc/systemd/system/fastapi-tutorial.service`: 0 cookbook template renders; generated from inline Chef content.

## Pre-flight checks

```bash
# Confirm the target platform.
. /etc/os-release
printf 'Platform: %s %s\n' "$ID" "$VERSION_ID"

# Fedora/RHEL package checks.
if command -v rpm >/dev/null 2>&1; then
  rpm -q python3
  rpm -q python3-pip
  rpm -q git
  rpm -q postgresql-server
  rpm -q postgresql-contrib
  rpm -q libpq-devel
fi

# Debian-family package checks.
if command -v dpkg >/dev/null 2>&1; then
  dpkg -s python3
  dpkg -s python3-pip
  dpkg -s python3-venv
  dpkg -s git
  dpkg -s postgresql
  dpkg -s postgresql-contrib
  dpkg -s libpq-dev
fi

# fastapi-tutorial instance checks.
ls -ld /opt/fastapi-tutorial
ls -l /opt/fastapi-tutorial/requirements.txt
ls -ld /opt/fastapi-tutorial/venv
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
/opt/fastapi-tutorial/venv/bin/pip check
systemctl status fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
ls -l /opt/fastapi-tutorial/.env
stat -c '%a %n' /opt/fastapi-tutorial/.env
systemctl cat fastapi-tutorial
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
journalctl -u fastapi-tutorial --no-pager -n 100

# Review application configuration without exposing likely secrets.
sed -E 's/(PASSWORD|SECRET|TOKEN|KEY)=.*/\1=<redacted>/g' \
  /opt/fastapi-tutorial/.env

# Determine and test the configured FastAPI endpoint.
ss -tlnp
# After identifying the configured application port:
curl -I http://127.0.0.1:PORT
curl -sS http://127.0.0.1:PORT/

# postgresql instance checks.
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql

# Fedora/RHEL initialization check.
if command -v postgresql-setup >/dev/null 2>&1; then
  ls -ld /var/lib/pgsql
fi

# Debian-family cluster check.
if command -v pg_lsclusters >/dev/null 2>&1; then
  pg_lsclusters
fi

# PostgreSQL role, database, ownership, and privileges.
sudo -u postgres psql -tAc \
  "SELECT usename FROM pg_catalog.pg_user WHERE usename = 'fastapi';"

sudo -u postgres psql -tAc \
  "SELECT datname, pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"

sudo -u postgres psql -tAc \
  "SELECT has_database_privilege('fastapi', 'fastapi_db', 'CONNECT');"

sudo -u postgres psql -tAc \
  "SELECT has_database_privilege('fastapi', 'fastapi_db', 'CREATE');"

sudo -u postgres psql -tAc \
  "SELECT has_database_privilege('fastapi', 'fastapi_db', 'TEMPORARY');"

# PostgreSQL endpoint checks.
sudo -u postgres psql -tAc "SHOW port;"
sudo -u postgres psql -tAc "SHOW unix_socket_directories;"
ss -tlnp
ls -ld /run/postgresql

# Run the migration a second time to verify idempotence.
systemctl is-active postgresql
systemctl is-active fastapi-tutorial
sudo -u postgres psql -tAc \
  "SELECT usename FROM pg_catalog.pg_user WHERE usename = 'fastapi';"
sudo -u postgres psql -tAc \
  "SELECT datname FROM pg_database WHERE datname = 'fastapi_db';"
```

Expected results:

- `fastapi-tutorial` is enabled and active.
- `postgresql` is enabled and active.
- `/opt/fastapi-tutorial` and its virtual environment exist.
- The virtual environment contains executable `python` and `pip`.
- `pip check` reports no broken requirements.
- The `fastapi` PostgreSQL role exists.
- `fastapi_db` exists and is owned by `fastapi`.
- PostgreSQL privilege checks return `t`.
- The systemd unit passes `systemd-analyze verify`.
- The FastAPI endpoint responds on the port identified from the deployed configuration.
- A second migration run does not create duplicate database objects, unnecessarily recreate the virtual environment, or restart `fastapi-tutorial` unless application files or the systemd unit changed.