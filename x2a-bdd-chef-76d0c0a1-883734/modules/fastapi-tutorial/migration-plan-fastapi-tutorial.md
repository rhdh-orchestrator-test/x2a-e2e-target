---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys one FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, and PostgreSQL development packages, creates a Python virtual environment, installs dependencies from `requirements.txt`, creates the PostgreSQL user and database, writes an environment file, and manages the `fastapi-tutorial` systemd service on port `8000`. It supports Debian/Ubuntu and RHEL/Fedora systems and contains one hardcoded PostgreSQL credential.

## Service Type and Instances

**Service Type**: Application Server with PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application served by Uvicorn
  - Location/Path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Python virtual environment: `/opt/fastapi-tutorial/venv`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Service user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Start command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Port/Socket: `0.0.0.0:8000`
  - Restart policy: `always`
  - Systemd dependencies: `network.target` and `postgresql.service`

Supporting PostgreSQL configuration:

- Database user: `fastapi`
- Database name: `fastapi_db`
- Database host: `localhost`
- Database port: `5432`
- Database owner: `fastapi`

## File Structure

Only files participating in the supplied execution tree and structured analysis are listed.

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

No ERB templates are rendered. The `.env` file and systemd unit are created using inline Chef `file` resources.

**Attributes:**
```text
cookbooks/fastapi-tutorial/attributes/default.rb
```

**Files:**
```text
```

No static files from `files/default/` or `files/` are deployed.

## Module Explanation

The cookbook performs operations in the following order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Checks whether the platform belongs to the Fedora/RHEL family.
   - On RHEL/Fedora, installs `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, and `libpq-devel`.
   - On RHEL/Fedora, runs `postgresql-setup --initdb` through `execute[initialize_postgresql]`, guarded by `/var/lib/pgsql/data/PG_VERSION`.
   - On Debian/Ubuntu and other non-Fedora/non-RHEL platforms, installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`—seven packages total.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates `/opt/fastapi-tutorial/venv` with:
     ```bash
     python3 -m venv /opt/fastapi-tutorial/venv
     ```
     guarded by the existence of `/opt/fastapi-tutorial/venv`.
   - Installs Python dependencies using:
     ```bash
     /opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt
     ```
     with working directory `/opt/fastapi-tutorial`.
   - Enables and starts the `postgresql` service.
   - Runs `execute[create_db_user]` to create PostgreSQL user `fastapi`, database `fastapi_db`, and database privileges using the hardcoded password `fastapi_password`.
   - Creates `/opt/fastapi-tutorial/.env` with owner `root`, group `root`, and mode `0644`.
   - Writes the following environment configuration:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Resolves the recipe’s `service_name` to the exact instance name `fastapi-tutorial`.
   - Creates `/etc/systemd/system/fastapi-tutorial.service` with owner `root`, group `root`, and mode `0644`.
   - Configures the systemd service to run as `root`, use `/opt/fastapi-tutorial` as its working directory, use `/opt/fastapi-tutorial/venv/bin` in `PATH`, and execute Uvicorn on `0.0.0.0:8000`.
   - Defines `execute[systemd_reload]` with `systemctl daemon-reload` and action `nothing`; the systemd unit file notifies it immediately when the unit changes.
   - Enables and starts the `fastapi-tutorial` service.
   - No `.each` loops or collection attributes are used; there are no iterable instances to expand.

## Dependencies

**External cookbook dependencies**: None identified in `metadata.rb`.

**System package dependencies**:

RHEL/Fedora:

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

**Application dependency source**:

```text
/opt/fastapi-tutorial/requirements.txt
```

## Credentials

**Detection Summary**: 1 hardcoded database credential detected in 1 recipe file. The credential is used in PostgreSQL creation commands and in the application `DATABASE_URL`.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None
- **Path**: None
- **Data bag, Chef Vault, CyberArk, or external secret manager**: None detected

### PostgreSQL Password

- **Variable(s)**:
  - Password literal: `fastapi_password`
  - Connection string: `DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the recipe and written to `/opt/fastapi-tutorial/.env`
- **Usage context**:
  - Sets the password for PostgreSQL user `fastapi`
  - Authenticates the application to database `fastapi_db`
- **Migration guidance**:
  - Store the password in Ansible Vault or an AAP credential/secret variable.
  - Use the secret for the PostgreSQL user task and for generating `DATABASE_URL`.
  - Do not commit the literal password to the Ansible repository.

No additional data-bag secret, Vault item, CyberArk secret, Conjur variable, TLS certificate, private key, API token, or external database connection string was detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- `/var/lib/pgsql/data/PG_VERSION` on RHEL/Fedora
- PostgreSQL database `fastapi_db`
- PostgreSQL role `fastapi`

**Service endpoints to check**:

- FastAPI: `0.0.0.0:8000`
- PostgreSQL: `localhost:5432`

**Unix sockets**:

- No cookbook-specific Unix socket is configured.
- PostgreSQL may create its platform-default Unix socket.

**Templates rendered**:

- No Chef templates are rendered.
- `/opt/fastapi-tutorial/.env`: created once by an inline `file` resource.
- `/etc/systemd/system/fastapi-tutorial.service`: created once by an inline `file` resource.

## Pre-flight checks:

### Package and platform checks

```bash
python3 --version
python3 -m pip --version
git --version
psql --version
```

On RHEL/Fedora:

```bash
rpm -q python3 python3-pip git postgresql-server postgresql-contrib libpq-devel
test -f /var/lib/pgsql/data/PG_VERSION
```

On Debian/Ubuntu:

```bash
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev
```

### FastAPI instance: `fastapi-tutorial`

```bash
test -d /opt/fastapi-tutorial
test -f /opt/fastapi-tutorial/requirements.txt
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
git -C /opt/fastapi-tutorial rev-parse HEAD
/opt/fastapi-tutorial/venv/bin/pip list
/opt/fastapi-tutorial/venv/bin/python -c "import fastapi; print(fastapi.__version__)"
```

Verify the environment file:

```bash
stat /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' /opt/fastapi-tutorial/.env
ls -l /opt/fastapi-tutorial/.env
```

Expected keys:

```text
PROJECT_NAME="FastAPI Tutorial"
API_VERSION=1.0.0
DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
```

Verify the systemd unit and service:

```bash
systemctl cat fastapi-tutorial
systemctl status fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl show fastapi-tutorial \
  --property=User,WorkingDirectory,ExecStart,Restart,ActiveState,SubState
```

Expected values include:

- `User=root`
- `WorkingDirectory=/opt/fastapi-tutorial`
- Uvicorn under `/opt/fastapi-tutorial/venv/bin/`
- `Restart=always`
- Active state `active`
- Sub-state `running`

Verify the FastAPI endpoint and process:

```bash
ss -ltnp | grep ':8000'
curl -i http://127.0.0.1:8000/
curl -i http://127.0.0.1:8000/health
ps aux | grep '[u]vicorn app.main:app'
```

The application should return an HTTP response, normally `200 OK` for a valid endpoint.

### PostgreSQL service

```bash
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
ss -ltnp | grep ':5432'
```

### PostgreSQL role: `fastapi`

```bash
sudo -u postgres psql -tAc \
  "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"
```

Expected output:

```text
fastapi
```

### PostgreSQL database: `fastapi_db`

```bash
sudo -u postgres psql -tAc \
  "SELECT datname, pg_catalog.pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"
```

Expected output:

```text
fastapi_db | fastapi
```

Verify application credentials:

```bash
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT version();"

PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT 1;"
```

### Logs and restart behavior

```bash
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u postgresql --no-pager -n 100
journalctl -u fastapi-tutorial --no-pager | grep -Ei 'error|failed|traceback'
```

After changing the systemd unit:

```bash
systemctl daemon-reload
systemctl restart fastapi-tutorial
systemctl is-active fastapi-tutorial
```

### Resource and network verification

```bash
systemctl show fastapi-tutorial --property=MainPID,MemoryCurrent,TasksCurrent
ss -ltnp | grep ':8000'
ss -ltnp | grep ':5432'
```

The final state should show:

- `fastapi-tutorial` enabled and running
- FastAPI listening on `0.0.0.0:8000`
- `postgresql` enabled and running
- PostgreSQL available on `localhost:5432`
- Database `fastapi_db` accessible by role `fastapi`