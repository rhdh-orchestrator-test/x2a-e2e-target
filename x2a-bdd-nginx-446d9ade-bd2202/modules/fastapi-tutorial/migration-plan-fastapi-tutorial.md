---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI Tutorial application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`, creates a Python virtual environment, installs dependencies, configures PostgreSQL with the `fastapi` role and `fastapi_db` database, writes an environment file, and runs the application through the `fastapi-tutorial` systemd service on port `8000`. It supports RHEL/Fedora and Debian/Ubuntu package sets. One FastAPI application instance and one PostgreSQL instance are configured.

## Service Type and Instances

**Service Type**: Application server with PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application server
  - Application source: `https://github.com/dibanez/fastapi_tutorial.git`
  - Git revision: `main`
  - Location/Path: `/opt/fastapi-tutorial`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Runs as: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Startup command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Listening address: `0.0.0.0`
  - Port: `8000`
  - Environment file: `/opt/fastapi-tutorial/.env`
  - Restart policy: `Restart=always`

- **postgresql**: PostgreSQL database service for the FastAPI application
  - Service name: `postgresql`
  - Service actions: enable and start
  - Database role: `fastapi`
  - Database name: `fastapi_db`
  - Database owner: `fastapi`
  - Host: `localhost`
  - Port: `5432`
  - Privilege: `ALL PRIVILEGES` on `fastapi_db`
  - RHEL/Fedora packages: `postgresql-server`, `postgresql-contrib`, `libpq-devel`
  - Debian/Ubuntu packages: `postgresql`, `postgresql-contrib`, `libpq-dev`
  - RHEL/Fedora initialization command: `postgresql-setup --initdb`

## File Structure

The supplied execution tree contains one recipe and no providers, templates, attributes, or static files.

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
```

**Files:**
```text
```

## Module Explanation

The cookbook performs operations in this order:

1. **Platform-specific package installation** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - On RHEL/Fedora platforms, installs `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, and `libpq-devel`.
   - Runs `postgresql-setup --initdb` on RHEL/Fedora.
   - The validation analysis does not confirm a `creates` guard or marker-file condition for PostgreSQL initialization. The Ansible migration must add an explicit idempotent initialization guard if required.
   - On Debian/Ubuntu platforms, installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Resources: one conditional `package` resource per platform branch and one RHEL/Fedora `execute[initialize_postgresql]` resource.

2. **Create the application directory** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/opt/fastapi-tutorial`.
   - The supplied plan specifies owner `root`, group `root`, mode `0755`, and recursive creation.
   - Ansible equivalent: `ansible.builtin.file` with `state: directory`, owner `root`, group `root`, and mode `0755`.
   - Resource: `directory[/opt/fastapi-tutorial]`.

3. **Synchronize the application repository** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git`.
   - Checks out revision `main`.
   - Places the repository at `/opt/fastapi-tutorial`.
   - Ansible equivalent: `ansible.builtin.git`.
   - Resource: `git[/opt/fastapi-tutorial]`, action `sync`.

4. **Create the Python virtual environment** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Runs `python3 -m venv /opt/fastapi-tutorial/venv`.
   - Uses `/opt/fastapi-tutorial/venv` as the completion path.
   - Ansible equivalent: `ansible.builtin.command` with a `creates` guard or an equivalent virtual-environment module.
   - Resource: `execute[create_venv]`.

5. **Install Python dependencies** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Runs `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt`.
   - Uses `/opt/fastapi-tutorial` as the working directory.
   - Installs dependencies into `/opt/fastapi-tutorial/venv`.
   - The Chef resource is an unconditional execute and runs on every convergence.
   - Ansible equivalent: `ansible.builtin.pip` with the virtual environment and requirements file, preferably with change detection.
   - Resource: `execute[install_dependencies]`.

6. **Enable and start PostgreSQL** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Enables the `postgresql` service.
   - Starts the `postgresql` service.
   - Resource: `service[postgresql]`, actions `enable` and `start`.

7. **Create the PostgreSQL role and database** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Executes PostgreSQL administration commands as the `postgres` operating-system user.
   - Creates the `fastapi` role with its password.
   - Creates the `fastapi_db` database with owner `fastapi`.
   - Grants `ALL PRIVILEGES` on `fastapi_db` to `fastapi`.
   - The original commands use `|| true`, which can hide failures and are not fully idempotent.
   - Ansible should use PostgreSQL-specific modules for role creation, password management, database creation, ownership, and privileges.
   - Resource: `execute[create_db_user]`.

8. **Create the application environment file** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/opt/fastapi-tutorial/.env`.
   - The supplied plan specifies the following inline content:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - The supplied plan specifies owner `root`, group `root`, and mode `0644`.
   - These inline values and properties were not independently confirmed by the validation analysis and must be verified against the recipe before being treated as authoritative.
   - Ansible should use `ansible.builtin.template` or `ansible.builtin.copy`, with the password supplied from Ansible Vault.
   - Resource: `file[/opt/fastapi-tutorial/.env]`.

9. **Create the systemd service unit** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/etc/systemd/system/fastapi-tutorial.service`.
   - The supplied plan specifies this unit content:
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
   - The supplied plan specifies owner `root`, group `root`, and mode `0644`.
   - The unit orders startup after `network.target` and `postgresql.service`.
   - It runs Uvicorn on `0.0.0.0:8000` as `root`.
   - The inline content and properties were not independently confirmed by the validation analysis and must be verified against the recipe.
   - Ansible should use `ansible.builtin.template` or `ansible.builtin.copy`.
   - Resource: `file[/etc/systemd/system/fastapi-tutorial.service]`.

10. **Reload systemd** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
    - Defines `execute[systemd_reload]` with command `systemctl daemon-reload`.
    - The resource has action `nothing`.
    - It runs immediately when the systemd unit file changes.
    - Ansible equivalent: a handler notified by changes to `/etc/systemd/system/fastapi-tutorial.service`.
    - Resource: `execute[systemd_reload]`.

11. **Enable and start the FastAPI service** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
    - Enables the `fastapi-tutorial` service.
    - Starts the `fastapi-tutorial` service.
    - Resource: `service[fastapi-tutorial]`, actions `enable` and `start`.

There are no `.each` loops or collection iterations in this cookbook.

The complete resource order is:

1. Conditional RHEL/Fedora `package`
2. RHEL/Fedora `execute[initialize_postgresql]`
3. Conditional Debian/Ubuntu `package`
4. `directory[/opt/fastapi-tutorial]`
5. `git[/opt/fastapi-tutorial]`
6. `execute[create_venv]`
7. `execute[install_dependencies]`
8. `service[postgresql]`
9. `execute[create_db_user]`
10. `file[/opt/fastapi-tutorial/.env]`
11. `file[/etc/systemd/system/fastapi-tutorial.service]`
12. Immediate `execute[systemd_reload]` when the unit changes
13. `service[fastapi-tutorial]`

The recipe does not explicitly restart `fastapi-tutorial` when the Git repository, Python dependencies, or `.env` file changes. The systemd unit's `Restart=always` only applies when the process exits. Ansible should normally notify a service restart when the environment file or application deployment changes.

## Dependencies

**External cookbook dependencies**: None listed in the supplied metadata.

**System package dependencies**:

- **RHEL/Fedora**: `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, `libpq-devel`
- **Debian/Ubuntu**: `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, `libpq-dev`

**Application dependency source**: `/opt/fastapi-tutorial/requirements.txt`

**Service dependencies**:

- `postgresql`
- `fastapi-tutorial`

**Systemd ordering dependency**: `After=network.target postgresql.service`

## Credentials

**Detection Summary**: 1 secret detected in 1 source file. The secret is `fastapi_password`, which is used directly for PostgreSQL role creation and embedded in the generated `DATABASE_URL`.

**Source**:

- **Provider**: Hardcoded in Chef recipe
- **URL**: None
- **Path**: `cookbooks/fastapi-tutorial/recipes/default.rb`

### PostgreSQL password

- **Variable/value**: `fastapi_password`
- **Source file**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded plaintext
- **Usage context**: Password for the `fastapi` PostgreSQL role and application database connectivity.
- **References**:
  ```bash
  CREATE USER fastapi WITH PASSWORD 'fastapi_password';
  ```
  ```dotenv
  DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
  ```
- **Ansible migration requirement**: Store the password in Ansible Vault and use the vaulted value both when creating the PostgreSQL role and when rendering `.env`.

### Database connection string

- **Variable**: `DATABASE_URL`
- **Source file**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Inline plaintext generated-file content
- **Value**: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Usage context**: FastAPI connection to the `fastapi_db` PostgreSQL database.
- **Sensitive component**: Embedded `fastapi_password`.
- **Ansible migration requirement**: Construct the connection string from separate variables for database user, vaulted password, host, and database name. Protect the resulting `.env` file with restrictive permissions.

No Chef data bags, encrypted data bags, Chef Vault, external secret providers, certificate files, private keys, API keys, or tokens were detected.

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
- Database owner `fastapi`
- `ALL PRIVILEGES` granted to `fastapi` on `fastapi_db`

**Service endpoints to check**:

- FastAPI: `0.0.0.0:8000`
- PostgreSQL: `localhost:5432`

**Templates rendered**: 0 cookbook templates. Two inline-content files are created:

1. `/opt/fastapi-tutorial/.env`
2. `/etc/systemd/system/fastapi-tutorial.service`

## Pre-flight checks

```bash
# Verify the application instance
test -d /opt/fastapi-tutorial
test -f /opt/fastapi-tutorial/requirements.txt
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
git -C /opt/fastapi-tutorial status --short
/opt/fastapi-tutorial/venv/bin/pip check

# Verify the FastAPI application instance
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl show fastapi-tutorial \
  --property=User \
  --property=WorkingDirectory \
  --property=ExecStart \
  --property=Restart
ss -tlnp | grep ':8000'
curl -i http://127.0.0.1:8000/
curl -i http://127.0.0.1:8000/docs
curl -i http://127.0.0.1:8000/openapi.json

# Verify the PostgreSQL instance on RHEL/Fedora
rpm -q python3 python3-pip git postgresql-server postgresql-contrib libpq-devel
test -f /var/lib/pgsql/data/PG_VERSION

# Verify the PostgreSQL instance on Debian/Ubuntu
dpkg -s python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

# Verify the PostgreSQL service
systemctl is-enabled postgresql
systemctl is-active postgresql
systemctl status postgresql --no-pager
ss -tlnp | grep ':5432'

# Verify the PostgreSQL role and database
sudo -u postgres psql -tAc "SELECT rolname FROM pg_roles WHERE rolname='fastapi';"
sudo -u postgres psql -tAc "SELECT datname FROM pg_database WHERE datname='fastapi_db';"
sudo -u postgres psql -tAc "SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname='fastapi_db';"

# Verify PostgreSQL authentication
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_database(), current_user;"

# Verify the environment file
test -f /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' /opt/fastapi-tutorial/.env
stat -c '%U:%G %a %n' /opt/fastapi-tutorial/.env

# Verify the FastAPI systemd unit
test -f /etc/systemd/system/fastapi-tutorial.service
systemctl cat fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial

# Verify service logs
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u postgresql --no-pager -n 100
journalctl -u fastapi-tutorial --no-pager | grep -Ei 'error|failed|traceback'
journalctl -u postgresql --no-pager | grep -Ei 'error|failed|fatal'

# Verify systemd reload behavior after a unit change
systemctl daemon-reload
systemctl restart fastapi-tutorial
systemctl is-active fastapi-tutorial
```