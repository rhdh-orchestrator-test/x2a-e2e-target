---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main`, installs Python, Git, PostgreSQL, and PostgreSQL development dependencies, creates a Python virtual environment, installs application requirements, provisions the PostgreSQL user `fastapi` and database `fastapi_db`, writes `/opt/fastapi-tutorial/.env`, and runs the application with Uvicorn through systemd. The `fastapi-tutorial` instance listens on `0.0.0.0:8000` and depends on the `postgresql` service on port `5432`. The database password is hardcoded in the Chef recipe and must be migrated to Ansible Vault or another approved secret-management system.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application served by Uvicorn
  - Application directory: `/opt/fastapi-tutorial`
  - Source repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Git revision: `main`
  - Python virtual environment: `/opt/fastapi-tutorial/venv`
  - Working directory: `/opt/fastapi-tutorial`
  - Process command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Listen address: `0.0.0.0`
  - Port: `8000`
  - Runtime user: `root`
  - Restart behavior: `Restart=always`
  - Environment file: `/opt/fastapi-tutorial/.env`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`

- **postgresql**: PostgreSQL database service for the FastAPI application
  - Service name: `postgresql`
  - Database user: `fastapi`
  - Database: `fastapi_db`
  - Database owner: `fastapi`
  - Host: `localhost`
  - Port: `5432` by PostgreSQL default
  - Connection URL: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`

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

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the operating-system packages `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates the virtual environment with `python3 -m venv /opt/fastapi-tutorial/venv` when `/opt/fastapi-tutorial/venv` does not exist.
   - Installs dependencies from `/opt/fastapi-tutorial/requirements.txt` using `/opt/fastapi-tutorial/venv/bin/pip`.
   - Enables and starts the `postgresql` service.
   - Creates the PostgreSQL user `fastapi` with password `fastapi_password`.
   - Creates the PostgreSQL database `fastapi_db` owned by `fastapi`.
   - Grants `fastapi` all privileges on `fastapi_db`.
   - Writes `/opt/fastapi-tutorial/.env` with owner `root`, group `root`, and mode `0644`. The file contains:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Writes `/etc/systemd/system/fastapi-tutorial.service` with owner `root`, group `root`, and mode `0644`.
   - Configures the systemd unit to run as `root` from `/opt/fastapi-tutorial`, use `/opt/fastapi-tutorial/venv/bin` in `PATH`, execute Uvicorn on `0.0.0.0:8000`, restart automatically, start after `network.target`, and order after `postgresql.service`.
   - Runs `systemctl daemon-reload` immediately when `/etc/systemd/system/fastapi-tutorial.service` changes.
   - Enables and starts the `fastapi-tutorial` systemd service.
   - Iterations: None. The recipe contains no `.each` loops or iterable collection attributes.

## Dependencies

**External cookbook dependencies**: None listed in `metadata.rb`.

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

**Application dependency source**:

- Repository: `https://github.com/dibanez/fastapi_tutorial.git`
- Revision: `main`
- Requirements file: `/opt/fastapi-tutorial/requirements.txt`

**Runtime dependency ordering**:

```text
system packages
  → /opt/fastapi-tutorial
  → repository checkout
  → Python virtual environment
  → Python dependencies
  → postgresql service
  → PostgreSQL user and database
  → /opt/fastapi-tutorial/.env
  → /etc/systemd/system/fastapi-tutorial.service
  → systemd daemon reload
  → fastapi-tutorial service
```

## Credentials

**Detection Summary**: 1 database credential detected in 1 recipe file. The password is used both in the PostgreSQL user-creation command and in the application database URL.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None
- **Path**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Secret value**: `fastapi_password`

### PostgreSQL password

- **Variable(s)**:
  - PostgreSQL user password: `fastapi_password`
  - Database URL: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded plaintext in the Chef recipe and rendered into `/opt/fastapi-tutorial/.env`
- **Usage context**:
  - Sets the password for PostgreSQL user `fastapi`.
  - Authenticates the FastAPI application to database `fastapi_db`.
- **Migration requirement**:
  - Store the password in Ansible Vault or an approved external secret provider, such as `fastapi_db_password`.
  - Use the protected variable when creating the PostgreSQL user.
  - Use the same protected variable when rendering `DATABASE_URL`.
  - Apply `no_log: true` to tasks that could expose the secret.
  - Prefer mode `0600` for `/opt/fastapi-tutorial/.env`; the Chef configuration currently uses mode `0644`.

No Chef data bags, encrypted data bags, Chef Vault calls, CyberArk integrations, Conjur variables, environment-variable secret lookups, TLS certificates, API tokens, or SSH keys were detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/fastapi-tutorial/recipes/default.rb`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/requirements.txt`
- The repository source implementing the `app.main:app` import target

**Service endpoints to check**:

- `fastapi-tutorial`: `http://127.0.0.1:8000/`
- `fastapi-tutorial`: TCP `8000`
- `postgresql`: TCP `5432`
- PostgreSQL local Unix socket: platform default, not explicitly configured

**Templates rendered**: None. The cookbook uses inline `file` resources and contains no `.erb` templates.

**Services to verify**:

- `postgresql`
- `fastapi-tutorial`

## Pre-flight checks

### Package and application layout

```bash
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev
ls -ld /opt/fastapi-tutorial
ls -ld /opt/fastapi-tutorial/venv
test -f /opt/fastapi-tutorial/requirements.txt
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn
```

On RPM-based systems, use the equivalent `rpm -q` package checks.

### `postgresql` instance

```bash
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
ss -tlnp | grep ':5432'
```

Verify the PostgreSQL user:

```bash
sudo -u postgres psql -tAc "SELECT usename FROM pg_user WHERE usename = 'fastapi';"
```

Expected result:

```text
fastapi
```

Verify the database and owner:

```bash
sudo -u postgres psql -tAc "SELECT datname FROM pg_database WHERE datname = 'fastapi_db';"
sudo -u postgres psql -tAc "SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"
```

Expected results:

```text
fastapi_db
fastapi
```

Verify application connectivity:

```bash
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT 1;"
```

Expected result: a successful query returning `1`.

### `fastapi-tutorial` instance

Verify the environment file:

```bash
ls -l /opt/fastapi-tutorial/.env
grep '^PROJECT_NAME=' /opt/fastapi-tutorial/.env
grep '^API_VERSION=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env | sed 's/:\/\/[^:]*:[^@]*@/:\/\/***:***@/'
```

Verify the systemd unit:

```bash
systemctl daemon-reload
systemctl status fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl cat fastapi-tutorial
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
```

Check required unit properties:

```bash
systemctl show fastapi-tutorial \
  --property=User,WorkingDirectory,ExecStart,Restart,FragmentPath
```

Expected values include:

```text
User=root
WorkingDirectory=/opt/fastapi-tutorial
ExecStart=/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
FragmentPath=/etc/systemd/system/fastapi-tutorial.service
```

Verify the HTTP endpoint and listening socket:

```bash
curl -i http://127.0.0.1:8000/
ss -tlnp | grep ':8000'
ps aux | grep '[u]vicorn'
```

Expected result: a Uvicorn or Python process listens on `0.0.0.0:8000`, and the endpoint returns an HTTP response. The exact status code depends on the repository's route definitions.

Review application logs:

```bash
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u fastapi-tutorial -f
```

Confirm successful Uvicorn startup, successful import of `app.main:app`, absence of Python tracebacks, absence of PostgreSQL authentication failures, and successful binding to port `8000`.