---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI Tutorial application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, and PostgreSQL development libraries; creates a Python virtual environment; installs application dependencies; creates the `fastapi` PostgreSQL role and `fastapi_db` database; writes an environment file containing the database connection string; and manages the `fastapi-tutorial` systemd service on port `8000`. The cookbook configures one application instance and one PostgreSQL database instance.

## Service Type and Instances

**Service Type**: Application Server with PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application service
  - Location/Path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Startup command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Working directory: `/opt/fastapi-tutorial`
  - Runs as: `root`
  - Port/Socket: TCP `0.0.0.0:8000`
  - Restart behavior: `Restart=always`
  - Systemd dependencies: starts after `network.target` and `postgresql.service`

- **fastapi_db**: PostgreSQL application database
  - Database user: `fastapi`
  - Database owner: `fastapi`
  - Host: `localhost`
  - Port/Socket: PostgreSQL default port and distribution-default Unix socket
  - Privileges: All privileges on `fastapi_db` granted to `fastapi`
  - Password configured by the cookbook: `fastapi_password`

No collection attributes or `.each` loops are present. There are no iterable application instances to expand.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

The following are the only relevant files identified by the execution tree and directory listing.

**Recipes:**
```text
recipes/default.rb
```

**Providers:**
```text
```

No custom resources or provider files are used.

**Templates:**
```text
```

No Chef templates are rendered. The environment file and systemd unit are created with inline `file` resources.

**Attributes:**
```text
attributes/default.rb
```

**Files:**
```text
```

No static files are deployed with `cookbook_file` or `remote_file`.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Selects a platform-specific package branch.
   - On RHEL/Fedora systems, installs `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, and `libpq-devel`.
   - On non-RHEL/Fedora systems, installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - On RHEL/Fedora systems, runs `postgresql-setup --initdb` only when `/var/lib/pgsql/data/PG_VERSION` does not exist.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates `/opt/fastapi-tutorial/venv` with `python3 -m venv` when the directory does not exist.
   - Installs dependencies from `/opt/fastapi-tutorial/requirements.txt` into `/opt/fastapi-tutorial/venv`.
   - Enables and starts the `postgresql` service.
   - Creates the PostgreSQL role `fastapi` with password `fastapi_password`.
   - Creates the PostgreSQL database `fastapi_db` owned by `fastapi`.
   - Grants all privileges on `fastapi_db` to `fastapi`.
   - Creates `/opt/fastapi-tutorial/.env` with owner `root`, group `root`, and mode `0644`, containing:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Deploys `/etc/systemd/system/fastapi-tutorial.service` with:
     - Description `FastAPI Tutorial Service`
     - `After=network.target postgresql.service`
     - `Type=simple`
     - `User=root`
     - Working directory `/opt/fastapi-tutorial`
     - `PATH=/opt/fastapi-tutorial/venv/bin`
     - Uvicorn target `app.main:app`
     - Bind address `0.0.0.0`
     - Port `8000`
     - `Restart=always`
     - Enablement through `multi-user.target`
   - Runs `systemctl daemon-reload` immediately when the systemd unit changes.
   - Enables and starts the `fastapi-tutorial` service.

The PostgreSQL shell commands use `|| true` to tolerate an existing role or database. The migration should use idempotent PostgreSQL-specific Ansible modules instead of reproducing those shell commands. The PostgreSQL Python driver and the appropriate Ansible PostgreSQL collection must be installed before database modules are used.

The Ansible migration should preserve the following attribute defaults:

```yaml
fastapi_tutorial:
  app_path: /opt/fastapi-tutorial
  repository: https://github.com/dibanez/fastapi_tutorial.git
  revision: main
  service_port: 8000
```

The existing `.env` mode is `0644`, which exposes the plaintext database password to local users. Mode `0600` is recommended as a deliberate security hardening improvement, but is not an exact permission translation.

## Dependencies

**External cookbook dependencies**: None listed in the provided metadata or execution tree.

**System package dependencies**:

- **RHEL/Fedora**:
  - `python3`
  - `python3-pip`
  - `git`
  - `postgresql-server`
  - `postgresql-contrib`
  - `libpq-devel`
- **Non-RHEL/Fedora**:
  - `python3`
  - `python3-pip`
  - `python3-venv`
  - `git`
  - `postgresql`
  - `postgresql-contrib`
  - `libpq-dev`

**Application dependency source**: `/opt/fastapi-tutorial/requirements.txt`, installed into `/opt/fastapi-tutorial/venv`.

**Service dependencies**:

- `postgresql`
- `fastapi-tutorial`
- `network.target`

The FastAPI systemd unit declares `After=network.target postgresql.service`.

## Credentials

**Detection Summary**: 2 sensitive references detected in `cookbooks/fastapi-tutorial/recipes/default.rb`.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None
- **Path**: None
- **Vault/data bag integration**: None detected
- **Environment-variable secret lookup**: None detected
- **TLS certificate or key references**: None detected

### PostgreSQL role password

- **Variable(s)**: No named Chef attribute; literal `fastapi_password`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in an `execute` resource
- **Usage context**: Creates PostgreSQL role `fastapi` and sets its password
- **Current command**:
  ```sql
  CREATE USER fastapi WITH PASSWORD 'fastapi_password';
  ```

The Ansible migration should store this value in Ansible Vault, for example:

```yaml
fastapi_db_password: !vault |
  ...
```

The vaulted value must be supplied consistently to the PostgreSQL role-management task and the environment file.

### Database connection string

- **Variable(s)**: `DATABASE_URL`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in inline `.env` file content
- **Usage context**: Provides the FastAPI application with its PostgreSQL connection string
- **Current value**:
  ```text
  postgresql://fastapi:fastapi_password@localhost/fastapi_db
  ```

The Ansible implementation should construct this value from vaulted variables rather than storing the password in a non-secret role variable or plaintext task argument.

## Checks for the Migration

**Files to verify**:

- `cookbooks/fastapi-tutorial/attributes/default.rb`
- `cookbooks/fastapi-tutorial/recipes/default.rb`
- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- `/var/lib/pgsql/data/PG_VERSION` on RHEL/Fedora systems

**Service endpoints to check**:

- FastAPI instance `fastapi-tutorial`: TCP `0.0.0.0:8000`
- PostgreSQL instance `fastapi_db`: `localhost`, default PostgreSQL TCP port, and the distribution-default Unix socket

**Templates rendered**: None.

**Inline files rendered**:

- `/opt/fastapi-tutorial/.env`: rendered once
- `/etc/systemd/system/fastapi-tutorial.service`: rendered once

**Log sources**:

- `postgresql` systemd unit logs
- `fastapi-tutorial` systemd unit logs

## Pre-flight checks

### Platform and package checks

```bash
cat /etc/os-release
python3 --version
python3 -m pip --version
git --version
```

On RHEL/Fedora systems:

```bash
rpm -q python3 python3-pip git postgresql-server postgresql-contrib libpq-devel
```

On non-RHEL/Fedora systems:

```bash
dpkg-query -W python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev
```

### PostgreSQL instance: fastapi_db

```bash
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
```

Expected results:

- The PostgreSQL service is enabled and active.
- PostgreSQL accepts local connections.

On RHEL/Fedora systems, verify initialization:

```bash
test -f /var/lib/pgsql/data/PG_VERSION
```

Verify the role:

```bash
sudo -u postgres psql -tAc \
  "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"
```

Expected output:

```text
fastapi
```

Verify the database:

```bash
sudo -u postgres psql -tAc \
  "SELECT datname FROM pg_database WHERE datname = 'fastapi_db';"
```

Expected output:

```text
fastapi_db
```

Verify the database owner:

```bash
sudo -u postgres psql -tAc \
  "SELECT pg_catalog.pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"
```

Expected output:

```text
fastapi
```

Verify privileges:

```bash
sudo -u postgres psql -c "\l+ fastapi_db"
```

The output should show `fastapi` as the owner and include privileges for the `fastapi` role.

Validate authentication without exposing the password:

```bash
PGPASSWORD="$FASTAPI_DB_PASSWORD" psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_user, current_database();"
```

Expected values:

```text
current_user: fastapi
current_database: fastapi_db
```

Check the PostgreSQL listener when TCP is enabled:

```bash
ss -ltnp | grep ':5432'
```

If PostgreSQL uses only a Unix socket, validate connectivity with `psql` instead of requiring a TCP listener.

### FastAPI instance: fastapi-tutorial

Verify the application checkout:

```bash
test -d /opt/fastapi-tutorial
test -f /opt/fastapi-tutorial/requirements.txt
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
git -C /opt/fastapi-tutorial remote -v
```

Expected results:

- `/opt/fastapi-tutorial` exists.
- `/opt/fastapi-tutorial/requirements.txt` exists.
- The checkout corresponds to revision `main`.
- The configured repository is `https://github.com/dibanez/fastapi_tutorial.git`.

Verify the virtual environment and dependencies:

```bash
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn

/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip check
```

Expected results:

- Python, pip, and Uvicorn executables exist.
- `pip check` reports no broken requirements.

Verify the environment file without exposing the password:

```bash
stat -c '%U:%G %a %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION)=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env | \
  sed -E 's#(postgresql://[^:]+:)[^@]+@#\1***@#'
```

Expected configuration:

```text
PROJECT_NAME="FastAPI Tutorial"
API_VERSION=1.0.0
DATABASE_URL=postgresql://fastapi:***@localhost/fastapi_db
```

Verify the systemd unit:

```bash
systemctl cat fastapi-tutorial
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
```

Verify unit properties:

```bash
systemctl show fastapi-tutorial \
  --property=User \
  --property=WorkingDirectory \
  --property=ExecStart \
  --property=Restart
```

Expected values include:

- `User=root`
- `WorkingDirectory=/opt/fastapi-tutorial`
- `ExecStart` uses `/opt/fastapi-tutorial/venv/bin/uvicorn`
- Uvicorn target is `app.main:app`
- Host is `0.0.0.0`
- Port is `8000`
- `Restart=always`

Verify application health:

```bash
systemctl status fastapi-tutorial
journalctl -u fastapi-tutorial --no-pager -n 50
pgrep -af '/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app'
curl -i http://127.0.0.1:8000/
```

Expected results:

- The `fastapi-tutorial` service is enabled and active.
- One Uvicorn process is running with the configured command.
- The HTTP check returns a response from the FastAPI application rather than a connection failure. The exact status code depends on the repository's route definitions.

Verify the listener:

```bash
ss -ltnp | grep ':8000'
```

Expected result: a listener bound to `0.0.0.0:8000` or an equivalent IPv4 wildcard binding.

### Systemd dependency and reload checks

```bash
systemctl show fastapi-tutorial --property=After
systemctl daemon-reload
systemctl restart fastapi-tutorial
systemctl is-active fastapi-tutorial
```

Expected result: `fastapi-tutorial` remains active after the reload and restart and can connect to the local `fastapi_db` PostgreSQL database.