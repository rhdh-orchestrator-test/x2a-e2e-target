---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the `fastapi-tutorial` FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main`, installs Python, Git, and PostgreSQL dependencies, creates a Python virtual environment, installs application requirements, configures the PostgreSQL role and database, writes an application `.env` file, and manages the `fastapi-tutorial` systemd service. The reported application path is `/opt/fastapi-tutorial`, and the reported service listens on `0.0.0.0:8000`. Attribute values, resource properties, and systemd content should be confirmed against the source files because the supplied structured analysis does not independently verify all of these details.

## Service Type and Instances

**Service Type**: Application Server with PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application managed by systemd
  - Application path: `/opt/fastapi-tutorial` *(reported; verify from attributes)*
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git` *(reported; verify from recipe)*
  - Revision: `main` *(reported; verify from recipe)*
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Dependency file: `/opt/fastapi-tutorial/requirements.txt`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service` *(reported; verify `service_name`)*
  - Service user: `root` *(reported; verify unit content)*
  - Working directory: `/opt/fastapi-tutorial` *(reported; verify unit content)*
  - Start command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000` *(reported; verify unit content)*
  - Listening address: `0.0.0.0`
  - Listening port: `8000` *(reported from `service_port`; verify attributes and unit)*
  - Restart policy: `Restart=always` *(reported; verify unit content)*
  - Startup dependency: `network.target` and `postgresql.service` *(reported; verify unit content)*

### PostgreSQL database configuration

The reported application database configuration is:

- Database user: `fastapi`
- Database password: `fastapi_password`
- Database: `fastapi_db`
- Database owner: `fastapi`
- Grant: `ALL PRIVILEGES` on `fastapi_db` to `fastapi`
- PostgreSQL connection host: `localhost`

These values should be confirmed against the recipe before migration.

## File Structure

The supplied plan identifies one recipe and one attribute file. Provider, template, static file, metadata, and iteration claims were not independently represented in the structured validation summary.

**Recipes:**
```text
cookbooks/fastapi-tutorial/recipes/default.rb
```

**Providers:**
```text
```

**Templates:**
```text
```

**Attributes:**
```text
cookbooks/fastapi-tutorial/attributes/default.rb
```

**Files:**
```text
```

## Module Explanation

The cookbook performs operations in this order. The resolved values below are reported by the original plan and must be verified against the recipe and attribute file where noted.

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Selects platform-specific operating-system packages.
   - On RHEL/Fedora platforms, installs:
     - `python3`
     - `python3-pip`
     - `git`
     - `postgresql-server`
     - `postgresql-contrib`
     - `libpq-devel`
   - On non-RHEL/Fedora platforms, installs:
     - `python3`
     - `python3-pip`
     - `python3-venv`
     - `git`
     - `postgresql`
     - `postgresql-contrib`
     - `libpq-dev`
   - On RHEL/Fedora platforms, runs `postgresql-setup --initdb`. The reported guard is `/var/lib/pgsql/data/PG_VERSION`, but the guard must be confirmed in the recipe before migrating it as `creates: /var/lib/pgsql/data/PG_VERSION`.
   - Creates the reported application directory `/opt/fastapi-tutorial` with owner `root`, group `root`, mode `0755`, and recursive creation. These resolved properties must be confirmed from the recipe and attributes.
   - Synchronizes the Git repository to `/opt/fastapi-tutorial` using the reported repository `https://github.com/dibanez/fastapi_tutorial.git`, revision `main`, and action `sync`. The repository and revision must be confirmed from the recipe.
   - Runs `python3 -m venv /opt/fastapi-tutorial/venv`. The reported idempotency path is `/opt/fastapi-tutorial/venv`, but the source analysis does not confirm a `creates` guard.
   - Runs `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt` with working directory `/opt/fastapi-tutorial`.
   - Enables and starts `service[postgresql]`.
   - Creates PostgreSQL role `fastapi` with password `fastapi_password`.
   - Creates PostgreSQL database `fastapi_db` owned by `fastapi`.
   - Grants all privileges on `fastapi_db` to `fastapi`.
   - The original shell commands use `sudo -u postgres` and `|| true`; the Ansible migration should use idempotent PostgreSQL modules while preserving the resulting state.
   - Writes the reported environment file `/opt/fastapi-tutorial/.env` with owner `root`, group `root`, and mode `0644`. The file metadata and content must be confirmed from the recipe.
   - The reported `.env` content is:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Writes the reported systemd unit `/etc/systemd/system/fastapi-tutorial.service`. The service name, unit content, ownership, and mode must be confirmed from the local variable and file resource.
   - The reported unit content is:
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
   - Defines `execute[systemd_reload]` with command `systemctl daemon-reload` and action `nothing`.
   - The original plan reports that the unit file notifies `execute[systemd_reload]` when changed. The notification relationship must be confirmed in the recipe before implementing the handler.
   - Enables and starts the reported `fastapi-tutorial` service.
   - No `.each` loops or collection iterations are identified in the supplied plan.

## Dependencies

**External cookbook dependencies**: None listed in `metadata.rb` according to the original plan; the metadata file was not included in the supplied structured validation summary.

**System package dependencies**:

RHEL/Fedora branch:

- `python3`
- `python3-pip`
- `git`
- `postgresql-server`
- `postgresql-contrib`
- `libpq-devel`

Non-RHEL/Fedora branch:

- `python3`
- `python3-pip`
- `python3-venv`
- `git`
- `postgresql`
- `postgresql-contrib`
- `libpq-dev`

**Application dependency installation**:

- Requirements file: `/opt/fastapi-tutorial/requirements.txt`
- Installer: `/opt/fastapi-tutorial/venv/bin/pip`

**Service dependencies**:

- `postgresql.service`
- `fastapi-tutorial.service`
- `network.target`

The reported FastAPI unit declares:

```ini
After=network.target postgresql.service
```

## Credentials

**Detection Summary**: One hardcoded PostgreSQL credential was detected in one source file and used in two configuration contexts.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None
- **Path**: `cookbooks/fastapi-tutorial/recipes/default.rb`

### PostgreSQL application database password

- **Variable(s)**:
  - Current Chef value: literal `fastapi_password`
  - Target Ansible variable: `fastapi_db_password`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded plaintext in the recipe
- **Target storage**: Ansible Vault, AAP credentials, or another protected secret store
- **Usage context**:
  1. PostgreSQL role creation:
     ```sql
     CREATE USER fastapi WITH PASSWORD 'fastapi_password';
     ```
  2. Application database URL:
     ```dotenv
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```

The generated `/opt/fastapi-tutorial/.env` file is also sensitive because it contains the password in plaintext. The original mode is reported as `0644` and should be tightened during migration unless application requirements prohibit it.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, TLS certificates, API keys, or tokens were detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/fastapi-tutorial/recipes/default.rb`
- `cookbooks/fastapi-tutorial/attributes/default.rb`
- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- RHEL/Fedora PostgreSQL data directory: `/var/lib/pgsql/data`
- Non-RHEL/Fedora distribution-managed PostgreSQL data directory
- PostgreSQL database: `fastapi_db`
- PostgreSQL role: `fastapi`

**Service endpoints to check**:

- `fastapi-tutorial`: TCP `0.0.0.0:8000`
- PostgreSQL: local `localhost` connection using the distribution-default PostgreSQL socket or local connection mechanism

**Templates rendered**:

- No templates identified.
- `/opt/fastapi-tutorial/.env`: inline file resource, reported render count one
- `/etc/systemd/system/fastapi-tutorial.service`: inline file resource, reported render count one

## Pre-flight checks

Run the following checks after applying the Ansible migration.

### Instance: fastapi-tutorial

```bash
test -d /opt/fastapi-tutorial
test -f /opt/fastapi-tutorial/requirements.txt
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -f /opt/fastapi-tutorial/.env
test -f /etc/systemd/system/fastapi-tutorial.service
```

Verify the repository and reported revision:

```bash
git -C /opt/fastapi-tutorial remote -v
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
```

Expected values:

```text
Repository: https://github.com/dibanez/fastapi_tutorial.git
Revision: main
```

Verify the virtual environment and dependencies:

```bash
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip list
```

Verify environment-file metadata without exposing its contents:

```bash
stat -c '%U %G %a %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' /opt/fastapi-tutorial/.env \
  | sed 's#\(DATABASE_URL=postgresql://[^:]*:\)[^@]*#\1REDACTED#'
```

Verify the service unit and systemd state:

```bash
systemctl daemon-reload
systemctl cat fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl show fastapi-tutorial \
  --property=ExecStart,User,WorkingDirectory,Environment,After,Restart
```

Verify the expected application command:

```bash
grep -E '^(Description|After|Type|User|WorkingDirectory|Environment|ExecStart|Restart|WantedBy)=' \
  /etc/systemd/system/fastapi-tutorial.service
```

Verify the process and endpoint:

```bash
ps aux | grep '[u]vicorn app.main:app'
ss -tlnp | grep ':8000'
curl -i http://127.0.0.1:8000/
```

Check application logs and restart policy:

```bash
systemctl status fastapi-tutorial
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u fastapi-tutorial --no-pager \
  | grep -E 'ERROR|Traceback|Failed|Exception'
systemctl show fastapi-tutorial --property=Restart
```

Expected restart setting:

```text
Restart=always
```

### Database: fastapi_db

Verify PostgreSQL service state:

```bash
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
```

Verify the PostgreSQL role:

```bash
sudo -u postgres psql -tAc \
  "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"
```

Expected result:

```text
fastapi
```

Verify the database:

```bash
sudo -u postgres psql -tAc \
  "SELECT datname FROM pg_database WHERE datname = 'fastapi_db';"
```

Expected result:

```text
fastapi_db
```

Verify database ownership:

```bash
sudo -u postgres psql -tAc \
  "SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"
```

Expected result:

```text
fastapi
```

Verify application credentials and database connectivity:

```bash
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_database(), current_user;"
```

Verify a basic query:

```bash
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT 1;"
```

Check PostgreSQL logs:

```bash
journalctl -u postgresql --no-pager -n 100
```

### Platform package and initialization checks

For RHEL/Fedora targets:

```bash
rpm -q python3 python3-pip git postgresql-server postgresql-contrib libpq-devel
test -f /var/lib/pgsql/data/PG_VERSION
```

For non-RHEL/Fedora targets:

```bash
dpkg -s python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev
```

The PostgreSQL initialization guard and resulting data path must match the target distribution and the verified Chef recipe behavior.

### Application dependency installation check

```bash
cd /opt/fastapi-tutorial
/opt/fastapi-tutorial/venv/bin/pip install \
  -r /opt/fastapi-tutorial/requirements.txt
```

Confirm the application remains active after PostgreSQL is available:

```bash
systemctl is-active postgresql
systemctl is-active fastapi-tutorial
ss -tlnp | grep ':8000'
```
