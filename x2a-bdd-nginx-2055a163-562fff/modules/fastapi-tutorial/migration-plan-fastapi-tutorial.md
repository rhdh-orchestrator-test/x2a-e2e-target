---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook provisions the `fastapi-tutorial` FastAPI application from the `main` branch of `https://github.com/dibanez/fastapi_tutorial.git`. It installs Python, Git, PostgreSQL, and development dependencies; creates a Python virtual environment; installs application requirements; configures a local PostgreSQL user and database; writes an inline `.env` file containing the database connection string; and manages the application with a systemd service listening on port `8000`. The cookbook contains one executed recipe, no custom resources or providers, no templates, and no static files.

## Service Type and Instances

**Service Type**: Application Server with PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application server
  - Application path: `/opt/fastapi-tutorial`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Run user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - systemd unit: `fastapi-tutorial.service`
  - Listen address: `0.0.0.0`
  - Port: `8000`
  - Application command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Restart policy: `Restart=always`

- **postgresql**: Local PostgreSQL database service
  - Database host: `localhost`
  - Database user: `fastapi`
  - Database name: `fastapi_db`
  - Database owner: `fastapi`
  - Connection string: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`

No collection attributes or `.each` loops are present. There are no additional application, database, or service instances to expand.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**
```text
recipes/default.rb
```

**Providers:**

None.

**Templates:**

None. The `.env` file and systemd unit are created with inline Chef `file` resources rather than `.erb` templates.

**Attributes:**

None.

**Files:**

None. No `cookbook_file` or `remote_file` resources are used.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the following seven system packages with one `package` resource:
     - `python3`
     - `python3-pip`
     - `python3-venv`
     - `git`
     - `postgresql`
     - `postgresql-contrib`
     - `libpq-dev`
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes the Git repository `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates the virtual environment with `execute[create_venv]`:
     ```bash
     python3 -m venv /opt/fastapi-tutorial/venv
     ```
     This uses `creates: /opt/fastapi-tutorial/venv`.
   - Installs Python dependencies with `execute[install_dependencies]`:
     ```bash
     /opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt
     ```
     The working directory is `/opt/fastapi-tutorial`.
   - Enables and starts `service[postgresql]`.
   - Creates the PostgreSQL user, database, owner relationship, and privileges with `execute[create_db_user]`:
     ```bash
     sudo -u postgres psql -c "CREATE USER fastapi WITH PASSWORD 'fastapi_password';" || true
     sudo -u postgres psql -c "CREATE DATABASE fastapi_db OWNER fastapi;" || true
     sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE fastapi_db TO fastapi;" || true
     ```
     Existing-user and existing-database errors are suppressed by `|| true`.
   - Writes `/opt/fastapi-tutorial/.env` with owner `root`, group `root`, and mode `0644`:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Writes `/etc/systemd/system/fastapi-tutorial.service` with owner `root`, group `root`, and mode `0644`:
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
     The file immediately notifies `execute[systemd_reload]` when its content changes.
   - Defines `execute[systemd_reload]` with action `nothing`:
     ```bash
     systemctl daemon-reload
     ```
     It runs only when notified by the systemd unit file resource.
   - Enables and starts `service[fastapi-tutorial]`.

   **Resource summary:**
   - `package`: 1 resource containing 7 package names
   - `directory`: 1 resource
   - `git`: 1 resource
   - `execute`: 4 resources:
     - `create_venv`
     - `install_dependencies`
     - `create_db_user`
     - `systemd_reload`
   - `service`: 2 resources:
     - `postgresql`
     - `fastapi-tutorial`
   - `file`: 2 resources:
     - `/opt/fastapi-tutorial/.env`
     - `/etc/systemd/system/fastapi-tutorial.service`

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

Package names may require OS-family-specific handling during Ansible migration, particularly `libpq-dev` versus the equivalent PostgreSQL development package on Red Hat-family systems. The cookbook supports Ubuntu `>= 18.04` and CentOS `>= 7.0`.

**Service dependencies**:

- `postgresql`
  - Enabled and started by the recipe.
- `fastapi-tutorial`
  - Enabled and started by the recipe.
  - Declares `After=network.target postgresql.service`.

**Application dependency source**:

- Repository: `https://github.com/dibanez/fastapi_tutorial.git`
- Revision: `main`
- Requirements file: `/opt/fastapi-tutorial/requirements.txt`

## Credentials

**Detection Summary**: 1 credential detected in 1 recipe file. The same password is used for the PostgreSQL user and in the generated `DATABASE_URL`.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None
- **Path**: None

### PostgreSQL Application Password

- **Variable(s)**:
  - PostgreSQL password: `fastapi_password`
  - Database URL: `DATABASE_URL`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the recipe and copied into `/opt/fastapi-tutorial/.env`
- **Usage context**:
  - Sets the password for PostgreSQL user `fastapi`.
  - Authenticates the FastAPI application to database `fastapi_db`.
  - Appears in:
    ```text
    postgresql://fastapi:fastapi_password@localhost/fastapi_db
    ```

The migration should store the password in Ansible Vault, use the vaulted value for both the PostgreSQL user task and `.env` content, apply `no_log: true` to credential-bearing tasks, and preferably restrict `.env` to mode `0600`. Retaining mode `0644` is required for literal Chef equivalence but exposes the password to all local users.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, external secret-manager URLs, environment-variable secret references, TLS certificates, API keys, or tokens were detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/fastapi-tutorial/recipes/default.rb`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- Repository-provided application module used by `app.main:app`

PostgreSQL data and log paths are distribution-managed and are not explicitly created by this cookbook.

**Service endpoints to check**:

- FastAPI HTTP endpoint: `0.0.0.0:8000`
- PostgreSQL endpoint: `localhost`
- PostgreSQL Unix socket: distribution-dependent and not explicitly configured

**Templates rendered**:

- None
- Inline file `/opt/fastapi-tutorial/.env`: 1 file resource
- Inline systemd unit `/etc/systemd/system/fastapi-tutorial.service`: 1 file resource

## Pre-flight checks

### Package and virtual-environment checks

```bash
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev 2>/dev/null || \
rpm -q python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -f /opt/fastapi-tutorial/requirements.txt
```

### Application instance: fastapi-tutorial

```bash
test -d /opt/fastapi-tutorial
git -C /opt/fastapi-tutorial remote -v
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
git -C /opt/fastapi-tutorial status --short

test -f /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' /opt/fastapi-tutorial/.env

test -f /etc/systemd/system/fastapi-tutorial.service
systemctl cat fastapi-tutorial
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service

systemctl daemon-reload
systemctl status fastapi-tutorial --no-pager
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial

curl -i http://127.0.0.1:8000/
ss -tlnp | grep ':8000'
ps aux | grep '[u]vicorn app.main:app'
journalctl -u fastapi-tutorial --no-pager -n 100
```

Expected application configuration:

```text
PROJECT_NAME="FastAPI Tutorial"
API_VERSION=1.0.0
DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
```

Expected service state:

```text
enabled
active
running
```

Expected Uvicorn command:

```text
/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Expected listener:

```text
0.0.0.0:8000
```

### Database instance: postgresql

```bash
systemctl status postgresql --no-pager
systemctl is-enabled postgresql
systemctl is-active postgresql

sudo -u postgres psql -tAc \
  "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"

sudo -u postgres psql -tAc \
  "SELECT datname, pg_catalog.pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"

PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT version();"

PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_database(), current_user;"

journalctl -u postgresql --no-pager -n 100
```

Expected role:

```text
fastapi
```

Expected database owner:

```text
fastapi_db | fastapi
```

Expected connection identity:

```text
fastapi_db | fastapi
```

### Configuration and security checks

```bash
stat -c '%a %U:%G %n' \
  /opt/fastapi-tutorial \
  /opt/fastapi-tutorial/.env \
  /etc/systemd/system/fastapi-tutorial.service

systemctl --failed
```

Literal Chef-equivalent permissions:

```text
755 root:root /opt/fastapi-tutorial
644 root:root /opt/fastapi-tutorial/.env
644 root:root /etc/systemd/system/fastapi-tutorial.service
```

Because `.env` contains the PostgreSQL password, verify whether the migration intentionally retains mode `0644` or applies the recommended hardened mode `0600`.