---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the `fastapi-tutorial` FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main`. It installs Python, Git, PostgreSQL, and development dependencies; creates a Python virtual environment; installs application requirements; initializes the PostgreSQL role and database; writes the application `.env` file; and runs Uvicorn as a systemd service on `0.0.0.0:8000`. The PostgreSQL password is hardcoded in the recipe and generated `.env` file and must be migrated to Ansible Vault or another approved secret store.

## Service Type and Instances

**Service Type**: Application Server with PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application service
  - Location/Path: `/opt/fastapi-tutorial`
  - Port/Socket: `0.0.0.0:8000`
  - Key Config: Repository `https://github.com/dibanez/fastapi_tutorial.git`, revision `main`, virtual environment `/opt/fastapi-tutorial/venv`, command `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`, working directory `/opt/fastapi-tutorial`, service user `root`, restart policy `always`, systemd service `fastapi-tutorial`

- **postgresql**: PostgreSQL database service
  - Location/Path: System PostgreSQL installation
  - Port/Socket: PostgreSQL default port, normally `localhost:5432`; no port is explicitly configured
  - Key Config: Enabled and started; role `fastapi`; database `fastapi_db`; owner `fastapi`; all database privileges granted to `fastapi`

There are no collection attributes or `.each` loops in the execution tree. No iteration expansion is required.

## File Structure

Only one recipe file is present and executed. No provider, template, attribute, or static file is used by the cookbook.

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
   - Installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev` with one `package` resource.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` into `/opt/fastapi-tutorial` at revision `main`.
   - Creates the Python virtual environment with `python3 -m venv /opt/fastapi-tutorial/venv`, guarded by the existence of `/opt/fastapi-tutorial/venv`.
   - Installs dependencies with `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt` from working directory `/opt/fastapi-tutorial`.
   - Enables and starts `postgresql`.
   - Runs PostgreSQL commands as the `postgres` user to create role `fastapi`, database `fastapi_db`, and grant all privileges on `fastapi_db` to `fastapi`. Each command ends with `|| true`, which suppresses existing-object and other PostgreSQL errors.
   - Creates `/opt/fastapi-tutorial/.env` with owner `root`, group `root`, and mode `0644`. The file contains:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Creates `/etc/systemd/system/fastapi-tutorial.service` with owner `root`, group `root`, and mode `0644`. The unit:
     - Runs after `network.target` and `postgresql.service`
     - Runs as `root`
     - Uses `/opt/fastapi-tutorial` as its working directory
     - Sets `PATH` to `/opt/fastapi-tutorial/venv/bin`
     - Executes `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
     - Uses `Restart=always`
     - Is enabled through the `fastapi-tutorial` service resource
   - Immediately notifies `execute[systemd_reload]` when the systemd unit changes.
   - Runs `systemctl daemon-reload` through an execute resource whose default action is `nothing`.
   - Enables and starts the `fastapi-tutorial` service after the unit is installed and systemd has reloaded.

   **Resources in execution order**:
   - `package` (1)
   - `directory` (1)
   - `git` (1)
   - `execute[create_venv]` (1)
   - `execute[install_dependencies]` (1)
   - `service[postgresql]` (1)
   - `execute[create_db_user]` (1)
   - `file[/opt/fastapi-tutorial/.env]` (1)
   - `file[/etc/systemd/system/fastapi-tutorial.service]` (1)
   - `execute[systemd_reload]` (1, notified and run only when the unit changes)
   - `service[fastapi-tutorial]` (1)

   **Ansible migration considerations**:
   - Use `ansible.builtin.package` or platform-specific package tasks.
   - Use `ansible.builtin.file`, `ansible.builtin.git`, `ansible.builtin.command` with `creates`, and `ansible.builtin.pip`.
   - Replace shell-based PostgreSQL initialization with `community.postgresql.postgresql_user`, `community.postgresql.postgresql_db`, and `community.postgresql.postgresql_privs`.
   - Store the database password in Ansible Vault, AAP credentials, HashiCorp Vault, or another approved secret manager.
   - Prefer mode `0600` for `.env` instead of the current `0644`.
   - Use a managed systemd unit and notify a handler with `daemon_reload: true` when it changes.
   - Notify or restart `fastapi-tutorial` when `.env` or the systemd unit changes.
   - Package names may require platform-specific mapping on CentOS. The cookbook declares support for Ubuntu `>= 18.04` and CentOS `>= 7.0`, but does not provide separate package names.

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

**Source dependencies**:
- Git repository: `https://github.com/dibanez/fastapi_tutorial.git`
- Revision: `main`
- Application requirements: `/opt/fastapi-tutorial/requirements.txt`

**Service dependencies**:
- `postgresql`: enabled and started before database initialization
- `fastapi-tutorial`: enabled and started after its systemd unit is installed and systemd has reloaded
- `fastapi-tutorial` systemd unit: ordered after `network.target` and `postgresql.service`

## Credentials

**Detection Summary**: 1 credential detected across 1 file.

**Source**:
  - **Provider**: Hardcoded in the Chef recipe
  - **URL**: None
  - **Path**: `cookbooks/fastapi-tutorial/recipes/default.rb`

### PostgreSQL Database Password

- **Variable(s)**: No Chef attribute variable; literal `fastapi_password`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the PostgreSQL `CREATE USER` command and the `DATABASE_URL` value
- **Usage context**:
  - Creates PostgreSQL role `fastapi`
  - Connects the FastAPI application to `localhost/fastapi_db`
  - Is written to `/opt/fastapi-tutorial/.env`
- **Migration requirement**: Store the password in Ansible Vault, AAP credentials, HashiCorp Vault, or another approved secret manager. Do not commit the cleartext password to the playbook repository. Prefer mode `0600` for `/opt/fastapi-tutorial/.env`.

No Chef data bags, encrypted data bags, Chef Vault calls, CyberArk integration, Conjur integration, environment-variable secret references, TLS certificates, private keys, API tokens, or external database connection strings were detected.

## Checks for the Migration

**Files to verify**:
- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Database objects to verify**:
- PostgreSQL role `fastapi`
- PostgreSQL database `fastapi_db`
- Database owner `fastapi`
- All privileges on `fastapi_db` granted to `fastapi`

**Service endpoints to check**:
- FastAPI instance `fastapi-tutorial`: `0.0.0.0:8000`
- PostgreSQL instance `postgresql`: normally `localhost:5432`

**Unix sockets**:
- No application Unix socket is configured.
- PostgreSQL’s distribution-specific Unix socket is not explicitly configured.

**Templates rendered**:
- None. Two inline Chef `file` resources create the configuration files:
  - `/opt/fastapi-tutorial/.env`: 1 file
  - `/etc/systemd/system/fastapi-tutorial.service`: 1 file

## Pre-flight checks

```bash
# Verify installed packages
python3 --version
python3 -m pip --version
git --version
psql --version

# Verify the fastapi-tutorial application directory and checkout
ls -ld /opt/fastapi-tutorial
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
git -C /opt/fastapi-tutorial rev-parse --verify HEAD
test -f /opt/fastapi-tutorial/requirements.txt

# Verify the fastapi-tutorial virtual environment
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip list

# Verify fastapi-tutorial configuration
stat /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' /opt/fastapi-tutorial/.env

# Verify the fastapi-tutorial systemd unit
systemctl cat fastapi-tutorial
grep -E '^(Description|After|Type|User|WorkingDirectory|Environment|ExecStart|Restart|WantedBy)=' \
  /etc/systemd/system/fastapi-tutorial.service

systemctl daemon-reload
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl status fastapi-tutorial --no-pager

# Verify the fastapi-tutorial process and endpoint
ps aux | grep '[u]vicorn app.main:app'
ss -tlnp | grep ':8000'
netstat -tulpn 2>/dev/null | grep ':8000'
curl -I http://127.0.0.1:8000/
curl -sS -o /dev/null -w 'HTTP status: %{http_code}\n' http://127.0.0.1:8000/
journalctl -u fastapi-tutorial --no-pager -n 100

# Verify the postgresql instance
systemctl is-enabled postgresql
systemctl is-active postgresql
systemctl status postgresql --no-pager
journalctl -u postgresql --no-pager -n 100

# Verify the fastapi PostgreSQL role
sudo -u postgres psql -tAc \
  "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"

# Verify the fastapi_db database and owner
sudo -u postgres psql -tAc \
  "SELECT datname, pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"

# Verify application database connectivity
PGPASSWORD='REDACTED' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT version();"

# Verify fastapi database privileges
sudo -u postgres psql -tAc \
  "SELECT has_database_privilege('fastapi', 'fastapi_db', 'CONNECT');"
```

Expected results:

- `fastapi-tutorial` is enabled and active.
- `postgresql` is enabled and active.
- Uvicorn runs from `/opt/fastapi-tutorial/venv/bin/uvicorn`.
- Port `8000` is listening for the `fastapi-tutorial` instance.
- The FastAPI endpoint returns a valid response, ideally `200 OK`.
- PostgreSQL role `fastapi` exists.
- Database `fastapi_db` exists and is owned by `fastapi`.
- A PostgreSQL connection using the application credentials succeeds.
- `.env` contains `PROJECT_NAME`, `API_VERSION`, and `DATABASE_URL`.
- The systemd unit contains the expected working directory, virtual-environment path, Uvicorn command, and port `8000`.