---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI Tutorial application from the `main` branch of `https://github.com/dibanez/fastapi_tutorial.git` to `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, and PostgreSQL development packages; creates a Python virtual environment; installs application requirements; creates the `fastapi` PostgreSQL role and `fastapi_db` database; writes an application `.env` file; and manages the application with the `fastapi-tutorial` systemd service on `0.0.0.0:8000`. The PostgreSQL password is hardcoded in the Chef recipe and must be migrated to Ansible Vault or an Ansible Automation Platform credential.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application service
  - Location/Path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Service user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Application command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Port/Socket: `0.0.0.0:8000`
  - Restart policy: `always`

- **fastapi_db**: PostgreSQL database instance
  - Database name: `fastapi_db`
  - Database user: `fastapi`
  - Database owner: `fastapi`
  - Host: `localhost`
  - Port/Socket: `5432`
  - Database URL: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`

No collection attributes or `.each` iterations are present. There are no additional application sites, database collections, or service-instance loops.

## File Structure

The execution tree contains one recipe file. No provider, template, attribute, or static file is used by this cookbook.

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

The `.env` file and systemd unit are created using inline Chef `file` resources rather than cookbook files.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - The Chef package resource installs seven packages in one resource.
   - Migrate with `ansible.builtin.package`; validate package and PostgreSQL service names on Ubuntu `>= 18.04` and CentOS `>= 7.0`.

2. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/opt/fastapi-tutorial` recursively.
   - Sets owner and group to `root:root` and mode to `0755`.
   - Migrate with `ansible.builtin.file` using `state: directory`.

3. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - No repository credentials are configured because the repository is unauthenticated.
   - Migrate with `ansible.builtin.git` using an update behavior equivalent to Chef `sync`.

4. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Runs `python3 -m venv /opt/fastapi-tutorial/venv`.
   - Uses a `creates` guard, so the command is skipped when `/opt/fastapi-tutorial/venv` already exists.
   - Migrate with `ansible.builtin.command` or `ansible.builtin.shell` guarded by file existence, or create the environment before using `ansible.builtin.pip`.

5. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Runs `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt` with working directory `/opt/fastapi-tutorial`.
   - The task runs after repository synchronization and virtual-environment creation.
   - Prefer `ansible.builtin.pip` with requirements `/opt/fastapi-tutorial/requirements.txt` and virtual environment `/opt/fastapi-tutorial/venv`.

6. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Enables and starts the `postgresql` service.
   - Migrate with `ansible.builtin.service` or `ansible.builtin.systemd` using `enabled: true` and `state: started`.
   - This must occur before PostgreSQL role and database creation.

7. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates PostgreSQL role `fastapi` with the configured password.
   - Creates database `fastapi_db` owned by `fastapi`.
   - Grants all privileges on `fastapi_db` to `fastapi`.
   - The original Chef commands use `|| true`, which masks errors beyond expected already-exists conditions.
   - Replace the commands with `community.postgresql.postgresql_user`, `community.postgresql.postgresql_db`, and `community.postgresql.postgresql_privs`.
   - Execute PostgreSQL administration tasks with `become_user: postgres`.
   - Supply the password from Ansible Vault or an AAP credential; do not store it in ordinary variables or task files.

8. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/opt/fastapi-tutorial/.env` as `root:root` with mode `0644`.
   - Writes:
     - `PROJECT_NAME="FastAPI Tutorial"`
     - `API_VERSION=1.0.0`
     - `DATABASE_URL` pointing to `fastapi_db` on `localhost`.
   - Migrate with `ansible.builtin.copy` or `ansible.builtin.template`.
   - Construct `DATABASE_URL` from protected variables and consider mode `0600` because the file contains a database password. Any mode change from `0644` must be documented as a security improvement.

9. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/etc/systemd/system/fastapi-tutorial.service` as `root:root` with mode `0644`.
   - Defines `Description=FastAPI Tutorial Service`.
   - Uses `After=network.target postgresql.service`.
   - Runs as `root` with working directory `/opt/fastapi-tutorial`.
   - Sets `PATH=/opt/fastapi-tutorial/venv/bin`.
   - Runs `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`.
   - Uses `Restart=always` and `WantedBy=multi-user.target`.
   - Migrate with `ansible.builtin.copy` or `ansible.builtin.template`, preserving the command, dependencies, working directory, user, and restart policy unless service hardening is intentionally implemented.

10. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
    - Defines `systemctl daemon-reload` as `execute['systemd_reload']` with action `:nothing`.
    - The reload is notified immediately when `/etc/systemd/system/fastapi-tutorial.service` changes.
    - Migrate with an Ansible handler using `ansible.builtin.systemd` and `daemon_reload: true`.

11. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
    - Enables and starts the `fastapi-tutorial` service.
    - Migrate with `ansible.builtin.systemd` using `name: fastapi-tutorial`, `enabled: true`, and `state: started`.
    - Start only after the repository, virtual environment, Python dependencies, PostgreSQL service, PostgreSQL objects, `.env` file, systemd unit, and systemd reload are complete.

## Dependencies

**External cookbook dependencies**: None declared in `metadata.rb`.

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

**Application dependencies**:

- Python packages from `/opt/fastapi-tutorial/requirements.txt`
- Python virtual environment at `/opt/fastapi-tutorial/venv`

**Repository dependency**:

- URL: `https://github.com/dibanez/fastapi_tutorial.git`
- Revision: `main`

## Credentials

**Detection Summary**: 2 credential references detected in 1 recipe file. Both references represent the same PostgreSQL password used in different contexts.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None
- **Path**: None
- **Source file**: `cookbooks/fastapi-tutorial/recipes/default.rb`

### PostgreSQL password used during database creation

- **Variable(s)**: `fastapi_password`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`, line 40
- **Current storage**: Hardcoded in the `CREATE USER` SQL command
- **Usage context**: Sets the password for PostgreSQL role `fastapi`
- **Migration handling**: Store in Ansible Vault or an AAP credential and pass it to `community.postgresql.postgresql_user`.

### PostgreSQL password embedded in the application connection string

- **Variable(s)**: `DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`, lines 48–57
- **Current storage**: Hardcoded in the inline `.env` file content
- **Usage context**: Connects the application to the `fastapi_db` PostgreSQL database
- **Migration handling**: Construct the value from protected variables, use `no_log: true` where appropriate, and consider deploying `.env` with mode `0600` instead of the current `0644`.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, cloud secret manager, TLS certificates, private keys, API tokens, or environment-variable secret lookups were detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Service endpoints to check**:

- **fastapi-tutorial**: `0.0.0.0:8000`
- **fastapi_db**: PostgreSQL on `localhost:5432`

**Database objects to verify**:

- PostgreSQL role `fastapi`
- PostgreSQL database `fastapi_db`
- Database owner `fastapi`

**Templates rendered**:

- `/opt/fastapi-tutorial/.env`: rendered once by an inline Chef `file` resource
- `/etc/systemd/system/fastapi-tutorial.service`: rendered once by an inline Chef `file` resource
- Cookbook templates: none

## Pre-flight checks:

```bash
# Verify installed packages on Debian-family systems
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev 2>/dev/null

# Verify installed packages on Red Hat-family systems
rpm -q python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

# Verify Python and virtual-environment support
python3 --version
python3 -m venv --help >/dev/null

# Verify the fastapi-tutorial application instance
ls -ld /opt/fastapi-tutorial
test -f /opt/fastapi-tutorial/requirements.txt
test -d /opt/fastapi-tutorial/venv
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
git -C /opt/fastapi-tutorial remote -v
git -C /opt/fastapi-tutorial branch --show-current
git -C /opt/fastapi-tutorial rev-parse --verify HEAD
/opt/fastapi-tutorial/venv/bin/pip check

# Verify the PostgreSQL fastapi_db instance
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
ss -ltnp | grep ':5432'
sudo -u postgres psql -tAc "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"
sudo -u postgres psql -tAc "SELECT datname FROM pg_database WHERE datname = 'fastapi_db';"
sudo -u postgres psql -tAc "SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"

# Test PostgreSQL connectivity using an approved protected secret-injection mechanism
PGPASSWORD='<protected-password>' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_database(), current_user;"

# Verify the application environment file without exposing its password
stat -c '%U:%G %a %n' /opt/fastapi-tutorial/.env
grep '^PROJECT_NAME=' /opt/fastapi-tutorial/.env
grep '^API_VERSION=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env

# Verify the fastapi-tutorial systemd instance
systemctl daemon-reload
systemctl cat fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
grep '^After=' /etc/systemd/system/fastapi-tutorial.service
grep '^User=' /etc/systemd/system/fastapi-tutorial.service
grep '^WorkingDirectory=' /etc/systemd/system/fastapi-tutorial.service
grep '^Environment=' /etc/systemd/system/fastapi-tutorial.service
grep '^ExecStart=' /etc/systemd/system/fastapi-tutorial.service
grep '^Restart=' /etc/systemd/system/fastapi-tutorial.service

# Verify the FastAPI listener and endpoint
ps aux | grep '[u]vicorn'
ss -ltnp | grep ':8000'
curl -i http://127.0.0.1:8000/
curl -i http://127.0.0.1:8000/docs
curl -i http://127.0.0.1:8000/openapi.json

# Review logs and restart behavior
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u postgresql --no-pager -n 100
systemctl restart fastapi-tutorial
systemctl is-active fastapi-tutorial
```

Expected results:

- `fastapi-tutorial` is enabled and active.
- The application listens on `0.0.0.0:8000`.
- `fastapi_db` exists and is owned by `fastapi`.
- PostgreSQL is enabled, active, and available on `localhost:5432`.
- The application returns an HTTP response without connection errors.
- Logs contain no Python import errors, missing-package errors, database authentication failures, port-binding failures, or PostgreSQL startup failures.