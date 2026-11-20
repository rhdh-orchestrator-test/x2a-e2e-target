---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, and PostgreSQL development dependencies; creates a Python virtual environment; installs `requirements.txt`; initializes and starts PostgreSQL; creates the `fastapi` PostgreSQL user and `fastapi_db` database; writes the application configuration to `/opt/fastapi-tutorial/.env`; and creates and starts the `fastapi-tutorial` systemd service on TCP port `8000`. The supplied analysis references four attributes but does not include the contents of `attributes/default.rb`, so their values cannot be independently verified.

## Service Type and Instances

**Service Type**: Application Server

The deployed application is a FastAPI application launched with Uvicorn. PostgreSQL is a required database service dependency.

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application service
  - Location/Path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Startup command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Listen address: `0.0.0.0`
  - Port/Socket: TCP `8000`
  - Run user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Restart policy: `always`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`

- **postgresql**: PostgreSQL database service for the FastAPI application
  - Database user: `fastapi`
  - Database password: `fastapi_password`
  - Database name: `fastapi_db`
  - Host: `localhost`
  - Port/Socket: TCP `5432` and the platform-specific PostgreSQL Unix socket
  - Database URL: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`

No collection attributes or `.each` loops are present in the cookbook.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

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
cookbooks/fastapi-tutorial/attributes/default.rb
```

**Files:**
```text
```

No custom providers, ERB templates, or static files are used. Configuration files are generated directly with Chef `file` resources.

## Attributes

The analysis references the following attributes in `cookbooks/fastapi-tutorial/recipes/default.rb`, but does not provide the analyzed definitions or values from `cookbooks/fastapi-tutorial/attributes/default.rb`. The values below are therefore reported as referenced or resolved values from the migration plan and cannot be independently verified:

| Attribute | Referenced value | Ansible equivalent |
|---|---|---|
| `node['fastapi_tutorial']['app_path']` | `/opt/fastapi-tutorial` | `fastapi_tutorial_app_path` |
| `node['fastapi_tutorial']['repository']` | `https://github.com/dibanez/fastapi_tutorial.git` | `fastapi_tutorial_repository` |
| `node['fastapi_tutorial']['revision']` | `main` | `fastapi_tutorial_revision` |
| `node['fastapi_tutorial']['service_port']` | `8000` | `fastapi_tutorial_service_port` |

No package versions are pinned. The migration should use the target platform package manager's available versions unless explicit version pinning is added.

## Module Explanation

The cookbook performs operations in this order:

1. **`default`** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - On RHEL/Fedora-family systems, install `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, and `libpq-devel`.
   - On RHEL/Fedora-family systems, run `postgresql-setup --initdb` only when `/var/lib/pgsql/data/PG_VERSION` does not exist.
   - On non-RHEL/Fedora systems, including supported Ubuntu systems, install `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Create `/opt/fastapi-tutorial` as `root:root` with mode `0755` and recursive creation enabled.
   - Synchronize `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Create `/opt/fastapi-tutorial/venv` with `python3 -m venv /opt/fastapi-tutorial/venv`, guarded by the virtual-environment path.
   - Install dependencies from `/opt/fastapi-tutorial/requirements.txt` into the virtual environment. The original command is `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt`, run with `/opt/fastapi-tutorial` as the working directory. An idempotent migration should preferably use `ansible.builtin.pip` with the requirements file and virtual environment.
   - Enable and start the `postgresql` service.
   - Create the PostgreSQL user `fastapi` with password `fastapi_password`, create the `fastapi_db` database owned by `fastapi`, and grant all privileges on `fastapi_db` to `fastapi`. Use `community.postgresql.postgresql_user`, `community.postgresql.postgresql_db`, and, if required, `community.postgresql.postgresql_privs` rather than reproducing the original broadly suppressive `|| true` shell commands.
   - Write `/opt/fastapi-tutorial/.env` with owner `root`, group `root`, and mode `0644`:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Write `/etc/systemd/system/fastapi-tutorial.service` with owner `root`, group `root`, and mode `0644`:
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
   - Reload systemd with `systemctl daemon-reload` only when `/etc/systemd/system/fastapi-tutorial.service` changes.
   - Enable and start the `fastapi-tutorial` systemd service.

There are no additional recipes, providers, templates, static files, or `.each` iterations. The analyzed recipe contains 13 resources and is the only executed recipe.

## Dependencies

**External cookbook dependencies**: None listed in `metadata.rb`.

**System package dependencies**:

RHEL/Fedora branch:

- `python3`
- `python3-pip`
- `git`
- `postgresql-server`
- `postgresql-contrib`
- `libpq-devel`

Non-RHEL/Fedora branch:

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

The FastAPI systemd unit declares `After=network.target postgresql.service`.

## Credentials

**Detection Summary**: 1 credential detected in 2 source locations within `cookbooks/fastapi-tutorial/recipes/default.rb`.

**Source**:

- **Provider**: None detected; the credential is not stored in Chef Vault, an encrypted data bag, CyberArk, HashiCorp Vault, AWS Secrets Manager, or an environment variable.
- **URL**: None
- **Path**: `cookbooks/fastapi-tutorial/recipes/default.rb:49` and `cookbooks/fastapi-tutorial/recipes/default.rb:61`

### Database Password for PostgreSQL User `fastapi`

- **Variable(s)**: No Chef attribute variable is used. The hardcoded password is `fastapi_password`.
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb:49`
  - `cookbooks/fastapi-tutorial/recipes/default.rb:61`
- **Current storage**: Hardcoded in the recipe and embedded in the generated `/opt/fastapi-tutorial/.env` database URL.
- **Usage context**:
  - PostgreSQL `CREATE USER` command.
  - FastAPI `DATABASE_URL` connection string:
    `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Migration handling**: Store the password in Ansible Vault or another approved secret-management system. Generate the `.env` file from the protected variable rather than embedding `fastapi_password` directly.

No TLS certificate, private key, API key, token, `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, `conjur_variable`, or CyberArk integration was detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/fastapi-tutorial/recipes/default.rb`
- `cookbooks/fastapi-tutorial/attributes/default.rb`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/app/main.py`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- `/var/lib/pgsql/data/PG_VERSION` on RHEL/Fedora systems
- Platform-specific PostgreSQL data paths on non-RHEL systems

**Service endpoints to check**:

- **fastapi-tutorial**: HTTP on `0.0.0.0:8000`
- **postgresql**: Local TCP endpoint on `localhost:5432`
- **postgresql**: Platform-specific PostgreSQL Unix socket

**Templates rendered**:

- None. No ERB templates are used.
- `/opt/fastapi-tutorial/.env`: direct file resource, rendered once
- `/etc/systemd/system/fastapi-tutorial.service`: direct file resource, rendered once

## Pre-flight checks

### Platform and package checks

```bash
cat /etc/os-release
command -v python3
command -v git
command -v psql
command -v uvicorn
python3 --version
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
```

### PostgreSQL instance: `postgresql`

```bash
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
ss -tlnp | grep ':5432'
sudo -u postgres psql -c "SELECT version();"
sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='fastapi';"
sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='fastapi_db';"
sudo -u postgres psql -tAc \
  "SELECT pg_catalog.pg_get_userbyid(datdba) FROM pg_database WHERE datname='fastapi_db';"
PGPASSWORD='fastapi_password' \
  psql -h localhost -U fastapi -d fastapi_db -c "SELECT version();"
PGPASSWORD='fastapi_password' \
  psql -h localhost -U fastapi -d fastapi_db -c "SELECT 1;"
```

### FastAPI instance: `fastapi-tutorial`

```bash
ls -ld /opt/fastapi-tutorial
test -f /opt/fastapi-tutorial/requirements.txt
test -f /opt/fastapi-tutorial/app/main.py
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' \
  /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=postgresql://fastapi:.*@localhost/fastapi_db$' \
  /opt/fastapi-tutorial/.env

systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
grep -E '^(After=|User=|WorkingDirectory=|Environment=|ExecStart=|Restart=)' \
  /etc/systemd/system/fastapi-tutorial.service
systemctl daemon-reload
systemctl status fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
ps aux | grep '[u]vicorn'
ss -tlnp | grep ':8000'

curl -i http://127.0.0.1:8000/
curl -i http://127.0.0.1:8000/openapi.json
curl -i http://127.0.0.1:8000/docs
```

Expected result: `fastapi-tutorial` is enabled and active, Uvicorn is listening on TCP port `8000`, and the HTTP endpoints return responses from the FastAPI application.

### Service logs and diagnostics

```bash
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u fastapi-tutorial -f
journalctl -u postgresql --no-pager -n 100
systemctl --failed
```

### File, permission, and import checks

```bash
ls -l /etc/systemd/system/fastapi-tutorial.service
ls -l /opt/fastapi-tutorial/.env
ls -ld /opt/fastapi-tutorial/venv

cd /opt/fastapi-tutorial
/opt/fastapi-tutorial/venv/bin/python -c \
  "import app.main; print('app.main import succeeded')"
```