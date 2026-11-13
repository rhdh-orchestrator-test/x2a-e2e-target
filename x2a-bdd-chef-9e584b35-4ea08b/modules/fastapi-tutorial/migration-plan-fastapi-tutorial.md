---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI Tutorial application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`, installs platform-specific Python, Git, PostgreSQL, and development packages, creates a Python virtual environment, installs application requirements, initializes and configures PostgreSQL, writes an environment file, and runs the application through systemd on `0.0.0.0:8000`. The cookbook configures one application instance, `fastapi-tutorial`, with a `postgresql` database dependency. The database password is hardcoded in the Chef source and must be migrated to Ansible Vault or an approved external secret-management system.

## Service Type and Instances

**Service Type**: Application Server with PostgreSQL database dependency

The cookbook does not install a web server such as Nginx. The FastAPI application listens directly through Uvicorn on TCP port `8000`.

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application server
  - Location/Path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Dependency file: `/opt/fastapi-tutorial/requirements.txt`
  - Application module: `app.main:app`
  - Application command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Run user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Port/Socket: `0.0.0.0:8000`
  - Environment file: `/opt/fastapi-tutorial/.env`
  - Systemd behavior: enabled, started, and configured with `Restart=always`

- **postgresql**: Local PostgreSQL database service
  - Service name: `postgresql`
  - Service actions: enabled and started
  - Database user: `fastapi`
  - Database name: `fastapi_db`
  - Database owner: `fastapi`
  - Database host: `localhost`
  - Port/Socket: PostgreSQL local default port and distribution-default Unix socket; no explicit port is configured
  - Database URL: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`

No collection attributes or `.each` loops are present. There are no repeated instances to expand.

## File Structure

```text
cookbooks/fastapi-tutorial/
├── recipes/
│   └── default.rb
├── providers/
├── templates/
├── attributes/
└── files/
```

Only `cookbooks/fastapi-tutorial/recipes/default.rb` is executed or referenced by the supplied execution tree. No custom resources, providers, ERB templates, attribute files, or static cookbook files are used. Configuration files are generated directly by Chef `file` resources using inline content.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs RHEL/Fedora packages when `platform_family?('fedora', 'rhel')` is true:
     - `python3`
     - `python3-pip`
     - `git`
     - `postgresql-server`
     - `postgresql-contrib`
     - `libpq-devel`
   - Runs `postgresql-setup --initdb` through `execute[initialize_postgresql]` only when `/var/lib/pgsql/data/PG_VERSION` does not exist.
   - Installs the non-Fedora/RHEL package set:
     - `python3`
     - `python3-pip`
     - `python3-venv`
     - `git`
     - `postgresql`
     - `postgresql-contrib`
     - `libpq-dev`
   - Creates `/opt/fastapi-tutorial` as `root:root` with mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial` through `git[/opt/fastapi-tutorial]`.
   - Creates `/opt/fastapi-tutorial/venv` with `python3 -m venv`, guarded by `creates: /opt/fastapi-tutorial/venv`.
   - Installs dependencies from `/opt/fastapi-tutorial/requirements.txt` using `/opt/fastapi-tutorial/venv/bin/pip` through `execute[install_dependencies]`, with `/opt/fastapi-tutorial` as the working directory.
   - Enables and starts the `postgresql` service through `service[postgresql]`.
   - Creates the PostgreSQL role `fastapi`, database `fastapi_db`, ownership, and privileges through `execute[create_db_user]`, executing as the `postgres` operating-system user. The Chef commands use `|| true`, so the migration should use idempotent PostgreSQL-specific modules instead.
   - Creates `/opt/fastapi-tutorial/.env` through `file[/opt/fastapi-tutorial/.env]`, owned by `root:root` with mode `0644`, containing:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
     The password must be replaced with a protected Ansible Vault or external-secret variable.
   - Creates `/etc/systemd/system/fastapi-tutorial.service` through `file[/etc/systemd/system/fastapi-tutorial.service]`, owned by `root:root` with mode `0644`, containing:
     ```ini
     [Unit]
     Description=FastAPI Tutorial Service
     After=network.target postgresql.service

     [Service]
     Type=simple
     User=root
     WorkingDirectory=/opt/fastapi-tutorial
     Environment="PATH=/opt/fastapi-tutorial/venv/bin"
     ExecStart=/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
     Restart=always

     [Install]
     WantedBy=multi-user.target
     ```
   - Notifies `execute[systemd_reload]`, which runs `systemctl daemon-reload` when the unit changes. The Chef resource has `action: nothing`; the Ansible equivalent should be a handler, with `meta: flush_handlers` used before service startup if strict ordering is required.
   - Enables and starts the `fastapi-tutorial` service through `service[fastapi-tutorial]` only after the unit file is deployed and systemd has reloaded its configuration.
   - Iterations: None. No `.each` loops or collection-based resources are present.

## Dependencies

**External cookbook dependencies**: None listed in `metadata.rb`.

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**System package dependencies**:

- **Fedora/RHEL**: `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, `libpq-devel`
- **Non-Fedora/RHEL**: `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, `libpq-dev`

**Service dependencies**:

- `postgresql`
- `fastapi-tutorial`

**Application dependency source**: `/opt/fastapi-tutorial/requirements.txt`

**Application dependency target**: `/opt/fastapi-tutorial/venv`

**Ansible project requirements**:

- `INPUT-AGENTS.md` and `EXPORT-AGENTS.md` must require a non-empty `ansible/Makefile`.
- The Makefile must define a default `all` target.
- The default target must invoke `ansible-playbook`.

Required pattern:

```makefile
.PHONY: all

all:
	ansible-playbook -i inventory site.yml
```

## Credentials

**Detection Summary**: 1 hardcoded database password detected in 1 source recipe and propagated into 1 generated environment file.

**Source**:
  - **Provider**: Hardcoded in the Chef recipe
  - **URL**: No secret-management URL detected
  - **Path**: No data bag, vault path, CyberArk path, or external secret path detected

### PostgreSQL database password

- **Variable(s)**: `fastapi_password`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded plaintext in the `create_db_user` execute resource
- **Additional usage**: Embedded in `DATABASE_URL` in `/opt/fastapi-tutorial/.env`
- **Usage context**: PostgreSQL role authentication for user `fastapi` connecting to `fastapi_db`
- **Migration requirement**: Store the password in Ansible Vault or an approved external secret manager. Use the protected value both when creating the PostgreSQL role and when rendering `DATABASE_URL`.

The PostgreSQL username `fastapi` is not itself a secret. No data bags, encrypted data bags, Chef Vault items, Conjur variables, CyberArk integrations, environment-variable secret lookups, TLS certificates, private keys, API tokens, or external database connection strings were detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- `/var/lib/pgsql/data` on RHEL/Fedora after initialization
- The distribution-specific PostgreSQL data path on Debian/Ubuntu
- PostgreSQL logs from the `postgresql` service journal
- FastAPI logs from the `fastapi-tutorial` service journal

**Service endpoints to check**:

- `fastapi-tutorial`: `0.0.0.0:8000`
- `postgresql`: local PostgreSQL listener; no explicit port is configured

**Unix sockets**:

- No application Unix socket is configured.
- PostgreSQL may expose its distribution-default local Unix socket.

**Templates rendered**:

- None; render count: `0`.
- The cookbook uses inline `file` resources instead of ERB templates.

**Generated configuration files**:

- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

## Pre-flight checks:

```bash
# Verify the fastapi-tutorial application instance
ls -ld /opt/fastapi-tutorial
ls -l /opt/fastapi-tutorial/requirements.txt
ls -ld /opt/fastapi-tutorial/venv
git -C /opt/fastapi-tutorial rev-parse --is-inside-work-tree
git -C /opt/fastapi-tutorial branch --show-current
git -C /opt/fastapi-tutorial rev-parse HEAD
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip --version
/opt/fastapi-tutorial/venv/bin/pip check

# Verify the PostgreSQL instance
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='fastapi';"
sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='fastapi_db';"
sudo -u postgres psql -tAc \
  "SELECT pg_catalog.pg_get_userbyid(datdba) FROM pg_database WHERE datname='fastapi_db';"
sudo -u postgres psql -d fastapi_db -c "SELECT version();"
PGPASSWORD='<retrieve-from-approved-secret-store>' \
psql -h localhost -U fastapi -d fastapi_db -c "SELECT 1;"

# Verify the application environment file
stat -c '%A %U:%G %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION)=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env | \
  sed -E 's#://[^:]+:[^@]+@#://***:***@#'

# Verify the fastapi-tutorial systemd unit
stat -c '%A %U:%G %n' /etc/systemd/system/fastapi-tutorial.service
systemctl cat fastapi-tutorial
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl show fastapi-tutorial -p ExecStart
systemctl show fastapi-tutorial -p WorkingDirectory
systemctl show fastapi-tutorial -p User
systemctl show fastapi-tutorial -p Restart
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial

# Verify the FastAPI process and endpoint
ps aux | grep '[u]vicorn app.main:app'
ss -tlnp | grep ':8000'
netstat -tulpn 2>/dev/null | grep ':8000'
curl -I http://127.0.0.1:8000/
curl -sS http://127.0.0.1:8000/

# Review FastAPI service behavior and logs
systemctl list-unit-files | grep '^fastapi-tutorial.service'
systemctl --failed
journalctl -u fastapi-tutorial --since "30 minutes ago" --no-pager
journalctl -u fastapi-tutorial --no-pager -n 100
```
