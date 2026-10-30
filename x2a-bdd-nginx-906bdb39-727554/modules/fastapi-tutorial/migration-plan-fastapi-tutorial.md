---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the `fastapi-tutorial` FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` on Ubuntu or CentOS. It installs Python, Git, PostgreSQL, and PostgreSQL development packages; creates a Python virtual environment; installs application dependencies; creates the `fastapi` PostgreSQL user and `fastapi_db` database; writes an environment file; and manages a systemd service listening on `0.0.0.0:8000`. The application runs from `/opt/fastapi-tutorial` under `root` and is supervised by `fastapi-tutorial.service`.

## Service Type and Instances

**Service Type**: Application Server

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application server backed by PostgreSQL
  - Location/Path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Dependency file: `/opt/fastapi-tutorial/requirements.txt`
  - Command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Port/Socket: `0.0.0.0:8000`
  - Working directory: `/opt/fastapi-tutorial`
  - Run user: `root`
  - Restart policy: `Restart=always`
  - systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Environment file: `/opt/fastapi-tutorial/.env`
  - Database: `fastapi_db`
  - Database user: `fastapi`
  - Database host: `localhost`
  - Database connection string: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
  - Key configuration: FastAPI with Uvicorn, PostgreSQL dependency, systemd supervision, and `PATH=/opt/fastapi-tutorial/venv/bin`

No collection attributes or `.each` loops are present. The cookbook configures one instance named `fastapi-tutorial`.

## File Structure

Only the recipe file is executed or referenced by the supplied execution tree. The `.env` file and systemd unit are generated inline by Chef resources; they are not cookbook template or static files.

**Recipes:**

```text
cookbooks/fastapi-tutorial/recipes/default.rb
```

**Providers:**

```text
```

No custom resources or provider files are used.

**Templates:**

```text
```

No `.erb` templates are rendered.

**Attributes:**

```text
```

No attribute files are used.

**Files:**

```text
```

No cookbook static files are deployed with `cookbook_file` or `remote_file`.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the seven system packages `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev` using one `package` resource.
   - Creates `/opt/fastapi-tutorial` as a recursive directory owned by `root:root` with mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates `/opt/fastapi-tutorial/venv` with `python3 -m venv`; the command is guarded by `creates: /opt/fastapi-tutorial/venv`.
   - Installs dependencies from `/opt/fastapi-tutorial/requirements.txt` into `/opt/fastapi-tutorial/venv` using `/opt/fastapi-tutorial/venv/bin/pip`.
   - Enables and starts the `postgresql` service.
   - Executes PostgreSQL initialization as the `postgres` operating-system user:
     - Creates role `fastapi` with password `fastapi_password`.
     - Creates database `fastapi_db` owned by `fastapi`.
     - Grants all privileges on `fastapi_db` to `fastapi`.
     - The original shell commands use `|| true`; the Ansible migration should use idempotent PostgreSQL modules instead of suppressing all errors.
   - Creates `/opt/fastapi-tutorial/.env` owned by `root:root` with mode `0644`, containing:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Creates `/etc/systemd/system/fastapi-tutorial.service` owned by `root:root` with mode `0644`, containing:
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
   - Notifies `execute[systemd_reload]` immediately when the systemd unit changes.
   - Runs `systemctl daemon-reload` only when notified; the `systemd_reload` resource has action `:nothing` during normal convergence.
   - Enables and starts the `fastapi-tutorial` service after the application directory, repository, virtual environment, dependencies, PostgreSQL service, database objects, environment file, and systemd unit are ready.
   - The Chef recipe does not explicitly restart `fastapi-tutorial` when `.env` or the unit file changes. A unit-file change triggers only `systemctl daemon-reload`.

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

**Service dependencies**:

- `postgresql.service`
- `fastapi-tutorial.service`

**Application dependencies**:

- Python packages listed in `/opt/fastapi-tutorial/requirements.txt`

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

Package names may require Debian-family and Red Hat-family mappings in Ansible if CentOS support is retained.

## Credentials

**Detection Summary**: One logical database credential was detected across one file, with three sensitive-value occurrences in `cookbooks/fastapi-tutorial/recipes/default.rb`.

**Source**:

- **Provider**: Hardcoded in Chef recipe
- **URL**: None
- **Path**: None
- **Source file**: `cookbooks/fastapi-tutorial/recipes/default.rb`

### PostgreSQL database password

- **Variable(s)**:
  - Password: `fastapi_password`
  - Database user: `fastapi`
  - Connection string: `DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the Chef recipe and written in plaintext to `/opt/fastapi-tutorial/.env`
- **Usage context**:
  - Creates the PostgreSQL role `fastapi`
  - Authenticates the FastAPI application to PostgreSQL
  - Supplies the `DATABASE_URL` connection string
- **Migration recommendation**:
  - Store the password in Ansible Vault or an approved AAP credential.
  - Use a variable such as `fastapi_db_password`.
  - Apply `no_log: true` to database credential tasks.
  - Construct `DATABASE_URL` from vaulted variables.
  - Do not print the environment file contents.
  - Consider changing `.env` mode from `0644` to `0600` as a security improvement, while noting that the Chef source specifies `0644`.

### Database connection string

- **Variable**: `DATABASE_URL`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
  - `/opt/fastapi-tutorial/.env`
- **Current storage**: Plaintext file containing an embedded PostgreSQL password
- **Usage context**: FastAPI database connection configuration
- **Migration recommendation**: Build the value from vaulted variables and protect the generated environment file.

## Checks for the Migration

**Files to verify**:

- `cookbooks/fastapi-tutorial/recipes/default.rb`
- `/opt/fastapi-tutorial/`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv/`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Database objects to verify**:

- PostgreSQL role `fastapi`
- PostgreSQL database `fastapi_db`
- Database owner `fastapi`
- `ALL` privileges on `fastapi_db` for `fastapi`

**Service endpoints to check**:

- `fastapi-tutorial`: TCP `0.0.0.0:8000`
- PostgreSQL: `localhost`
- PostgreSQL Unix socket: not explicitly configured

**Templates rendered**:

- 0 cookbook templates rendered
- `/opt/fastapi-tutorial/.env`: 1 inline-content file
- `/etc/systemd/system/fastapi-tutorial.service`: 1 inline-content file

## Pre-flight checks:

```bash
# Verify installed packages on Debian-family systems
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev 2>/dev/null

# Verify installed packages on Red Hat-family systems
rpm -q python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev 2>/dev/null

# Verify the fastapi-tutorial application directory
stat -c '%U:%G %a %n' /opt/fastapi-tutorial
test -d /opt/fastapi-tutorial

# Verify the fastapi-tutorial repository
git -C /opt/fastapi-tutorial status --short --branch
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
test "$(git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD)" = "main"

# Verify the fastapi-tutorial requirements file
test -f /opt/fastapi-tutorial/requirements.txt
ls -l /opt/fastapi-tutorial/requirements.txt

# Verify the fastapi-tutorial virtual environment
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip --version
/opt/fastapi-tutorial/venv/bin/pip check

# Verify PostgreSQL service
systemctl status postgresql --no-pager
systemctl is-enabled postgresql
systemctl is-active postgresql

# Verify the fastapi PostgreSQL role
sudo -u postgres psql -tAc "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"

# Verify the fastapi_db database and owner
sudo -u postgres psql -tAc "SELECT datname, pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"

# Verify fastapi database connectivity
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_database(), current_user;"

# Verify fastapi_db privileges
sudo -u postgres psql -d fastapi_db -c "\l+ fastapi_db"

# Verify the fastapi-tutorial environment file
stat -c '%U:%G %a %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' /opt/fastapi-tutorial/.env

# Verify the fastapi-tutorial systemd unit
systemctl cat fastapi-tutorial
grep -E '^(Description|After|Type|User|WorkingDirectory|Environment|ExecStart|Restart|WantedBy)=' \
  /etc/systemd/system/fastapi-tutorial.service
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl daemon-reload

# Verify the fastapi-tutorial service
systemctl status fastapi-tutorial --no-pager
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial

# Verify the fastapi-tutorial Uvicorn process
ps aux | grep '[u]vicorn'
pgrep -af 'uvicorn app.main:app'

# Verify the fastapi-tutorial listening port
ss -tlnp | grep ':8000'
netstat -tulpn 2>/dev/null | grep ':8000'
lsof -iTCP:8000 -sTCP:LISTEN

# Verify the fastapi-tutorial application endpoints
curl -i http://127.0.0.1:8000/
curl -i http://127.0.0.1:8000/docs

# Verify fastapi-tutorial and PostgreSQL logs
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u postgresql --no-pager -n 100

# Verify fastapi-tutorial dependency ordering
systemctl show fastapi-tutorial \
  --property=After \
  --property=Requires \
  --property=Wants
```

The root endpoint response depends on the application implementation in the Git repository. The port check must show a listener on `0.0.0.0:8000`, and `fastapi-tutorial.service` should report `active (running)`.