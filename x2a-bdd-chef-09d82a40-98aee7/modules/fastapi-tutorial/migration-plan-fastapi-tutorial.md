---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the `main` branch of `https://github.com/dibanez/fastapi_tutorial.git` to `/opt/fastapi-tutorial`, installs Python, Git, PostgreSQL, and PostgreSQL development libraries, creates a Python virtual environment, installs application dependencies, initializes and manages PostgreSQL, creates the `fastapi` user and `fastapi_db` database, writes the application environment file, and manages a systemd service named `fastapi-tutorial` listening on port `8000`. The PostgreSQL password is hardcoded in the Chef recipe and must be replaced with an Ansible Vault or approved credential source.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application server
  - Location/Path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Dependency file: `/opt/fastapi-tutorial/requirements.txt`
  - Entry point: `app.main:app`
  - Process command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Listen address: `0.0.0.0`
  - Port: `8000`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Runtime user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Restart policy: `Restart=always`
  - Environment PATH: `/opt/fastapi-tutorial/venv/bin`

- **postgresql**: PostgreSQL database service
  - Service name: `postgresql`
  - State: enabled and started
  - Connection host: `localhost`
  - Port: `5432`
  - Database user: `fastapi`
  - Database name: `fastapi_db`
  - Database owner: `fastapi`
  - RHEL/Fedora packages: `postgresql-server`, `postgresql-contrib`, `libpq-devel`
  - Debian/Ubuntu packages: `postgresql`, `postgresql-contrib`, `libpq-dev`
  - RHEL/Fedora initialization command: `postgresql-setup --initdb`
  - RHEL/Fedora initialization marker: `/var/lib/pgsql/data/PG_VERSION`

No collection attributes, `.each` loops, or configured multi-item iterations exist in the supplied execution tree.

## File Structure

```text
cookbooks/fastapi-tutorial/
├── recipes/
│   └── default.rb
├── providers/
├── templates/
├── attributes/
└── files/
```

**Recipes:**
```text
recipes/default.rb
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

The cookbook does not use Chef templates, custom resource providers, static cookbook files, or attribute files.

## Module Explanation

The cookbook performs operations in this order:

1. **Platform-specific package installation** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - On RHEL/Fedora, installs `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, and `libpq-devel`.
   - Runs `postgresql-setup --initdb` using `/var/lib/pgsql/data/PG_VERSION` as the idempotence marker.
   - On Debian/Ubuntu, installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Resources: one `package` resource per platform branch and one RHEL/Fedora `execute[initialize_postgresql]` resource.

2. **Create the application directory** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/opt/fastapi-tutorial`.
   - Sets owner and group to `root`.
   - Sets mode to `0755`.
   - Enables recursive creation.

3. **Synchronize the application repository** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Synchronizes `/opt/fastapi-tutorial` from `https://github.com/dibanez/fastapi_tutorial.git`.
   - Checks out revision `main`.
   - The repository provides `/opt/fastapi-tutorial/requirements.txt` and the application entry point.

4. **Create the Python virtual environment** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Runs `python3 -m venv /opt/fastapi-tutorial/venv`.
   - Uses `/opt/fastapi-tutorial/venv` as the idempotence marker.

5. **Install Python dependencies** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Runs `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt`.
   - Uses `/opt/fastapi-tutorial` as the working directory.
   - Ansible may use `ansible.builtin.pip` with the virtual environment and requirements file while preserving equivalent behavior.

6. **Enable and start PostgreSQL** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Enables and starts `postgresql`.
   - PostgreSQL must be running before database objects are created.

7. **Create the PostgreSQL user and database** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates PostgreSQL user `fastapi`.
   - Sets its password to the migrated secret.
   - Creates database `fastapi_db` owned by `fastapi`.
   - Grants all privileges on `fastapi_db` to `fastapi`.
   - The Chef implementation executes these operations as the operating-system `postgres` user and ignores errors with `|| true`.
   - The Ansible migration should use idempotent `community.postgresql.postgresql_user`, `community.postgresql.postgresql_db`, and, if required, `community.postgresql.postgresql_privs` tasks with `become_user: postgres`.

8. **Create the application environment file** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/opt/fastapi-tutorial/.env`.
   - Sets owner and group to `root`.
   - Chef mode is `0644`; Ansible should preferably use `0600` because the file contains credentials.
   - Preserves:
     - `PROJECT_NAME="FastAPI Tutorial"`
     - `API_VERSION=1.0.0`
     - `DATABASE_URL=postgresql://fastapi:<vaulted-password>@localhost/fastapi_db`
   - The password must be URL-encoded when required.

9. **Create the systemd service unit** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/etc/systemd/system/fastapi-tutorial.service`.
   - Sets owner and group to `root`.
   - Sets mode to `0644`.
   - Defines service `fastapi-tutorial` with:
     - `Type=simple`
     - `User=root`
     - `WorkingDirectory=/opt/fastapi-tutorial`
     - `Environment="PATH=/opt/fastapi-tutorial/venv/bin"`
     - `ExecStart=/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
     - `Restart=always`
     - `After=network.target postgresql.service`
     - `WantedBy=multi-user.target`

10. **Reload systemd** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
    - Defines `execute[systemd_reload]` with command `systemctl daemon-reload`.
    - The resource has action `nothing` unless notified.
    - The service unit file notifies this resource immediately when changed.
    - Ansible should use a handler with `ansible.builtin.systemd: daemon_reload: true`.

11. **Enable and start the FastAPI service** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
    - Enables and starts `fastapi-tutorial`.
    - Runs after the repository, virtual environment, dependencies, PostgreSQL, database objects, `.env`, systemd unit, and systemd reload are complete.

## Dependencies

**External cookbook dependencies**: None declared.

**System package dependencies**:

- **RHEL/Fedora**: `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, `libpq-devel`
- **Debian/Ubuntu**: `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, `libpq-dev`

**Service dependencies**:

- `postgresql`
- `fastapi-tutorial`

**Application dependency source**:

- `/opt/fastapi-tutorial/requirements.txt`

## Credentials

**Detection Summary**: 1 credential detected in 1 recipe file and used in both PostgreSQL user creation and the application connection string.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None
- **Path**: None

### PostgreSQL database password

- **Variable(s)**:
  - No Chef variable is used.
  - Literal password: `fastapi_password`
  - Connection string: `DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in recipe content
- **Usage context**:
  - Sets the password for PostgreSQL user `fastapi`.
  - Is embedded in `/opt/fastapi-tutorial/.env`.
  - Provides FastAPI with PostgreSQL connection credentials.
- **Required migration handling**:
  - Store the password in Ansible Vault, an AAP credential, or another approved secret-management integration.
  - Use the vaulted value for the PostgreSQL user task and `.env`.
  - Do not commit `fastapi_password` to the Ansible project.

No Chef data bags, encrypted data bags, Chef Vault calls, CyberArk integrations, Conjur variables, AWS Secrets Manager references, environment-variable secret lookups, TLS certificates, private keys, API keys, or tokens were detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- `/var/lib/pgsql/data/PG_VERSION` on RHEL/Fedora
- The installed PostgreSQL cluster data directory on Debian/Ubuntu

**Service endpoints to check**:

- FastAPI: `0.0.0.0:8000`
- PostgreSQL: `localhost:5432`
- PostgreSQL local Unix socket: discover with `SHOW unix_socket_directories;`

**Templates rendered**:

- None.
- Inline file resources rendered:
  - `/opt/fastapi-tutorial/.env`: 1
  - `/etc/systemd/system/fastapi-tutorial.service`: 1

## Pre-flight checks

### FastAPI instance: `fastapi-tutorial`

```bash
# Verify application directory and repository
ls -ld /opt/fastapi-tutorial
test -f /opt/fastapi-tutorial/requirements.txt
test -f /opt/fastapi-tutorial/app/main.py
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
git -C /opt/fastapi-tutorial log -1 --oneline

# Verify virtual environment and dependencies
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn
/opt/fastapi-tutorial/venv/bin/pip list
/opt/fastapi-tutorial/venv/bin/python -c "from app.main import app; print(app)"

# Verify environment file without exposing the password
stat -c '%U %G %a %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION)=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env | sed -E 's#(postgresql://[^:]+:)[^@]+@#\1********@#'

# Verify systemd unit and service
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl daemon-reload
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl status fastapi-tutorial --no-pager
systemctl show fastapi-tutorial \
  --property=User,WorkingDirectory,ExecStart,Restart,Environment
journalctl -u fastapi-tutorial --no-pager -n 50

# Verify port 8000 and HTTP response
ss -ltnp | grep ':8000'
curl -i http://127.0.0.1:8000/
curl -i http://localhost:8000/
ps aux | grep '[u]vicorn app.main:app'
```

Expected values:

- User: `root`
- Working directory: `/opt/fastapi-tutorial`
- Executable: `/opt/fastapi-tutorial/venv/bin/uvicorn`
- Application: `app.main:app`
- Port: `8000`
- Restart policy: `always`

### PostgreSQL instance: `postgresql`

```bash
# Verify service state
systemctl status postgresql --no-pager
systemctl is-enabled postgresql
systemctl is-active postgresql

# Verify RHEL/Fedora initialization
test -f /var/lib/pgsql/data/PG_VERSION && echo "PostgreSQL initialized"

# Verify PostgreSQL listener and local access
ss -ltnp | grep ':5432'
sudo -u postgres psql -c "SELECT version();"
sudo -u postgres psql -c "SHOW unix_socket_directories;"

# Verify role and database
sudo -u postgres psql -tAc \
  "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"
sudo -u postgres psql -tAc \
  "SELECT datname FROM pg_database WHERE datname = 'fastapi_db';"
sudo -u postgres psql -tAc \
  "SELECT datname, pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"

# Verify privileges
sudo -u postgres psql -c "\du fastapi"
sudo -u postgres psql -c "\l+ fastapi_db"

# Verify application credentials without committing or displaying the password
PGPASSWORD='<retrieve-from-approved-secret-source>' \
  psql -h localhost -U fastapi -d fastapi_db -c "SELECT 1;"

# Verify application database integration
PGPASSWORD='<retrieve-from-approved-secret-source>' \
  psql -h localhost -U fastapi -d fastapi_db \
  -c "SELECT current_database(), current_user;"
```

Expected values:

- PostgreSQL is enabled and active.
- PostgreSQL listens on `localhost:5432`.
- Role `fastapi` exists.
- Database `fastapi_db` exists.
- `fastapi_db` is owned by `fastapi`.
- User `fastapi` can connect and execute `SELECT 1`.

### Platform and package checks

```bash
cat /etc/os-release
python3 --version
python3 -m pip --version
git --version

# Debian/Ubuntu
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

# RHEL/Fedora
rpm -q python3 python3-pip git postgresql-server postgresql-contrib libpq-devel
```

On Debian/Ubuntu, `python3-venv` must be installed. On RHEL/Fedora, PostgreSQL initialization must create `/var/lib/pgsql/data/PG_VERSION`.