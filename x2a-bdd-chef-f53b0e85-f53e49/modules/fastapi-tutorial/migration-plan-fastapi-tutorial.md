---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`, installs Python, Git, and PostgreSQL dependencies, creates a Python virtual environment, installs application requirements, initializes and starts PostgreSQL, creates the `fastapi` role and `fastapi_db` database, writes an environment file, and manages the `fastapi-tutorial` systemd service on port `8000`. Debian-family systems use the default package branch; Fedora/RHEL systems use platform-specific packages and PostgreSQL initialization. The database password is currently hardcoded and must be migrated to Ansible Vault.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application managed by systemd
  - Location/Path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Entry point: `app.main:app`
  - Server command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Port/Socket: `0.0.0.0:8000`
  - systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Runtime user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Restart policy: `always`
  - Service ordering: After `network.target` and `postgresql.service`

- **fastapi_db**: PostgreSQL database used by the FastAPI application
  - Location/Path: Platform-managed PostgreSQL data directory
  - Port/Socket: Local PostgreSQL Unix socket or TCP connection at `localhost`
  - Owner: `fastapi`
  - Database user: `fastapi`
  - Database password: `fastapi_password`
  - Connection string: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
  - Required privileges: `ALL` on `fastapi_db`

## File Structure

Only one recipe file is executed by the supplied execution tree.

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

No ERB templates are rendered. Configuration is written using inline Chef `file` resources.

**Attributes:**
```text
```

No attribute files are used by the execution tree.

**Files:**
```text
```

No static files are deployed with `cookbook_file` or `remote_file`.

## Module Explanation

The cookbook has one entry recipe and no `include_recipe` calls. The complete execution order is:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Selects package and PostgreSQL initialization behavior based on `platform_family?('fedora', 'rhel')`.
   - On Fedora/RHEL, installs `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, and `libpq-devel`.
   - On Fedora/RHEL, runs `postgresql-setup --initdb` only when `/var/lib/pgsql/data/PG_VERSION` does not exist.
   - On non-Fedora/RHEL platforms, installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates `/opt/fastapi-tutorial/venv` with `python3 -m venv`, only when the virtual environment does not exist.
   - Installs dependencies from `/opt/fastapi-tutorial/requirements.txt` into `/opt/fastapi-tutorial/venv`.
   - Enables and starts the `postgresql` service.
   - Creates the PostgreSQL role `fastapi` with password `fastapi_password`.
   - Creates the `fastapi_db` database owned by `fastapi`.
   - Grants all privileges on `fastapi_db` to `fastapi`.
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
   - Runs `systemctl daemon-reload` immediately when the systemd unit changes.
   - Enables and starts the `fastapi-tutorial` service.
   - Does not show an explicit automatic restart notification for repository, dependency, `.env`, or systemd unit changes. The Ansible migration must not add a restart handler unless that behavior is intentionally documented as a change.

   **Iterations**: None. No `.each` loops or collection-based iterations are present.

## Dependencies

**External cookbook dependencies**: None declared in `metadata.rb`.

**System package dependencies**:

- Fedora/RHEL:
  - `python3`
  - `python3-pip`
  - `git`
  - `postgresql-server`
  - `postgresql-contrib`
  - `libpq-devel`
- Non-Fedora/RHEL:
  - `python3`
  - `python3-pip`
  - `python3-venv`
  - `git`
  - `postgresql`
  - `postgresql-contrib`
  - `libpq-dev`

**Application dependencies**:

- Python packages listed in `/opt/fastapi-tutorial/requirements.txt`
- Packages installed into `/opt/fastapi-tutorial/venv`

**Service dependencies**:

- `postgresql`
- `fastapi-tutorial`

**Repository dependency**:

- Repository: `https://github.com/dibanez/fastapi_tutorial.git`
- Revision: `main`

## Credentials

**Detection Summary**: 1 hardcoded database credential detected in 1 recipe file and reproduced in the generated `.env` content.

**Source**:

- **Provider**: Hardcoded in Chef recipe
- **URL**: None
- **Path**: None
- **Secret value**: `fastapi_password`

### PostgreSQL database password

- **Variable(s)**:
  - No Chef attribute variable is used.
  - Literal password: `fastapi_password`
  - Embedded connection string: `DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded plaintext in the PostgreSQL `execute` resource and inline `.env` file content
- **Usage context**:
  - Sets the password for PostgreSQL user `fastapi`.
  - Authenticates the FastAPI application to `fastapi_db`.
- **Migration storage**:
  - Store the value in Ansible Vault as `fastapi_db_password`.
  - Use the vaulted variable for both the PostgreSQL user task and `.env` deployment.
  - Use `no_log: true` on tasks that could expose the password.

No Chef data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, HashiCorp Vault, AWS Secrets Manager, environment-variable secret lookups, TLS certificates, private keys, API tokens, or SSH keys were detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- Fedora/RHEL PostgreSQL data directory: `/var/lib/pgsql/data/`
- Non-Fedora/RHEL PostgreSQL data directory: platform-managed path discovered from the installed package

**Database objects to verify**:

- PostgreSQL role: `fastapi`
- PostgreSQL database: `fastapi_db`
- Database owner: `fastapi`
- `ALL` privileges granted to `fastapi`

**Service endpoints to check**:

- FastAPI: `http://127.0.0.1:8000`
- FastAPI listener: `0.0.0.0:8000`
- PostgreSQL: `localhost` using the platform PostgreSQL Unix socket or local TCP endpoint

**Templates rendered**:

None. No ERB templates are used.

**Inline configuration files created**:

- `/opt/fastapi-tutorial/.env`: created once
- `/etc/systemd/system/fastapi-tutorial.service`: created once

## Pre-flight checks

Run these checks after the Ansible role completes.

### PostgreSQL instance: `postgresql`

```bash
systemctl status postgresql --no-pager
systemctl is-enabled postgresql
systemctl is-active postgresql
```

Expected result:

- PostgreSQL is enabled.
- PostgreSQL is active.

Verify the PostgreSQL role:

```bash
sudo -u postgres psql -tAc \
  "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"
```

Expected result:

```text
fastapi
```

Verify the database and owner:

```bash
sudo -u postgres psql -tAc \
  "SELECT datname, pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"
```

Expected result:

```text
fastapi_db|fastapi
```

Test application authentication:

```bash
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_user, current_database();"
```

Expected result:

- `current_user` is `fastapi`.
- `current_database` is `fastapi_db`.

Verify database privileges:

```bash
sudo -u postgres psql -d fastapi_db -c "\l+ fastapi_db"
```

Confirm that `fastapi` owns the database and has the expected access.

### FastAPI instance: `fastapi-tutorial`

```bash
systemctl status fastapi-tutorial --no-pager
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
```

Expected result:

- `fastapi-tutorial` is enabled.
- `fastapi-tutorial` is active.

Test the HTTP endpoint:

```bash
curl -i http://127.0.0.1:8000/
```

Expected result:

- TCP connection succeeds on port `8000`.
- The application returns an HTTP response.

Verify the listener:

```bash
ss -tlnp | grep ':8000'
```

Expected result:

- A listener exists on `0.0.0.0:8000` or an equivalent IPv4 wildcard address.
- The listener belongs to the Uvicorn/FastAPI process.

Verify the application process:

```bash
ps aux | grep '[u]vicorn app.main:app'
```

Expected command:

```text
/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Verify virtual environment executables:

```bash
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn
```

### Application configuration

```bash
cat /opt/fastapi-tutorial/.env
```

Confirm the following settings:

```text
PROJECT_NAME="FastAPI Tutorial"
API_VERSION=1.0.0
DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
```

Verify the systemd unit:

```bash
systemctl cat fastapi-tutorial
systemctl show fastapi-tutorial \
  --property=User \
  --property=WorkingDirectory \
  --property=ExecStart \
  --property=Restart
```

Expected values include:

- `User=root`
- `WorkingDirectory=/opt/fastapi-tutorial`
- Uvicorn executable: `/opt/fastapi-tutorial/venv/bin/uvicorn`
- `Restart=always`

Validate the unit:

```bash
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
```

Expected result:

- No systemd unit syntax errors.

### Repository and dependency validation

```bash
git -C /opt/fastapi-tutorial status
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
git -C /opt/fastapi-tutorial rev-parse HEAD
test -f /opt/fastapi-tutorial/requirements.txt
/opt/fastapi-tutorial/venv/bin/pip list
```

Confirm that the repository is at revision `main`, `requirements.txt` exists, and dependencies are installed in the intended virtual environment.

### Service logs

```bash
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u postgresql --no-pager -n 100
```

Follow FastAPI logs while making a request:

```bash
journalctl -u fastapi-tutorial -f
```

### Service restart policy

```bash
systemctl show fastapi-tutorial --property=Restart
```

Expected result:

```text
Restart=always
```

Test the application service lifecycle:

```bash
sudo systemctl restart fastapi-tutorial
systemctl is-active fastapi-tutorial
curl -i http://127.0.0.1:8000/
```

Expected result:

- The service returns to the `active` state.
- The HTTP endpoint responds on port `8000`.

The analyzed Chef execution does not automatically restart `fastapi-tutorial` when the systemd unit changes; it only immediately runs `systemctl daemon-reload`. The Ansible implementation should preserve that behavior unless an explicit restart handler is intentionally added and documented.