---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI tutorial application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, and PostgreSQL development packages; initializes and starts PostgreSQL; creates the `fastapi` PostgreSQL role and `fastapi_db` database; creates a Python virtual environment; installs application requirements; writes the database connection environment file; and creates and starts the `fastapi-tutorial` systemd service on TCP port `8000`.

## Service Type and Instances

**Service Type**: Application Server with a local PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application served by Uvicorn
  - Application path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Git revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Service user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Process command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Listening address: `0.0.0.0`
  - Port: `8000`
  - Restart policy: `Restart=always`
  - PostgreSQL dependency: `postgresql.service`

- **postgresql**: Local PostgreSQL database service
  - Service name: `postgresql`
  - Database role: `fastapi`
  - Database: `fastapi_db`
  - Database owner: `fastapi`
  - Local connection host: `localhost`

The cookbook has no collection attributes and no `.each` loops.

## File Structure

Only the following cookbook files are used by the analyzed execution flow.

**Recipes:**

```text
cookbooks/fastapi-tutorial/recipes/default.rb
```

**Providers:**

```text
```

No custom Chef resources or provider files are used.

**Templates:**

```text
```

No ERB templates are rendered. Configuration is written using inline Chef `file` resources.

**Attributes:**

```text
cookbooks/fastapi-tutorial/attributes/default.rb
```

**Files:**

```text
```

No static files from `files/` are deployed by `cookbook_file` or `remote_file`.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Loads the default attributes from `cookbooks/fastapi-tutorial/attributes/default.rb`:
     - `node['fastapi_tutorial']['app_path']`: `/opt/fastapi-tutorial`
     - `node['fastapi_tutorial']['repository']`: `https://github.com/dibanez/fastapi_tutorial.git`
     - `node['fastapi_tutorial']['revision']`: `main`
     - `node['fastapi_tutorial']['service_port']`: `8000`
   - Installs platform-specific system packages.
     - Fedora/RHEL packages:
       - `python3`
       - `python3-pip`
       - `git`
       - `postgresql-server`
       - `postgresql-contrib`
       - `libpq-devel`
     - Debian/Ubuntu packages:
       - `python3`
       - `python3-pip`
       - `python3-venv`
       - `git`
       - `postgresql`
       - `postgresql-contrib`
       - `libpq-dev`
   - On Fedora/RHEL, runs `postgresql-setup --initdb` only when `/var/lib/pgsql/data/PG_VERSION` does not exist.
   - Creates `/opt/fastapi-tutorial` as a recursive `0755` directory owned by `root:root`.
   - Synchronizes the Git repository into `/opt/fastapi-tutorial` at revision `main`.
   - Creates `/opt/fastapi-tutorial/venv` with:
     ```bash
     python3 -m venv /opt/fastapi-tutorial/venv
     ```
     The virtual environment is created only when `/opt/fastapi-tutorial/venv` does not already exist.
   - Installs application requirements using:
     ```bash
     /opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt
     ```
     with `/opt/fastapi-tutorial` as the working directory. The Chef action is unconditional and should be represented in Ansible as an installation that is rerun when the checked-out revision changes.
   - Enables and starts the `postgresql` service.
   - Creates the PostgreSQL role and database:
     - Role: `fastapi`
     - Password: `fastapi_password`
     - Database: `fastapi_db`
     - Owner: `fastapi`
     - Privileges: `ALL` on `fastapi_db` for `fastapi`
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
   - Notifies `execute[systemd_reload]` immediately when the systemd unit changes.
   - Runs `systemctl daemon-reload` only when notified.
   - Enables and starts the `fastapi-tutorial` service.
   - There are no `.each` iterations or additional recipes.

## Dependencies

**External cookbook dependencies**: None declared.

**System package dependencies**:

Fedora/RHEL:

- `python3`
- `python3-pip`
- `git`
- `postgresql-server`
- `postgresql-contrib`
- `libpq-devel`

Debian/Ubuntu:

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

- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`

The cookbook metadata supports Ubuntu `>= 18.04` and CentOS `>= 7.0`.

## Credentials

**Detection Summary**: 1 database credential detected in 1 file.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None detected
- **Path**: None detected

### PostgreSQL application password

- **Variable(s)**: No Chef attribute variable is used. The password is hardcoded as `fastapi_password`.
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the PostgreSQL user creation command and repeated in `/opt/fastapi-tutorial/.env`.
- **Usage context**:
  - PostgreSQL role creation:
    ```sql
    CREATE USER fastapi WITH PASSWORD 'fastapi_password';
    ```
  - Application database connection:
    ```text
    DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
    ```

The Ansible migration should store this password in Ansible Vault or an AAP credential/injected secret. It should not remain plaintext in role defaults, task files, or committed `.env` content. If the generated `.env` file continues to contain the password, restrictive permissions should be used and the change from the cookbook’s `0644` mode should be documented.

No Chef data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, cloud secret manager references, environment-variable secret lookups, TLS certificates, private keys, or API tokens were detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- `/var/lib/pgsql/data/PG_VERSION` on Fedora/RHEL

**Database objects to verify**:

- PostgreSQL role `fastapi`
- PostgreSQL database `fastapi_db`
- Database owner `fastapi`
- `ALL` privileges on `fastapi_db` for `fastapi`

**Service endpoints to check**:

- FastAPI: `0.0.0.0:8000`
- PostgreSQL: local `postgresql` service using `localhost`
- Unix sockets: no explicit socket path configured

**Templates rendered**:

- None; no ERB templates are used.

**Configuration files written**:

- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Template render counts**:

- No templates rendered.

## Pre-flight checks:

### Application instance: `fastapi-tutorial`

```bash
test -d /opt/fastapi-tutorial
git -C /opt/fastapi-tutorial rev-parse --is-inside-work-tree
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
test -f /opt/fastapi-tutorial/requirements.txt
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn

systemctl cat fastapi-tutorial
systemctl status fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl show fastapi-tutorial \
  --property=User,WorkingDirectory,ExecStart,Restart

systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service

ss -tlnp | grep ':8000'
curl -I http://127.0.0.1:8000/
curl -sS http://127.0.0.1:8000/
ps aux | grep '[u]vicorn app.main:app'
```

Expected application results:

- `/opt/fastapi-tutorial` exists and is a valid Git working tree.
- The checkout is on or resolves to the configured `main` revision.
- `requirements.txt`, Python, pip, and Uvicorn exist.
- `fastapi-tutorial` is enabled and active.
- The service runs as `root` with working directory `/opt/fastapi-tutorial`.
- Uvicorn runs `app.main:app` from `/opt/fastapi-tutorial/venv/bin`.
- TCP port `8000` is listening on `0.0.0.0`.
- HTTP requests do not fail with a connection-refused error.

### Database instance: `postgresql`

```bash
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
```

On Fedora/RHEL:

```bash
rpm -q python3 python3-pip git postgresql-server postgresql-contrib libpq-devel
test -f /var/lib/pgsql/data/PG_VERSION
```

On Debian/Ubuntu:

```bash
dpkg-query -W python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev
```

Expected PostgreSQL results:

- The `postgresql` service is enabled and active.
- PostgreSQL accepts local connections.
- Fedora/RHEL has an initialized data directory.

### PostgreSQL role and database

```bash
sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='fastapi';"
sudo -u postgres psql -tAc "SELECT datname FROM pg_database WHERE datname='fastapi_db';"
sudo -u postgres psql -tAc "SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname='fastapi_db';"
sudo -u postgres psql -d fastapi_db -c "SELECT current_database(), current_user;"
```

Expected results:

- The role query returns `1`.
- The database query returns `fastapi_db`.
- The owner query returns `fastapi`.
- A connection to `fastapi_db` succeeds.

Validate the application credentials:

```bash
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT version();"
```

### Environment file

```bash
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' /opt/fastapi-tutorial/.env
stat -c '%U %G %a %n' /opt/fastapi-tutorial/.env
```

Expected values:

```text
PROJECT_NAME="FastAPI Tutorial"
API_VERSION=1.0.0
DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
```

The cookbook specifies:

```text
root root 644 /opt/fastapi-tutorial/.env
```

### Logs and reload behavior

```bash
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u postgresql --no-pager -n 100
```

Check for Uvicorn startup, successful binding to `0.0.0.0:8000`, PostgreSQL connection errors, missing Python modules, failures importing `app.main:app`, and PostgreSQL startup or initialization failures.

After changing the systemd unit:

```bash
systemctl daemon-reload
systemctl restart fastapi-tutorial
systemctl status fastapi-tutorial
```

The intended migration behavior is:

1. Write or update `/etc/systemd/system/fastapi-tutorial.service`.
2. Notify the systemd daemon reload handler.
3. Enable and start `fastapi-tutorial`.
4. Verify that port `8000` is listening.