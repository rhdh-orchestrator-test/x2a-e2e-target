---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI Tutorial application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`, installs Python, Git, and PostgreSQL dependencies, creates `/opt/fastapi-tutorial/venv`, installs the repository requirements, provisions the `fastapi_db` PostgreSQL database and `fastapi` user, writes the application environment file, and manages the application with `fastapi-tutorial.service` listening on `0.0.0.0:8000`. It supports RHEL/Fedora and Debian/Ubuntu package layouts.

## Service Type and Instances

**Service Type**: Application Server with PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application served by Uvicorn
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Location/Path: `/opt/fastapi-tutorial`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Application entry point: `app.main:app`
  - Process command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Bind address: `0.0.0.0`
  - Port/Socket: `8000`
  - Systemd unit: `fastapi-tutorial.service`
  - Runtime user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Restart policy: `Restart=always`
  - Key configuration: `PROJECT_NAME="FastAPI Tutorial"`, `API_VERSION=1.0.0`, and a local PostgreSQL `DATABASE_URL`

- **postgresql**: PostgreSQL backing database service
  - Service name: `postgresql`
  - Database: `fastapi_db`
  - Database owner: `fastapi`
  - Database user: `fastapi`
  - Host/Socket: `localhost` for application connections; local PostgreSQL socket for administrative commands
  - Port: PostgreSQL default local port unless platform configuration changes it

## File Structure

**MANDATORY: Preserve this section from the original plan.**

Only one recipe file is executed by the cookbook. No provider, template, attribute, or static file is referenced by the supplied execution tree.

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

The cookbook performs operations in this order. No `.each` loops are defined.

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Detects the platform family with `platform_family?('fedora', 'rhel')`.
   - On RHEL/Fedora, installs `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, and `libpq-devel`.
   - On non-RHEL/Fedora systems, installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - On RHEL/Fedora, runs `postgresql-setup --initdb` through `execute[initialize_postgresql]` only when `/var/lib/pgsql/data/PG_VERSION` does not exist.
   - Creates `/opt/fastapi-tutorial` with owner `root`, group `root`, mode `0755`, and recursive creation enabled.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial` using `git[/opt/fastapi-tutorial]`.
   - Creates `/opt/fastapi-tutorial/venv` with `python3 -m venv /opt/fastapi-tutorial/venv` through `execute[create_venv]`, guarded by the virtual environment directory.
   - Installs dependencies with `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt` through `execute[install_dependencies]`, using `/opt/fastapi-tutorial` as the working directory.
   - Enables and starts `service[postgresql]`.
   - Creates PostgreSQL role `fastapi`, database `fastapi_db`, owner assignment, and grants using `execute[create_db_user]` as the `postgres` operating-system user. The source commands ignore existing-object errors with `|| true`.
   - Creates `/opt/fastapi-tutorial/.env` with owner `root`, group `root`, and mode `0644`, containing:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Creates `/etc/systemd/system/fastapi-tutorial.service` with owner `root`, group `root`, and mode `0644`. The unit:
     - Uses `Description=FastAPI Tutorial Service`.
     - Starts after `network.target` and `postgresql.service`.
     - Runs as `root` from `/opt/fastapi-tutorial`.
     - Sets `PATH=/opt/fastapi-tutorial/venv/bin`.
     - Executes `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`.
     - Uses `Restart=always`.
     - Is enabled through `multi-user.target`.
   - Notifies `execute[systemd_reload]` immediately when the unit file changes. The command is `systemctl daemon-reload` and has a default action of `nothing`.
   - Enables and starts `service[fastapi-tutorial]`.
   - The source recipe does not define an iterable collection or `.each` loop.

## Dependencies

**External cookbook dependencies**: None listed in `metadata.rb`.

**System package dependencies**:

RHEL/Fedora:
- `python3`
- `python3-pip`
- `git`
- `postgresql-server`
- `postgresql-contrib`
- `libpq-devel`

Debian/Ubuntu and other non-RHEL/Fedora platforms:
- `python3`
- `python3-pip`
- `python3-venv`
- `git`
- `postgresql`
- `postgresql-contrib`
- `libpq-dev`

**Application dependency source**:
- `/opt/fastapi-tutorial/requirements.txt`
- Repository: `https://github.com/dibanez/fastapi_tutorial.git`

**Service dependencies**:
- `postgresql`
- `fastapi-tutorial.service`

**Service ordering**:
- PostgreSQL starts before database provisioning and FastAPI startup.
- `fastapi-tutorial.service` declares `After=network.target postgresql.service`.

## Credentials

**Detection Summary**: 1 hardcoded database credential detected in 1 recipe file.

**Source**:
  - **Provider**: Hardcoded in the Chef recipe
  - **URL**: None
  - **Path**: None
  - **Recommended migration storage**: Ansible Vault

### PostgreSQL database password

- **Variable(s)**:
  - Hardcoded password: `fastapi_password`
  - Database user: `fastapi`
  - Database URL variable: `DATABASE_URL`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the recipe
- **Usage context**:
  - PostgreSQL command: `CREATE USER fastapi WITH PASSWORD 'fastapi_password'`
  - Environment file: `/opt/fastapi-tutorial/.env`
  - Connection string: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Recommended Ansible variables**:
  ```yaml
  fastapi_db_user: fastapi
  fastapi_db_password: "{{ vault_fastapi_db_password }}"
  fastapi_db_name: fastapi_db
  ```
- Store `vault_fastapi_db_password` in Ansible Vault and avoid logging it during database provisioning or file rendering.

No Chef data bags, encrypted data bags, Chef Vault calls, CyberArk integration, Conjur variables, TLS certificates, private keys, API keys, or external database connection strings were detected.

## Checks for the Migration

**Files to verify**:
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/var/lib/pgsql/data/PG_VERSION` on RHEL/Fedora
- Platform-managed PostgreSQL data directory on non-RHEL/Fedora systems
- PostgreSQL database `fastapi_db`
- PostgreSQL role `fastapi`

**Service endpoints to check**:
- FastAPI instance `fastapi-tutorial`: `0.0.0.0:8000`
- PostgreSQL instance `postgresql`: local `localhost` connection and local PostgreSQL socket

**Templates rendered**: None (0). The recipe creates both configuration files with inline `file` resources:
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Reload and restart behavior**:
- Changes to `/etc/systemd/system/fastapi-tutorial.service` trigger `systemctl daemon-reload`.
- The source recipe does not explicitly restart `fastapi-tutorial` when `.env` or application files change.
- `Restart=always` restarts the FastAPI process when it exits.

## Pre-flight checks:

```bash
# Package checks
python3 --version
python3 -m pip --version
git --version

# FastAPI instance: fastapi-tutorial
test -d /opt/fastapi-tutorial
test -d /opt/fastapi-tutorial/venv
test -f /opt/fastapi-tutorial/requirements.txt
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip

# RHEL/Fedora PostgreSQL initialization
test -f /var/lib/pgsql/data/PG_VERSION

# Repository
git -C /opt/fastapi-tutorial remote -v
git -C /opt/fastapi-tutorial branch --show-current
git -C /opt/fastapi-tutorial rev-parse --verify HEAD

# PostgreSQL instance: postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
systemctl status postgresql --no-pager

# PostgreSQL role and database
sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='fastapi';"
sudo -u postgres psql -tAc "SELECT datname FROM pg_database WHERE datname='fastapi_db';"
sudo -u postgres psql -tAc "SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname='fastapi_db';"

# PostgreSQL connectivity for fastapi-tutorial
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_database(), current_user;"

# Environment file
test -f /opt/fastapi-tutorial/.env
grep '^PROJECT_NAME=' /opt/fastapi-tutorial/.env
grep '^API_VERSION=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env

# FastAPI systemd instance: fastapi-tutorial.service
test -f /etc/systemd/system/fastapi-tutorial.service
systemctl daemon-reload
systemctl is-enabled fastapi-tutorial.service
systemctl is-active fastapi-tutorial.service
systemctl status fastapi-tutorial.service --no-pager
systemctl show fastapi-tutorial.service \
  --property=User,WorkingDirectory,ExecStart,Restart
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service

# FastAPI endpoint
curl -I http://127.0.0.1:8000/
curl -sS http://127.0.0.1:8000/
ss -tlnp | grep ':8000'

# Logs
journalctl -u postgresql --no-pager -n 100
journalctl -u fastapi-tutorial.service --no-pager -n 100

# File ownership and permissions
ls -ld /opt/fastapi-tutorial
ls -ld /opt/fastapi-tutorial/venv
stat -c '%U:%G %a %n' /opt/fastapi-tutorial/.env
stat -c '%U:%G %a %n' /etc/systemd/system/fastapi-tutorial.service
```

Expected results:

- Repository remote is `https://github.com/dibanez/fastapi_tutorial.git` and the requested revision is `main`.
- PostgreSQL is enabled and active.
- Role `fastapi` and database `fastapi_db` exist, with `fastapi` as the database owner.
- `fastapi-tutorial.service` is enabled and active.
- The FastAPI process listens on `0.0.0.0:8000`.
- The systemd unit has `User=root`, `WorkingDirectory=/opt/fastapi-tutorial`, `Restart=always`, and the expected Uvicorn command.
- Chef-equivalent permissions are `/opt/fastapi-tutorial` as `root:root` `0755`, `.env` as `root:root` `0644`, and the systemd unit as `root:root` `0644`.
- If the database password is migrated to Ansible Vault, `.env` should preferably use mode `0600`.
