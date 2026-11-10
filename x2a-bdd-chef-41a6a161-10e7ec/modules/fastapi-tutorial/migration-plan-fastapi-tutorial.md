---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` under `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, and platform-specific development packages; creates a Python virtual environment; installs application dependencies; initializes, enables, and starts PostgreSQL; creates the `fastapi` PostgreSQL role and `fastapi_db` database; writes the application environment file; and manages the `fastapi-tutorial` systemd service on port `8000`. The PostgreSQL password is currently hardcoded as `fastapi_password` and must be migrated to Ansible Vault.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application managed by systemd
  - Location/Path: `/opt/fastapi-tutorial`
  - Source repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Git revision: `main`
  - Python virtual environment: `/opt/fastapi-tutorial/venv`
  - Dependency file: `/opt/fastapi-tutorial/requirements.txt`
  - Startup command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Bind address: `0.0.0.0`
  - Port/Socket: `8000`
  - Runtime user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Restart policy: `always`
  - systemd unit: `/etc/systemd/system/fastapi-tutorial.service`

- **postgresql**: Local PostgreSQL database service
  - Service name: `postgresql`
  - Enabled at boot: yes
  - Started by Chef: yes
  - Database user: `fastapi`
  - Database name: `fastapi_db`
  - Database owner: `fastapi`
  - Connection host: `localhost`
  - Connection URL: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`

### Platform-Conditional Package Sets

For Fedora/RHEL systems:

- `python3`
- `python3-pip`
- `git`
- `postgresql-server`
- `postgresql-contrib`
- `libpq-devel`

For non-Fedora/RHEL systems, including Ubuntu/Debian:

- `python3`
- `python3-pip`
- `python3-venv`
- `git`
- `postgresql`
- `postgresql-contrib`
- `libpq-dev`

## File Structure

Only files shown in the supplied execution tree and directory listing are included.

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

The cookbook uses inline Chef resource content for `.env` and the systemd unit. It does not render ERB templates or deploy static cookbook files.

## Module Explanation

The cookbook has one recipe and no `include_recipe` calls. Execution order must be preserved in the Ansible role or playbook.

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Selects and installs the platform-specific package set.
   - On Fedora/RHEL, runs `postgresql-setup --initdb` when `/var/lib/pgsql/data/PG_VERSION` does not exist.
   - Creates `/opt/fastapi-tutorial` with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates `/opt/fastapi-tutorial/venv` using `python3 -m venv`.
   - Installs dependencies from `/opt/fastapi-tutorial/requirements.txt` into the virtual environment.
   - Enables and starts the `postgresql` service.
   - Creates the PostgreSQL role `fastapi`, database `fastapi_db`, and grants all database privileges to `fastapi`.
   - Creates `/opt/fastapi-tutorial/.env` with owner `root`, group `root`, and mode `0644`.
   - Creates `/etc/systemd/system/fastapi-tutorial.service` with owner `root`, group `root`, and mode `0644`.
   - Reloads systemd when the unit file changes.
   - Enables and starts the `fastapi-tutorial` service.

### Ansible implementation details

- Use `ansible.builtin.package` with:
  - Fedora/RHEL condition: `ansible_facts.os_family in ['RedHat', 'Fedora']`
  - Non-Fedora/RHEL condition: `ansible_facts.os_family not in ['RedHat', 'Fedora']`
- Use `ansible.builtin.command` with `creates: /var/lib/pgsql/data/PG_VERSION` for Fedora/RHEL PostgreSQL initialization.
- Use `ansible.builtin.file` for `/opt/fastapi-tutorial`.
- Use `ansible.builtin.git` for the repository checkout.
- Use `ansible.builtin.command` with `creates: /opt/fastapi-tutorial/venv` or an equivalent virtual-environment module.
- Use `ansible.builtin.pip` with:
  - Requirements: `/opt/fastapi-tutorial/requirements.txt`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
- Use PostgreSQL-specific Ansible modules to create the role, database, ownership, and privileges rather than reproducing the original `|| true` shell commands.
- Run database administration tasks as the PostgreSQL administrative account, normally `postgres`.
- Render `/opt/fastapi-tutorial/.env` using the vaulted database password.
- Deploy the systemd unit with `ansible.builtin.template` or `ansible.builtin.copy`.
- Notify a handler that runs `systemctl daemon-reload` when `/etc/systemd/system/fastapi-tutorial.service` changes.
- Enable and start `fastapi-tutorial` only after the repository, virtual environment, dependencies, environment file, PostgreSQL service, and database are configured.

### Configuration variables

```yaml
fastapi_app_directory: /opt/fastapi-tutorial
fastapi_repository: https://github.com/dibanez/fastapi_tutorial.git
fastapi_revision: main
fastapi_venv: /opt/fastapi-tutorial/venv
fastapi_port: 8000
fastapi_bind_address: 0.0.0.0
fastapi_db_user: fastapi
fastapi_db_name: fastapi_db
fastapi_db_host: localhost
fastapi_db_password: !vault |
  ...
```

## Dependencies

**External cookbook dependencies**: None specified in the supplied metadata or execution tree.

**System package dependencies**:

- Fedora/RHEL: `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, `libpq-devel`
- Non-Fedora/RHEL: `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, `libpq-dev`

**Service dependencies**:

- `postgresql`
- `fastapi-tutorial`

**Application dependency source**: `/opt/fastapi-tutorial/requirements.txt`

**Systemd dependency relationship**: `fastapi-tutorial.service` starts after `network.target` and `postgresql.service`.

## Credentials

**Detection Summary**: 1 credential detected across `cookbooks/fastapi-tutorial/recipes/default.rb`. The credential is used for both PostgreSQL role creation and the application connection URL.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None
- **Path**: None
- **Recommended storage**: Ansible Vault

### PostgreSQL Password

- **Variable(s)**: `fastapi_db_password`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Source locations**: PostgreSQL user creation command and `DATABASE_URL`
- **Current storage**: Hardcoded plaintext value `fastapi_password`
- **Usage context**:
  - Sets the password for PostgreSQL user `fastapi`
  - Authenticates the FastAPI application to `fastapi_db`
- **Migration action**:
  - Store the value in Ansible Vault as `fastapi_db_password`
  - Use the vaulted variable in the PostgreSQL role task
  - Use the same variable when rendering `/opt/fastapi-tutorial/.env`
  - Do not expose it in command-line arguments, committed plaintext variables, or task output

No Chef data bags, encrypted data bags, Chef Vault calls, CyberArk integration, Conjur variables, environment-variable secret lookups, TLS certificate references, or external secret-manager URLs were identified.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- `/var/lib/pgsql/data/PG_VERSION` on Fedora/RHEL

**Service endpoints to check**:

- FastAPI: `0.0.0.0:8000`
- PostgreSQL: `localhost`, database `fastapi_db`

**Templates rendered**:

- `/opt/fastapi-tutorial/.env`: rendered once; originally created by an inline Chef `file` resource
- `/etc/systemd/system/fastapi-tutorial.service`: rendered once; originally created by an inline Chef `file` resource

No Chef templates are rendered.

## Pre-flight checks

### fastapi-tutorial application instance

```bash
python3 --version
git --version

ls -ld /opt/fastapi-tutorial
ls -l /opt/fastapi-tutorial/requirements.txt
ls -l /opt/fastapi-tutorial/venv/bin/python
ls -l /opt/fastapi-tutorial/venv/bin/uvicorn

git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
git -C /opt/fastapi-tutorial rev-parse HEAD

ls -l /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION)=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env | \
  sed -E 's#://[^:]+:[^@]+@#://REDACTED:REDACTED@#'

ls -l /etc/systemd/system/fastapi-tutorial.service
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service

grep -E '^(After|User|WorkingDirectory|Environment|ExecStart|Restart)=' \
  /etc/systemd/system/fastapi-tutorial.service

systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl status fastapi-tutorial --no-pager

ss -tlnp | grep ':8000'
lsof -iTCP:8000 -sTCP:LISTEN
curl -i http://127.0.0.1:8000/
curl -i http://127.0.0.1:8000/openapi.json

journalctl -u fastapi-tutorial --no-pager -n 100
ps aux | grep '[u]vicorn'

systemctl show fastapi-tutorial \
  --property=User,WorkingDirectory,ExecStart,Environment,Restart
```

Expected application command:

```text
/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The service should run as `root`, use `/opt/fastapi-tutorial` as its working directory, and execute Uvicorn from `/opt/fastapi-tutorial/venv/bin/uvicorn`.

### postgresql database instance

```bash
systemctl is-enabled postgresql
systemctl is-active postgresql
systemctl status postgresql --no-pager

sudo -u postgres psql -tAc \
  "SELECT 1 FROM pg_roles WHERE rolname='fastapi';"

sudo -u postgres psql -tAc \
  "SELECT datname, pg_catalog.pg_get_userbyid(datdba) \
   FROM pg_database WHERE datname='fastapi_db';"

PGPASSWORD='REDACTED' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_database(), current_user;"

sudo -u postgres psql -tAc \
  "SELECT has_database_privilege('fastapi', 'fastapi_db', 'CONNECT');"

journalctl -u postgresql --no-pager -n 100
```

Supply the actual password securely rather than placing it literally in shell history. On Fedora/RHEL, also verify PostgreSQL initialization:

```bash
test -f /var/lib/pgsql/data/PG_VERSION
```

The expected database role is `fastapi`, the expected database is `fastapi_db`, and the expected database owner is `fastapi`.