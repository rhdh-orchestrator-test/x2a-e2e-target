---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys one FastAPI application from the `main` branch of `https://github.com/dibanez/fastapi_tutorial.git`. It installs Python, Git, PostgreSQL, and PostgreSQL development packages; creates a Python virtual environment at `/opt/fastapi-tutorial/venv`; installs application dependencies; enables PostgreSQL; creates the `fastapi` PostgreSQL role and `fastapi_db` database; writes an environment file containing the database connection string; and manages a systemd service listening on `0.0.0.0:8000`. The cookbook contains one recipe, no templates, no custom resources, no providers, no attribute files, and one hardcoded database credential that must be migrated to Ansible Vault.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application served by Uvicorn
  - Application path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Python virtual environment: `/opt/fastapi-tutorial/venv`
  - Environment file: `/opt/fastapi-tutorial/.env`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Service user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Process command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Listen address: `0.0.0.0`
  - Listen port: `8000`
  - Restart policy: `always`
  - Startup dependency: `postgresql.service`
  - Application target: `app.main:app`
  - The repository module layout and the existence of the `app.main:app` target must be verified against the application source before migration.

- **postgresql**: PostgreSQL database service supporting the FastAPI application
  - Operating-system service: `postgresql`
  - Database host: `localhost`
  - Expected port: `5432`
  - Database user: `fastapi`
  - Database name: `fastapi_db`
  - Connection scheme: PostgreSQL
  - Database URL: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
  - PostgreSQL port is not explicitly configured by the cookbook and therefore uses the platform default.

**Iterations**: None. The execution tree contains no `.each` loop, collection iteration, or repeated resource block.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

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

The cookbook creates these files dynamically through inline Chef `file` resources:

```text
/opt/fastapi-tutorial/.env
/etc/systemd/system/fastapi-tutorial.service
```

These are generated files, not static cookbook files.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the seven required system packages with one `package` resource:
     - `python3`
     - `python3-pip`
     - `python3-venv`
     - `git`
     - `postgresql`
     - `postgresql-contrib`
     - `libpq-dev`
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - The repository metadata, revision, and application module layout require verification against the source repository before migration.
   - Creates the virtual environment with:
     ```bash
     python3 -m venv /opt/fastapi-tutorial/venv
     ```
     using `/opt/fastapi-tutorial/venv` as the idempotence guard.
   - Installs Python dependencies from `/opt/fastapi-tutorial/requirements.txt` into `/opt/fastapi-tutorial/venv`.
   - Enables and starts the `postgresql` service.
   - Creates the PostgreSQL role `fastapi` with password `fastapi_password`.
   - Creates the PostgreSQL database `fastapi_db` owned by `fastapi`.
   - Grants all privileges on `fastapi_db` to `fastapi`.
   - Writes `/opt/fastapi-tutorial/.env` with application settings and the database URL.
   - Writes `/etc/systemd/system/fastapi-tutorial.service`.
   - Immediately runs `systemctl daemon-reload` when the systemd unit changes.
   - Enables and starts the `fastapi-tutorial` service.

   **Resources in execution order:**
   - `package`: one resource managing seven packages
   - `directory`: `/opt/fastapi-tutorial`
   - `git`: `/opt/fastapi-tutorial`
   - `execute[create_venv]`
   - `execute[install_dependencies]`
   - `service[postgresql]`
   - `execute[create_db_user]`
   - `file[/opt/fastapi-tutorial/.env]`
   - `file[/etc/systemd/system/fastapi-tutorial.service]`
   - `execute[systemd_reload]`, notified immediately by the systemd unit file resource
   - `service[fastapi-tutorial]`

   **Environment file content:**
   ```dotenv
   PROJECT_NAME="FastAPI Tutorial"
   API_VERSION=1.0.0
   DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
   ```

   **Systemd unit properties:**
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

   - The Ansible implementation should use `ansible.builtin.package`, `ansible.builtin.file`, `ansible.builtin.git`, `ansible.builtin.command` or `ansible.builtin.pip`, `ansible.builtin.copy`, and `ansible.builtin.systemd`.
   - PostgreSQL objects should preferably be managed with `community.postgresql.postgresql_user`, `community.postgresql.postgresql_db`, and `community.postgresql.postgresql_privs`.
   - Store the database password in Ansible Vault and use the vaulted variable in both the PostgreSQL role task and the environment file.
   - Apply `no_log: true` to credential-handling tasks.
   - Preserve the service user `root` for behavioral compatibility, although a dedicated service account is recommended as a deliberate security improvement.
   - Preserve the systemd daemon-reload notification relationship and ensure the reload occurs before starting the application service.
   - No `.each` loops or collection iterations require expansion.

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

`libpq-dev` is Debian-family package naming and must be validated or mapped appropriately on CentOS or other target distributions.

**Service dependencies**:
- `postgresql`: enabled and started before database initialization
- `fastapi-tutorial`: enabled and started after its unit file is written and systemd is reloaded
- `fastapi-tutorial` declares `After=network.target postgresql.service`

**Application dependencies**:
- Repository: `https://github.com/dibanez/fastapi_tutorial.git`
- Revision: `main`
- Requirements file: `/opt/fastapi-tutorial/requirements.txt`
- Uvicorn target: `app.main:app`

## Credentials

**Detection Summary**: 1 database credential detected in 1 recipe file. The credential is used both to create the PostgreSQL role and to construct the application database URL.

**Source**:
- **Provider**: Hardcoded in the Chef recipe
- **URL**: None
- **Path**: None
- **Current storage**: Plaintext in `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Recommended Ansible storage**: Ansible Vault

### PostgreSQL `fastapi` database password

- **Variable(s)**:
  - Literal password: `fastapi_password`
  - Database URL credential: `fastapi_password`
  - PostgreSQL role: `fastapi`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded plaintext
- **Usage context**:
  - Creates the PostgreSQL role `fastapi`
  - Authenticates the application to `fastapi_db`
  - Appears in `/opt/fastapi-tutorial/.env` as:
    ```text
    DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
    ```
- **Migration requirement**:
  - Define the password in an Ansible Vault-protected variable.
  - Use the vaulted variable when creating the PostgreSQL role.
  - Use the same variable when rendering `/opt/fastapi-tutorial/.env`.
  - Avoid exposing the password in task output with `no_log: true`.
  - Consider mode `0600` for the environment file instead of the cookbook’s `0644`.

No Chef data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, TLS certificates, private keys, API keys, or external secret-manager URLs were detected.

## Checks for the Migration

**Files to verify**:
- `cookbooks/fastapi-tutorial/recipes/default.rb`
- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Database objects to verify**:
- PostgreSQL role `fastapi`
- PostgreSQL database `fastapi_db`

**Service endpoints to check**:
- FastAPI: `0.0.0.0:8000`
- PostgreSQL: `localhost:5432`
- PostgreSQL Unix socket: platform default, because the cookbook does not specify a socket path

**Log sources to verify**:
- `journalctl -u fastapi-tutorial`
- `journalctl -u postgresql`

**Templates rendered**: None. The cookbook uses two inline `file` resources:
- Inline environment content → `/opt/fastapi-tutorial/.env` — rendered once
- Inline systemd unit content → `/etc/systemd/system/fastapi-tutorial.service` — rendered once

## Pre-flight checks

### Package and directory checks

```bash
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev 2>/dev/null || \
rpm -q python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

ls -ld /opt/fastapi-tutorial
ls -ld /opt/fastapi-tutorial/venv
test -f /opt/fastapi-tutorial/requirements.txt
```

### Repository and application checks

```bash
git -C /opt/fastapi-tutorial remote -v
git -C /opt/fastapi-tutorial branch --show-current
git -C /opt/fastapi-tutorial rev-parse --short HEAD
test -f /opt/fastapi-tutorial/requirements.txt
test -x /opt/fastapi-tutorial/venv/bin/uvicorn
```

Confirm the repository is `https://github.com/dibanez/fastapi_tutorial.git`, the intended revision is `main`, and the source contains the module target required by the service command: `app.main:app`.

### PostgreSQL instance checks

```bash
systemctl status postgresql --no-pager
systemctl is-enabled postgresql
systemctl is-active postgresql
ss -tlnp | grep ':5432' || true
```

Expected results:
- PostgreSQL is enabled.
- PostgreSQL is active.
- PostgreSQL accepts connections on its configured platform-default endpoint.

### PostgreSQL role and database checks

```bash
sudo -u postgres psql -tAc \
  "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"

sudo -u postgres psql -tAc \
  "SELECT datname, pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"
```

Expected results:
```text
fastapi
fastapi_db | fastapi
```

### Application database connectivity check

Retrieve the password securely from Ansible Vault or an approved secret source:

```bash
PGPASSWORD='<retrieve securely from Ansible Vault or an approved secret source>' \
psql -h localhost -U fastapi -d fastapi_db \
  -c "SELECT current_database(), current_user;"
```

Expected results:
- Current database: `fastapi_db`
- Current user: `fastapi`

### FastAPI instance checks

```bash
systemctl status fastapi-tutorial --no-pager
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl show fastapi-tutorial \
  --property=User,WorkingDirectory,ExecStart,Restart
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
```

Verify:
```text
User=root
WorkingDirectory=/opt/fastapi-tutorial
ExecStart=/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
```

### Environment file check

```bash
stat -c '%A %U %G %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' \
  /opt/fastapi-tutorial/.env
```

Expected keys:
```text
PROJECT_NAME
API_VERSION
DATABASE_URL
```

Do not print the complete file because it contains the database password.

### FastAPI endpoint and process checks

```bash
ss -tlnp | grep ':8000'
curl -i http://127.0.0.1:8000/
ps -ef | grep '[u]vicorn app.main:app'
```

Expected results:
- A listening socket is bound to `0.0.0.0:8000`.
- The HTTP request returns an application response rather than a connection-refused or timeout error.
- The process uses `/opt/fastapi-tutorial/venv/bin/uvicorn`.
- The command includes `--host 0.0.0.0 --port 8000`.

The cookbook does not define a specific health endpoint, so no additional application path should be assumed.

### Python environment checks

```bash
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip --version
/opt/fastapi-tutorial/venv/bin/pip check
/opt/fastapi-tutorial/venv/bin/pip list
```

### Log checks

```bash
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u postgresql --no-pager -n 100
```

Check for:
- Successful Uvicorn startup
- Successful PostgreSQL connectivity
- No `app.main` import errors
- No missing dependency errors
- No database authentication failures
- No repeated service restart loop

### Systemd reload check

After changing the service unit:

```bash
systemctl daemon-reload
systemctl restart fastapi-tutorial
systemctl status fastapi-tutorial --no-pager
```

The final Ansible implementation should notify a daemon-reload handler when `/etc/systemd/system/fastapi-tutorial.service` changes and ensure that the `fastapi-tutorial` service starts only after the reload has completed.