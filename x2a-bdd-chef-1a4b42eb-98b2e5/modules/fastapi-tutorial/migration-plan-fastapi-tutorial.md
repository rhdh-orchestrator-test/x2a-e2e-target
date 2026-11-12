---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI tutorial application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main`. It installs Python, Git, and PostgreSQL dependencies, creates a Python virtual environment, installs application requirements, provisions the `fastapi` PostgreSQL role and `fastapi_db` database, writes the application environment file, and manages a systemd service named `fastapi-tutorial` listening on port `8000`. The migration must store the database password in Ansible Vault and include a non-empty `ansible/Makefile` whose default `all` target invokes `ansible-playbook`.

## Service Type and Instances

**Service Type**: Application Server with PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application served by Uvicorn
  - Location/Path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Dependency file: `/opt/fastapi-tutorial/requirements.txt`
  - Environment file: `/opt/fastapi-tutorial/.env`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Runtime user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Executable: `/opt/fastapi-tutorial/venv/bin/uvicorn`
  - Application target: `app.main:app`
  - Port/Socket: `0.0.0.0:8000`
  - Restart policy: `always`
  - Service actions: enabled and started

- **postgresql**: Application database service
  - Service name: `postgresql`
  - Port/Socket: Normally TCP `5432` and/or a distribution-managed local Unix socket
  - Service actions: enabled and started
  - Database user: `fastapi`
  - Database name: `fastapi_db`
  - Database owner: `fastapi`
  - Connection host: `localhost`
  - Connection URL: `postgresql://fastapi:<vaulted-password>@localhost/fastapi_db`

There are no collection attributes or `.each` iterations in the cookbook. No instance expansion is required.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

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

None.

**Templates:**

None. Configuration is written through inline Chef `file` resources rather than `.erb` templates.

**Attributes:**

None.

**Files:**

None. No `cookbook_file` or `remote_file` resources are used.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Detects whether the platform belongs to the Fedora/RHEL family.
   - On Fedora/RHEL, installs `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, and `libpq-devel`.
   - On non-Fedora/RHEL platforms, installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - On Fedora/RHEL, runs `postgresql-setup --initdb` only when `/var/lib/pgsql/data/PG_VERSION` does not exist.
   - Creates `/opt/fastapi-tutorial` with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates `/opt/fastapi-tutorial/venv` with `python3 -m venv /opt/fastapi-tutorial/venv`.
   - Installs Python dependencies using `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt` from `/opt/fastapi-tutorial`.
   - Enables and starts the `postgresql` service before database provisioning.
   - Creates the PostgreSQL role `fastapi` with the vaulted password.
   - Creates the `fastapi_db` database owned by `fastapi`.
   - Grants all privileges on `fastapi_db` to `fastapi`.
   - Writes `/opt/fastapi-tutorial/.env` with owner `root`, group `root`, and mode `0644`, preserving:
     - `PROJECT_NAME="FastAPI Tutorial"`
     - `API_VERSION=1.0.0`
     - `DATABASE_URL=postgresql://fastapi:<vaulted-password>@localhost/fastapi_db`
   - Deploys `/etc/systemd/system/fastapi-tutorial.service` with owner `root`, group `root`, and mode `0644`.
   - Configures the systemd unit with:
     - `After=network.target postgresql.service`
     - `User=root`
     - `WorkingDirectory=/opt/fastapi-tutorial`
     - `Environment="PATH=/opt/fastapi-tutorial/venv/bin"`
     - `ExecStart=/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
     - `Restart=always`
     - `WantedBy=multi-user.target`
   - Notifies a systemd daemon-reload handler when `/etc/systemd/system/fastapi-tutorial.service` changes.
   - Enables and starts the `fastapi-tutorial` service.
   - Iterations: None; no `.each` loops are present.

   **Resources in execution order:**
   - `package`: 1 conditional resource
   - `execute[initialize_postgresql]`: conditional on Fedora/RHEL, idempotent with `/var/lib/pgsql/data/PG_VERSION`
   - `directory[/opt/fastapi-tutorial]`
   - `git[/opt/fastapi-tutorial]`
   - `execute[create_venv]`
   - `execute[install_dependencies]`
   - `service[postgresql]`
   - `execute[create_db_user]`
   - `file[/opt/fastapi-tutorial/.env]`
   - `file[/etc/systemd/system/fastapi-tutorial.service]`
   - `execute[systemd_reload]`:  notification-only resource with action `nothing`, invoked when the systemd unit changes
   - `service[fastapi-tutorial]`

   **Full resource counts:**
   - `package`: 1 conditional resource
   - `execute`: 5 resources
   - `directory`: 1 resource
   - `git`: 1 resource
   - `service`: 2 resources
   - `file`: 2 resources

## Dependencies

**External cookbook dependencies**: None listed in `metadata.rb`.

**System package dependencies**:

Fedora/RHEL:

- `python3`
- `python3-pip`
- `git`
- `postgresql-server`
- `postgresql-contrib`
- `libpq-devel`

Non-Fedora/RHEL:

- `python3`
- `python3-pip`
- `python3-venv`
- `git`
- `postgresql`
- `postgresql-contrib`
- `libpq-dev`

**Application dependency source**: `/opt/fastapi-tutorial/requirements.txt`

The exact Python packages are supplied by the cloned repository.

**Service dependencies**:

- `postgresql`
- `fastapi-tutorial`
- `network.target`

The FastAPI systemd unit declares `After=network.target postgresql.service`.

## Credentials

**Detection Summary**: 1 hardcoded database credential detected in 1 source file. The credential is used in the PostgreSQL role creation command and the generated database connection URL.

**Source**:

- **Provider**: Hardcoded in Chef recipe
- **URL**: None
- **Path**: None; no data bag, vault, CyberArk, Conjur, or external secret-manager path was detected

### PostgreSQL database password

- **Variable**: `fastapi_db_password`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current value**: Password for PostgreSQL user `fastapi`: `fastapi_password`
- **Current storage**: Hardcoded in `execute[create_db_user]` and inline `.env` content
- **Usage context**:
  - Sets the password for PostgreSQL role `fastapi`
  - Appears in `DATABASE_URL` in `/opt/fastapi-tutorial/.env`
  - Allows the FastAPI application to connect to `fastapi_db`

The Ansible migration must store `fastapi_db_password` in Ansible Vault or another approved secret-management system and use it consistently for PostgreSQL role creation, `.env`, and any derived database connection configuration.

No other credentials or secrets were detected. No SSL/TLS certificate, private key, API key, token, encrypted data bag, Chef Vault item, CyberArk integration, Conjur variable, or secret-related attribute namespace was detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/.env`
- `/opt/fastapi-tutorial/venv/`
- `/etc/systemd/system/fastapi-tutorial.service`
- `/opt/fastapi-tutorial/`
- Fedora/RHEL PostgreSQL data directory: `/var/lib/pgsql/data/`
- Non-Fedora/RHEL distribution-managed PostgreSQL data directory
- `ansible/Makefile`

**Service endpoints to check**:

- `fastapi-tutorial`: HTTP endpoint `0.0.0.0:8000`
- `postgresql`: local PostgreSQL service, normally TCP port `5432`
- `postgresql`: distribution-managed local Unix socket

**Templates rendered**:

None. The Chef cookbook does not render `.erb` templates.

**Inline files created**:

- `/opt/fastapi-tutorial/.env`: 1 time
- `/etc/systemd/system/fastapi-tutorial.service`: 1 time

## Pre-flight checks:

```bash
# Verify both named services individually
systemctl status postgresql
systemctl is-enabled postgresql
systemctl status fastapi-tutorial
systemctl is-enabled fastapi-tutorial

# Verify the PostgreSQL instance
sudo -u postgres psql -c "SELECT version();"
sudo -u postgres psql -tAc "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"
sudo -u postgres psql -tAc "SELECT datname FROM pg_database WHERE datname = 'fastapi_db';"
sudo -u postgres psql -tAc "SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"
ss -tlnp | grep ':5432' || true

# Verify the fastapi-tutorial instance and process
systemctl show fastapi-tutorial --property=ExecMainStatus,ActiveState,SubState
ps aux | grep '[u]vicorn app.main:app'
ss -tlnp | grep ':8000'
curl -I http://127.0.0.1:8000/
curl -sS http://127.0.0.1:8000/

# Verify application database connectivity without exposing the password
PGPASSWORD='<fastapi_db_password>' \
psql -h 127.0.0.1 -U fastapi -d fastapi_db -c "SELECT 1;"

# Verify application configuration
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' /opt/fastapi-tutorial/.env
grep -E '^(Description|After|User|WorkingDirectory|Environment|ExecStart|Restart|WantedBy)=' \
  /etc/systemd/system/fastapi-tutorial.service

# Validate the systemd unit and reload definitions
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl daemon-reload

# Verify the Python virtual environment and dependencies
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip check

# Verify the source checkout
git -C /opt/fastapi-tutorial rev-parse --is-inside-work-tree
git -C /opt/fastapi-tutorial branch --show-current
git -C /opt/fastapi-tutorial log -1 --oneline
test -f /opt/fastapi-tutorial/requirements.txt

# Verify the required Makefile
test -s ansible/Makefile
grep -q '^all:' ansible/Makefile
grep -q 'ansible-playbook' ansible/Makefile

# Review logs for both named services
journalctl -u postgresql --no-pager -n 100
journalctl -u fastapi-tutorial --no-pager -n 100
```

Expected results:

- `postgresql` is active and enabled.
- `fastapi-tutorial` is active and enabled.
- PostgreSQL role `fastapi` and database `fastapi_db` exist, with `fastapi` as the database owner.
- Uvicorn listens on `0.0.0.0:8000`.
- The FastAPI endpoint accepts HTTP connections.
- The virtual environment contains working Python and pip executables, and `pip check` reports no broken requirements.
- The checkout is a Git working tree corresponding to the `main` revision.
- The systemd unit passes validation and contains the required application, database ordering, and restart settings.
- The Makefile is non-empty, defines the default `all` target, and invokes `ansible-playbook`.
- Logs contain no Uvicorn startup errors, Python import errors, database authentication failures, missing dependency errors, or PostgreSQL initialization errors.