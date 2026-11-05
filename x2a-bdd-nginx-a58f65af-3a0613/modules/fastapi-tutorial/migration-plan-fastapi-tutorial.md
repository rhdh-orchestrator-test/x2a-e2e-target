---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI Tutorial application from the `main` branch of `https://github.com/dibanez/fastapi_tutorial.git` to `/opt/fastapi-tutorial`, installs Python, Git, PostgreSQL, and development dependencies, creates a Python virtual environment, installs application requirements, configures the PostgreSQL user and database, writes the application environment file, and manages the `fastapi-tutorial` systemd service. The application listens on `0.0.0.0:8000` and connects to the local PostgreSQL database `fastapi_db` as user `fastapi`. One hardcoded PostgreSQL password must be moved to Ansible Vault or another secret-management system.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application served by Uvicorn
  - Location/Path: `/opt/fastapi-tutorial`
  - Source repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Repository revision: `main`
  - Python virtual environment: `/opt/fastapi-tutorial/venv`
  - Port/Socket: TCP `8000`, bound to `0.0.0.0`
  - Application command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - systemd service: `fastapi-tutorial`
  - systemd user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Restart policy: `always`
  - Key Config: Starts after `network.target` and `postgresql.service`; enabled through `multi-user.target`

- **postgresql**: PostgreSQL database service for the FastAPI application
  - Location/Path: Local PostgreSQL installation
  - Port/Socket: TCP `5432` on `localhost`
  - Database user: `fastapi`
  - Database name: `fastapi_db`
  - Database owner: `fastapi`
  - Key Config: User has `ALL` privileges on `fastapi_db`; service is enabled and started

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**
```text
cookbooks/fastapi-tutorial/recipes/default.rb
```

**Providers:**
```text
```

No custom resource providers are used.

**Templates:**
```text
```

No ERB templates are used. Configuration files are created directly with Chef `file` resources.

**Attributes:**
```text
```

No attribute files are used.

**Files:**
```text
```

No static files are deployed with `cookbook_file` or `remote_file`.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the system packages `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates the virtual environment with `python3 -m venv /opt/fastapi-tutorial/venv` only when the path does not exist.
   - Installs dependencies from `/opt/fastapi-tutorial/requirements.txt` into `/opt/fastapi-tutorial/venv` using `/opt/fastapi-tutorial/venv/bin/pip`.
   - Enables and starts the `postgresql` service.
   - Creates PostgreSQL user `fastapi` with password `fastapi_password`.
   - Creates database `fastapi_db` owned by `fastapi`.
   - Grants `ALL` privileges on `fastapi_db` to `fastapi`.
   - Creates `/opt/fastapi-tutorial/.env` with owner `root`, group `root`, and mode `0644`.
   - Writes the following environment configuration:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Creates `/etc/systemd/system/fastapi-tutorial.service` with owner `root`, group `root`, and mode `0644`.
   - Configures the systemd unit to run as `root` from `/opt/fastapi-tutorial` using `/opt/fastapi-tutorial/venv/bin/uvicorn`.
   - Configures Uvicorn to serve `app.main:app` on `0.0.0.0:8000` with `Restart=always`.
   - Configures the service to start after `network.target` and `postgresql.service`.
   - Notifies `execute[systemd_reload]` when the systemd unit changes.
   - Runs `systemctl daemon-reload` only when notified.
   - Enables and starts the `fastapi-tutorial` service.
   - Iterations: None; the recipe contains no `.each` loops or collection-valued attributes.

For the Ansible migration:

- Use `ansible.builtin.package` for the seven system packages.
- Use `ansible.builtin.file` for `/opt/fastapi-tutorial`.
- Use `ansible.builtin.git` for repository synchronization.
- Use `ansible.builtin.command` with `creates: /opt/fastapi-tutorial/venv` for virtual-environment creation.
- Use `ansible.builtin.pip` with `/opt/fastapi-tutorial/requirements.txt` and `/opt/fastapi-tutorial/venv`.
- Use `ansible.builtin.service` or `ansible.builtin.systemd` to enable and start PostgreSQL.
- Use `community.postgresql.postgresql_user`, `community.postgresql.postgresql_db`, and `community.postgresql.postgresql_privs` for idempotent database configuration.
- Use `ansible.builtin.copy` or `ansible.builtin.template` for `/opt/fastapi-tutorial/.env` and the systemd unit.
- Store the database password in Ansible Vault or an external secret provider.
- Use an Ansible handler with `daemon_reload: true` when `/etc/systemd/system/fastapi-tutorial.service` changes.
- Enable and start `fastapi-tutorial` after the systemd daemon reload.

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

**Ansible collection dependencies**:

- `community.postgresql`

**Application dependency source**:

- `/opt/fastapi-tutorial/requirements.txt`
- Installed into `/opt/fastapi-tutorial/venv`

**Service dependencies**:

- `postgresql`
- `fastapi-tutorial`

**Execution dependency chain**:

1. Install operating-system packages.
2. Create `/opt/fastapi-tutorial`.
3. Synchronize the Git repository.
4. Create the Python virtual environment.
5. Install Python dependencies.
6. Enable and start PostgreSQL.
7. Create the PostgreSQL user, database, and privileges.
8. Write `/opt/fastapi-tutorial/.env`.
9. Write `/etc/systemd/system/fastapi-tutorial.service`.
10. Reload systemd if the unit changed.
11. Enable and start `fastapi-tutorial`.

## Credentials

**Detection Summary**: 1 credential detected in 1 source file, with two usages: PostgreSQL user creation and the application `DATABASE_URL`.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None
- **Path**: None

### PostgreSQL database password

- **Variable(s)**:
  - Literal password: `fastapi_password`
  - Embedded connection string: `DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded plaintext in the Chef recipe
- **Usage context**:
  - Sets the PostgreSQL password for user `fastapi`.
  - Supplies the FastAPI database connection string in `/opt/fastapi-tutorial/.env`.
- **Migration requirement**:
  - Store the password in Ansible Vault or an external secret-management system.
  - Use the protected variable when creating the PostgreSQL user.
  - Use the same protected variable when rendering `DATABASE_URL`.
  - Do not commit the plaintext value to the Ansible role or inventory.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable lookups, TLS certificates, API keys, or tokens were detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Application source directory**:

- `/opt/fastapi-tutorial`

**Database objects to verify**:

- PostgreSQL role: `fastapi`
- PostgreSQL database: `fastapi_db`
- Database owner: `fastapi`
- Database privileges: `ALL` on `fastapi_db` for `fastapi`

**Service endpoints to check**:

- `fastapi-tutorial`: `0.0.0.0:8000`
- `postgresql`: `localhost:5432`

**Templates rendered**:

- Chef ERB templates: 0
- `/opt/fastapi-tutorial/.env`, created directly by a Chef `file` resource: 1
- `/etc/systemd/system/fastapi-tutorial.service`, created directly by a Chef `file` resource: 1

## Pre-flight checks:

```bash
# Verify installed system packages
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

# Verify the fastapi-tutorial application source directory
ls -ld /opt/fastapi-tutorial
ls -l /opt/fastapi-tutorial/requirements.txt

# Verify the fastapi-tutorial virtual environment
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn

# Verify fastapi-tutorial Python dependencies
/opt/fastapi-tutorial/venv/bin/pip check

# Verify the postgresql service
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql

# Verify the postgresql listening port
ss -tlnp | grep ':5432'
# Expected output: PostgreSQL listening on localhost:5432

# Verify the fastapi PostgreSQL role
sudo -u postgres psql -tAc \
  "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"
# Expected output: fastapi

# Verify the fastapi_db database and owner
sudo -u postgres psql -tAc \
  "SELECT datname, pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"
# Expected output: fastapi_db with owner fastapi

# Verify connectivity to fastapi_db as fastapi
PGPASSWORD='<retrieve-from-Ansible-Vault>' \
psql -h localhost -U fastapi -d fastapi_db -c "SELECT 1;"
# Expected output: a one-row result containing 1

# Verify the fastapi-tutorial environment file
cat /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' \
  /opt/fastapi-tutorial/.env

# Verify the fastapi-tutorial systemd unit
cat /etc/systemd/system/fastapi-tutorial.service
grep -E '^(Description|After|Type|User|WorkingDirectory|Environment|ExecStart|Restart|WantedBy)' \
  /etc/systemd/system/fastapi-tutorial.service

# Validate and reload the fastapi-tutorial systemd unit
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl daemon-reload

# Verify the fastapi-tutorial service
systemctl status fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial

# Verify the fastapi-tutorial process
ps aux | grep '[u]vicorn'
ps aux | grep '[a]pp.main:app'

# Verify the fastapi-tutorial endpoint
curl -i http://localhost:8000/
# Expected result: an HTTP response from the FastAPI application

# Verify the fastapi-tutorial listening port
ss -tlnp | grep ':8000'
# Expected output: a listener bound to 0.0.0.0:8000

# Review fastapi-tutorial logs
journalctl -u fastapi-tutorial --no-pager -n 100

# Review postgresql logs
journalctl -u postgresql --no-pager -n 100
```

The migration is complete when the `fastapi-tutorial` source directory, virtual environment, dependencies, protected environment configuration, systemd unit, service enablement, FastAPI endpoint on port `8000`, PostgreSQL service on port `5432`, PostgreSQL role `fastapi`, database `fastapi_db`, and database connectivity all pass these checks.