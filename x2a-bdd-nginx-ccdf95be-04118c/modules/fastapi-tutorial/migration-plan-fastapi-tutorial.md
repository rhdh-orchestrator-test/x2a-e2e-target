---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` to `/opt/fastapi-tutorial`, installs Python, Git, PostgreSQL, and related system dependencies, creates a Python virtual environment, installs dependencies from `requirements.txt`, provisions the PostgreSQL database `fastapi_db` and user `fastapi`, writes the application environment file, and manages the `fastapi-tutorial.service` systemd unit. The FastAPI application listens on `0.0.0.0:8000` and depends on the `postgresql` service.

## Service Type and Instances

**Service Type**: Application Server with PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application served by Uvicorn
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Location/Path: `/opt/fastapi-tutorial`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Working directory: `/opt/fastapi-tutorial`
  - Entrypoint: `app.main:app`
  - Bind address: `0.0.0.0`
  - Port/Socket: TCP `8000`
  - Systemd unit: `fastapi-tutorial.service`
  - Service user: `root`
  - Restart policy: `Restart=always`
  - PATH: `/opt/fastapi-tutorial/venv/bin`

- **postgresql**: PostgreSQL database service for the FastAPI application
  - Service name: `postgresql`
  - Managed actions: enable and start
  - Database: `fastapi_db`
  - Database owner: `fastapi`
  - Database user: `fastapi`
  - Database host: `localhost`
  - Port/Socket: Distribution-dependent TCP port and Unix socket
  - Connection string: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`

There are no collection attributes or `.each` iterations in the execution tree. No repeated Chef-managed application or database items require expansion.

## File Structure

The execution tree contains one executed recipe and no custom providers, templates, attribute files, or deployed static files.

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

The cookbook creates `/opt/fastapi-tutorial/.env` and `/etc/systemd/system/fastapi-tutorial.service` using inline Chef `file` resources. These are generated configuration files, not cookbook static files or ERB templates.

## Module Explanation

The cookbook performs operations in this order:

1. **`default`** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the seven system packages `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial` using `git[/opt/fastapi-tutorial]`.
   - Creates the virtual environment with `execute[create_venv]`:
     ```bash
     python3 -m venv /opt/fastapi-tutorial/venv
     ```
     This is skipped when `/opt/fastapi-tutorial/venv` already exists.
   - Installs Python dependencies with `execute[install_dependencies]`:
     ```bash
     /opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt
     ```
     The working directory is `/opt/fastapi-tutorial`. This resource runs during convergence because it has no `creates` guard.
   - Enables and starts `postgresql` using `service[postgresql]`.
   - Creates the PostgreSQL user and database with `execute[create_db_user]`:
     ```bash
     sudo -u postgres psql -c "CREATE USER fastapi WITH PASSWORD 'fastapi_password';" || true
     sudo -u postgres psql -c "CREATE DATABASE fastapi_db OWNER fastapi;" || true
     sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE fastapi_db TO fastapi;" || true
     ```
     The `|| true` suffix suppresses errors, including errors caused by existing objects and unrelated PostgreSQL failures. The migration should preferably use PostgreSQL-specific Ansible modules for idempotent user, database, ownership, and privilege management.
   - Creates `/opt/fastapi-tutorial/.env` with owner `root`, group `root`, and mode `0644`, containing:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Creates `/etc/systemd/system/fastapi-tutorial.service` with owner `root`, group `root`, and mode `0644`, containing:
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
   - Immediately notifies `execute[systemd_reload]` when `/etc/systemd/system/fastapi-tutorial.service` changes.
   - Runs `execute[systemd_reload]` only when notified:
     ```bash
     systemctl daemon-reload
     ```
   - Enables and starts `fastapi-tutorial` using `service[fastapi-tutorial]`.

**Resource execution order:**

1. `package`: one resource containing seven packages
2. `directory`: `/opt/fastapi-tutorial`
3. `git`: `/opt/fastapi-tutorial`
4. `execute[create_venv]`
5. `execute[install_dependencies]`
6. `service[postgresql]`
7. `execute[create_db_user]`
8. `file[/opt/fastapi-tutorial/.env]`
9. `file[/etc/systemd/system/fastapi-tutorial.service]`
10. Deferred notification target `execute[systemd_reload]`, executed immediately when notified
11. `service[fastapi-tutorial]`

There are no custom resources, provider files, recipe includes, loops, ERB templates, or cookbook static-file deployments.

## Dependencies

**External cookbook dependencies**: None declared in the supplied metadata.

**Chef platform support**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

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

**Application dependency source**: `/opt/fastapi-tutorial/requirements.txt`

**Application dependency environment**: `/opt/fastapi-tutorial/venv`

## Credentials

**Detection Summary**: 2 credential references detected in 1 source recipe. Both references represent the same hardcoded PostgreSQL credential.

**Source**:

- **Provider**: Hardcoded in Chef recipe
- **URL**: None
- **Path**: None
- **Secret storage**: Not protected by Chef Vault, encrypted data bags, an external secret manager, or environment-variable lookup

### PostgreSQL Password

- **Variable(s)**: No named Chef attribute variable is used; the literal password is `fastapi_password`.
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in `execute[create_db_user]` and repeated in the `.env` file content.
- **Usage context**:
  ```sql
  CREATE USER fastapi WITH PASSWORD 'fastapi_password';
  ```
  The same password is used in:
  ```text
  postgresql://fastapi:fastapi_password@localhost/fastapi_db
  ```

### Database Connection String

- **Variable(s)**: `DATABASE_URL`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in `/opt/fastapi-tutorial/.env`.
- **Usage context**: Provides the FastAPI application with its PostgreSQL connection string.
- **Value**:
  ```text
  postgresql://fastapi:fastapi_password@localhost/fastapi_db
  ```

No `data_bag_item`, `encrypted_data_bag_item`, `chef_vault_item`, `ChefVault::Item`, `conjur_variable`, CyberArk data bag, Vault attribute namespace, or environment-variable secret lookup was detected.

No TLS certificate, private key, PEM, CRT, or API token reference was detected.

For Ansible, store the PostgreSQL password in Ansible Vault and use the protected variable for both PostgreSQL user creation and `.env` generation.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Database objects to verify**:

- PostgreSQL role: `fastapi`
- PostgreSQL database: `fastapi_db`
- Database owner: `fastapi`

**Service endpoints to check**:

- FastAPI: `0.0.0.0:8000`
- PostgreSQL: Distribution-dependent active TCP port
- PostgreSQL Unix socket: Distribution-dependent; discover with `SHOW unix_socket_directories;`

**Templates rendered**: None. The cookbook uses inline `file` resources rather than ERB templates. Render count: `0`.

**Configuration files created by inline content**:

- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

## Pre-flight checks

### Package and application checks for `fastapi-tutorial`

```bash
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev 2>/dev/null || \
rpm -q python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

ls -ld /opt/fastapi-tutorial
ls -ld /opt/fastapi-tutorial/venv
ls -l /opt/fastapi-tutorial/requirements.txt
```

Verify that all seven packages are installed, `/opt/fastapi-tutorial` is owned by `root:root` with mode `0755`, the virtual environment exists, and `requirements.txt` is present.

### Repository checks for `fastapi-tutorial`

```bash
git -C /opt/fastapi-tutorial remote -v
git -C /opt/fastapi-tutorial branch --show-current
git -C /opt/fastapi-tutorial rev-parse --verify HEAD
```

Verify that the remote is `https://github.com/dibanez/fastapi_tutorial.git` and that the checked-out revision corresponds to `main`.

### Python environment checks for `fastapi-tutorial`

```bash
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip --version
/opt/fastapi-tutorial/venv/bin/pip check
/opt/fastapi-tutorial/venv/bin/python -c "import fastapi; print(fastapi.__version__)"
/opt/fastapi-tutorial/venv/bin/python -c "import uvicorn; print(uvicorn.__version__)"
```

Verify that Python and pip execute from `/opt/fastapi-tutorial/venv`, `pip check` reports no broken requirements, and both `fastapi` and `uvicorn` can be imported.

### PostgreSQL service checks for `postgresql`

```bash
systemctl status postgresql --no-pager
systemctl is-enabled postgresql
systemctl is-active postgresql
```

Verify that `postgresql` is enabled and active.

### PostgreSQL role and database checks for `postgresql`

```bash
sudo -u postgres psql -d postgres -c "\du fastapi"
sudo -u postgres psql -d postgres -c "\l+ fastapi_db"
```

Verify that role `fastapi` exists, database `fastapi_db` exists, and `fastapi` owns the database.

Test application-user connectivity:

```bash
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_user, current_database();"
```

Expected result:

```text
 current_user | current_database
--------------+-----------------
 fastapi      | fastapi_db
```

Check the PostgreSQL version, port, and socket directory:

```bash
sudo -u postgres psql -d fastapi_db -c "SELECT version();"
sudo -u postgres psql -d fastapi_db -c "SHOW port;"
sudo -u postgres psql -d fastapi_db -c "SHOW unix_socket_directories;"
```

### Environment file checks for `fastapi-tutorial`

```bash
stat -c '%U:%G %a %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' /opt/fastapi-tutorial/.env
```

Expected configuration:

```text
PROJECT_NAME="FastAPI Tutorial"
API_VERSION=1.0.0
DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
```

The original Chef mode is `0644`. Because the file contains a database password, verify that the migrated file meets the security requirement; a hardened Ansible migration should use mode `0600`.

### Systemd unit checks for `fastapi-tutorial`

```bash
systemctl cat fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl status fastapi-tutorial --no-pager
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
```

Verify that the unit contains:

```text
After=network.target postgresql.service
User=root
WorkingDirectory=/opt/fastapi-tutorial
Environment="PATH=/opt/fastapi-tutorial/venv/bin"
ExecStart=/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
```

Verify that the unit is enabled and active and that no systemd syntax errors are reported.

### FastAPI endpoint checks for `fastapi-tutorial`

```bash
curl -I http://127.0.0.1:8000/
ss -tlnp | grep ':8000'
lsof -iTCP:8000 -sTCP:LISTEN
ps aux | grep '[u]vicorn app.main:app'
```

Verify that Uvicorn listens on TCP port `8000` and that the running command uses:

```text
/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The exact HTTP status for `/` depends on the routes in the repository.

### Logs and restart behavior for `postgresql` and `fastapi-tutorial`

```bash
journalctl -u postgresql --no-pager -n 50
journalctl -u fastapi-tutorial --no-pager -n 50
systemctl show fastapi-tutorial -p Restart -p User -p WorkingDirectory
```

Expected values for `fastapi-tutorial`:

```text
Restart=always
User=root
WorkingDirectory=/opt/fastapi-tutorial
```

### Systemd reload check for `fastapi-tutorial`

After changing the unit file, verify the daemon reload behavior:

```bash
sudo systemctl daemon-reload
systemctl show fastapi-tutorial --no-pager
```

The Ansible unit deployment task should notify the daemon-reload handler only when `/etc/systemd/system/fastapi-tutorial.service` changes, then ensure `fastapi-tutorial` is enabled and started.