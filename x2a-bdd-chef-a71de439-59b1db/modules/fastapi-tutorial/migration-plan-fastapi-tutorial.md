---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI Tutorial application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` under `/opt/fastapi-tutorial`, creates a Python virtual environment, installs application dependencies, initializes and starts PostgreSQL, creates the `fastapi` role and `fastapi_db` database, writes the application database URL to `/opt/fastapi-tutorial/.env`, and manages the application with the `fastapi-tutorial` systemd service. Uvicorn listens on TCP port `8000`, while PostgreSQL uses its platform-default local port, normally `5432`.

## Service Type and Instances

**Service Type**: Application Server with PostgreSQL database dependency

**Configured Instances**:

- **FastAPI Tutorial application**: FastAPI application served by Uvicorn
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Location/Path: `/opt/fastapi-tutorial`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Service name: `fastapi-tutorial`
  - Startup command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Runs as: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Port/Socket: TCP `8000`, bound to `0.0.0.0`
  - Restart policy: `Restart=always`
  - Key configuration: `PROJECT_NAME="FastAPI Tutorial"`, `API_VERSION=1.0.0`, and a PostgreSQL `DATABASE_URL`

- **PostgreSQL database**: Local database service for the FastAPI application
  - Service name: `postgresql`
  - Database user: `fastapi`
  - Database name: `fastapi_db`
  - Database owner: `fastapi`
  - Connection host: `localhost`
  - Port/Socket: Platform-default PostgreSQL port, normally TCP `5432`; the recipe does not explicitly configure the port
  - Connection URL: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
  - Required privileges: All privileges on `fastapi_db` granted to `fastapi`

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

The `.env` file and systemd unit are created directly with Chef `file` resources. They are not static cookbook files.

## Module Explanation

The cookbook performs operations in this order:

1. **Platform-specific system package installation** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - On Fedora/RHEL-family systems, installs `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, and `libpq-devel`.
   - The Chef condition is `platform_family?('fedora', 'rhel')`.
   - The Ansible implementation must use the equivalent `ansible_facts['os_family'] in ['RedHat', 'Fedora']` condition.

2. **Initialize PostgreSQL on Fedora/RHEL systems** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Runs `postgresql-setup --initdb`.
   - Executes only when `/var/lib/pgsql/data/PG_VERSION` does not exist.
   - Applies only to Fedora/RHEL-family systems.

3. **Install system packages on non-Fedora/RHEL systems** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - On other supported platforms, including Ubuntu, installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - The RHEL and Debian package lists must remain mutually exclusive.

4. **Create the application directory** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/opt/fastapi-tutorial` recursively.
   - Sets owner `root`, group `root`, and mode `0755`.

5. **Synchronize the application repository** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Checks out `https://github.com/dibanez/fastapi_tutorial.git` into `/opt/fastapi-tutorial`.
   - Synchronizes revision `main`.
   - Runs before virtual-environment creation and dependency installation.

6. **Create the Python virtual environment** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Runs `python3 -m venv /opt/fastapi-tutorial/venv`.
   - Runs only when `/opt/fastapi-tutorial/venv` does not exist.
   - Runs after repository synchronization.

7. **Install Python dependencies** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Runs `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt`.
   - Uses `/opt/fastapi-tutorial` as the working directory.
   - The `requirements.txt` file comes from the checked-out Git repository.
   - Runs after the repository and virtual environment exist.

8. **Enable and start PostgreSQL** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Enables the `postgresql` service.
   - Starts the `postgresql` service.
   - Runs before database role and database creation.

9. **Create the PostgreSQL role, database, and privileges** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates PostgreSQL role `fastapi` with password `fastapi_password`.
   - Creates database `fastapi_db` owned by `fastapi`.
   - Grants all privileges on `fastapi_db` to `fastapi`.
   - The Chef implementation uses `sudo -u postgres psql` commands with `|| true` to ignore already-existing objects.
   - The Ansible implementation should use idempotent `community.postgresql.postgresql_user`, `community.postgresql.postgresql_db`, and `community.postgresql.postgresql_privs` modules.

10. **Create the application environment file** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
    - Creates `/opt/fastapi-tutorial/.env`.
    - Sets owner `root`, group `root`, and mode `0644`.
    - Writes:
      ```dotenv
      PROJECT_NAME="FastAPI Tutorial"
      API_VERSION=1.0.0
      DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
      ```
    - The database password should preferably be supplied through Ansible Vault or an AAP credential while preserving the resulting application configuration.

11. **Create the systemd unit** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
    - Creates `/etc/systemd/system/fastapi-tutorial.service`.
    - Sets owner `root`, group `root`, and mode `0644`.
    - Uses the following unit configuration:
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
    - Starts after `network.target` and orders after `postgresql.service`.
    - Runs Uvicorn as `root` from `/opt/fastapi-tutorial`.
    - Binds to `0.0.0.0` on port `8000`.
    - Restarts automatically when it exits.

12. **Reload systemd when the unit changes** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
    - Defines `systemctl daemon-reload`.
    - Uses a `nothing` action.
    - Triggers immediately when `/etc/systemd/system/fastapi-tutorial.service` changes.
    - The Ansible equivalent should be a handler using `ansible.builtin.systemd` with `daemon_reload: true`.

13. **Enable and start the FastAPI service** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
    - Enables the `fastapi-tutorial` service.
    - Starts the `fastapi-tutorial` service.
    - Ensures the systemd daemon-reload handler has run before starting or restarting the service.

## Dependencies

**External cookbook dependencies**: None listed in the analyzed metadata.

**System package dependencies**:

- Fedora/RHEL-family:
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

**Application dependency source**: `/opt/fastapi-tutorial/requirements.txt`, obtained from the Git repository and installed into `/opt/fastapi-tutorial/venv`.

**Service dependencies**:

- `postgresql`
- `fastapi-tutorial`
- The FastAPI systemd unit declares `After=network.target postgresql.service`.

## Credentials

**Detection Summary**: 1 credential detected in 1 source file. The same hardcoded password is used in the database creation command and the application connection URL.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None
- **Path**: None
- **Source file**: `cookbooks/fastapi-tutorial/recipes/default.rb`

### PostgreSQL password

- **Variable(s)**:
  - No Chef variable is used.
  - Literal password: `fastapi_password`
  - Database username: `fastapi`
  - Database URL: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded plaintext
- **Usage context**:
  - Used in `CREATE USER fastapi WITH PASSWORD 'fastapi_password'`.
  - Embedded in `/opt/fastapi-tutorial/.env` as part of `DATABASE_URL`.
  - Used by the FastAPI application to connect to the local PostgreSQL database.
- **Migration guidance**:
  - Store the password in Ansible Vault or an AAP credential.
  - Do not commit the password directly to the Ansible playbook.
  - Render the `.env` file from a protected variable while preserving the final `DATABASE_URL` format.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, HashiCorp Vault, AWS Secrets Manager, environment-variable secret lookup, TLS certificate, private key, API token, or SSH credential reference was detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- `/var/lib/pgsql/data/PG_VERSION` on Fedora/RHEL systems

**Service endpoints to check**:

- FastAPI Tutorial application: `0.0.0.0:8000`
- PostgreSQL database: `localhost:5432`, normally
- PostgreSQL local Unix socket: platform default; no socket path is explicitly configured

**Database objects to verify**:

- PostgreSQL role: `fastapi`
- PostgreSQL database: `fastapi_db`
- Database owner: `fastapi`
- Database privileges: all privileges granted to `fastapi`

**Templates rendered**: None. The cookbook does not use ERB templates.

**Static files deployed**: None. The `.env` file and systemd unit are created inline with Chef `file` resources.

## Pre-flight checks

```bash
# Identify the operating system family
cat /etc/os-release

# Verify Python
python3 --version
python3 -m pip --version

# Verify Git
git --version

# Verify PostgreSQL client
psql --version
```

### FastAPI Tutorial application checks

```bash
# Verify the application directory and ownership
ls -ld /opt/fastapi-tutorial
stat -c '%U:%G %a %n' /opt/fastapi-tutorial

# Verify the repository
git -C /opt/fastapi-tutorial remote -v
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
git -C /opt/fastapi-tutorial log -1 --oneline

# Verify the dependency file
test -f /opt/fastapi-tutorial/requirements.txt
echo "requirements.txt exit code: $?"

# Verify the virtual environment
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip list

# Verify the FastAPI service
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl status fastapi-tutorial --no-pager

# Verify the application process and port
ps aux | grep '[u]vicorn app.main:app'
ss -tlnp | grep ':8000'

# Test the application endpoint
curl -i http://127.0.0.1:8000/

# Test the documentation endpoint when exposed by the application
curl -i http://127.0.0.1:8000/docs
```

The root endpoint may return `200`, `404`, or another valid application response. The required result is an HTTP response rather than a connection failure.

### PostgreSQL database checks

```bash
# On Fedora/RHEL systems, verify PostgreSQL initialization
test -f /var/lib/pgsql/data/PG_VERSION
echo "PostgreSQL initialization marker exit code: $?"

# Verify the PostgreSQL service
systemctl status postgresql --no-pager
systemctl is-enabled postgresql
systemctl is-active postgresql

# Verify the PostgreSQL endpoint
ss -ltnp | grep ':5432'

# Verify the fastapi role
sudo -u postgres psql -tAc \
  "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"

# Verify fastapi_db and its owner
sudo -u postgres psql -tAc \
  "SELECT datname, pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"

# Verify application-user connectivity
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_user, current_database();"

# Verify database privileges
sudo -u postgres psql -c "\l+ fastapi_db"
```

Expected PostgreSQL results:

- Role `fastapi` exists.
- Database `fastapi_db` exists.
- Database owner is `fastapi`.
- The `fastapi` user can connect successfully.
- `fastapi` has all privileges on `fastapi_db`.

### Environment file checks

```bash
# Verify ownership and mode
stat -c '%U:%G %a %n' /opt/fastapi-tutorial/.env

# Verify non-secret configuration keys
grep -E '^(PROJECT_NAME|API_VERSION)=' /opt/fastapi-tutorial/.env

# Verify the database URL exists without exposing its value in logs
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env
```

Do not print the database password in shared CI or migration logs. Use protected commands or redact the value during production validation.

### Systemd unit checks

```bash
# Verify ownership, mode, and contents
stat -c '%U:%G %a %n' /etc/systemd/system/fastapi-tutorial.service
cat /etc/systemd/system/fastapi-tutorial.service

# Validate the unit
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service

# Reload and verify the service
systemctl daemon-reload
systemctl is-enabled fastapi-tutorial
systemctl status fastapi-tutorial --no-pager

# Verify important unit settings
grep -E '^(Description|After|Type|User|WorkingDirectory|Environment|ExecStart|Restart|WantedBy)=' \
  /etc/systemd/system/fastapi-tutorial.service
```

### Service logs

```bash
# PostgreSQL logs
journalctl -u postgresql --no-pager -n 100

# FastAPI Tutorial logs
journalctl -u fastapi-tutorial --no-pager -n 100

# Follow FastAPI Tutorial logs during testing
journalctl -u fastapi-tutorial -f
```

Verify successful PostgreSQL startup, successful Uvicorn startup, database authentication, Python module loading, binding to port `8000`, and the absence of repeated service restart failures.