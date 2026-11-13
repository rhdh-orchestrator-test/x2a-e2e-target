---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys one FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` under `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, and required development libraries; creates a Python virtual environment; installs application dependencies; initializes and starts PostgreSQL; creates the `fastapi` user and `fastapi_db` database; writes the application environment file; and manages a systemd service listening on port `8000`.

## Service Type and Instances

**Service Type**: Application Server backed by a PostgreSQL database

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application server
  - Application path: `/opt/fastapi-tutorial`
  - Source repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Git revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Service user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Start command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Listen address: `0.0.0.0`
  - Listen port: `8000`
  - Restart policy: `always`

- **postgresql**: Local PostgreSQL database service
  - Service name: `postgresql`
  - Database user: `fastapi`
  - Database: `fastapi_db`
  - Database owner: `fastapi`
  - Host: `localhost`
  - Expected default port: `5432`

## File Structure

```text
cookbooks/fastapi-tutorial/
├── recipes/
│   └── default.rb
├── providers/
│   └── None
├── templates/
│   └── None
├── attributes/
│   └── None
└── files/
    └── None
```

**Recipes:**
```text
recipes/default.rb
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

The cookbook creates files dynamically with Chef `file` resources. No static files from a `files/` directory or ERB templates are used.

## Module Explanation

The cookbook performs operations in this order. The cookbook contains no `.each` loops and configures one application instance, `fastapi-tutorial`, and one database service, `postgresql`.

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Evaluates `platform_family?('fedora', 'rhel')`.
   - On RHEL/Fedora systems, installs `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, and `libpq-devel`.
   - On RHEL/Fedora systems, runs `postgresql-setup --initdb` through `execute[initialize_postgresql]`, guarded by `/var/lib/pgsql/data/PG_VERSION`.
   - On non-RHEL systems, installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Creates `/opt/fastapi-tutorial` as `root:root` with mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates `/opt/fastapi-tutorial/venv` by running `python3 -m venv /opt/fastapi-tutorial/venv`, guarded by the virtual-environment directory.
   - Installs dependencies with `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt` from `/opt/fastapi-tutorial`.
   - Enables and starts `service[postgresql]`.
   - Runs `execute[create_db_user]` as the operating-system `postgres` user:
     - Creates PostgreSQL user `fastapi` with password `fastapi_password`.
     - Creates database `fastapi_db` owned by `fastapi`.
     - Grants `ALL` privileges on `fastapi_db` to `fastapi`.
     - Each SQL command ends with `|| true`, suppressing failures and making the implementation non-strictly idempotent.
   - Creates `/opt/fastapi-tutorial/.env` as `root:root` with mode `0644`, containing:
     - `PROJECT_NAME="FastAPI Tutorial"`
     - `API_VERSION=1.0.0`
     - `DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db`
   - Creates `/etc/systemd/system/fastapi-tutorial.service` as `root:root` with mode `0644`.
   - Configures the systemd unit to:
     - Start after `network.target` and `postgresql.service`.
     - Run as `root`.
     - Use `/opt/fastapi-tutorial` as its working directory.
     - Set `PATH=/opt/fastapi-tutorial/venv/bin`.
     - Run `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`.
     - Restart always.
     - Start under `multi-user.target`.
   - Notifies `execute[systemd_reload]` immediately when the systemd unit changes.
   - Runs `systemctl daemon-reload` through `execute[systemd_reload]`, whose default action is `nothing` and which executes only when notified.
   - Enables and starts `service[fastapi-tutorial]`.

## Dependencies

**External cookbook dependencies**: None listed in the available metadata.

**System package dependencies**:

- RHEL/Fedora:
  - `python3`
  - `python3-pip`
  - `git`
  - `postgresql-server`
  - `postgresql-contrib`
  - `libpq-devel`
- Non-RHEL:
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

**Execution dependency chain**:

1. Install platform-specific packages.
2. Initialize PostgreSQL on RHEL/Fedora when `/var/lib/pgsql/data/PG_VERSION` is absent.
3. Create `/opt/fastapi-tutorial`.
4. Synchronize the Git repository.
5. Create the Python virtual environment.
6. Install Python dependencies.
7. Enable and start `postgresql`.
8. Create the `fastapi` PostgreSQL user and `fastapi_db` database.
9. Write `/opt/fastapi-tutorial/.env`.
10. Write `/etc/systemd/system/fastapi-tutorial.service`.
11. Reload systemd when the unit changes.
12. Enable and start `fastapi-tutorial`.

## Credentials

**Detection Summary**: 2 sensitive references detected in `cookbooks/fastapi-tutorial/recipes/default.rb`.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None
- **Path**: None
- **Vault or secret-manager integration**: None detected
- **Data bags**: None detected
- **Chef Vault**: None detected
- **CyberArk/Conjur**: None detected
- **Environment-based secret lookup**: None detected

### PostgreSQL password in database creation command

- **Variable(s)**: No variable; literal password `fastapi_password`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in an `execute` resource
- **Usage context**: Sets the password for PostgreSQL user `fastapi`

The value appears in:

```bash
CREATE USER fastapi WITH PASSWORD 'fastapi_password';
```

Migration requirements:

- Replace the literal with an Ansible Vault variable such as `fastapi_db_password`.
- Execute password-bearing tasks with `no_log: true`.
- Create the user with `community.postgresql.postgresql_user`.
- Execute database tasks as the PostgreSQL administrative operating-system user, normally `postgres`.

### PostgreSQL password embedded in `DATABASE_URL`

- **Variable(s)**: `DATABASE_URL`; embedded password `fastapi_password`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the generated `.env` file
- **Usage context**: Application database connection string

The generated value is:

```text
DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
```

Migration requirements:

- Generate the URL from vaulted variables.
- Ensure the password is URL-encoded if it contains URL-reserved characters.
- Protect the resulting `.env` file.
- Prefer mode `0600` instead of the Chef mode `0644`.
- Use `no_log: true` for tasks that may expose the password.

No TLS certificate, private key, API token, SSH private key, or other credential reference was detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/.env`
- `/opt/fastapi-tutorial/venv`
- `/etc/systemd/system/fastapi-tutorial.service`
- `/var/lib/pgsql/data/PG_VERSION` on RHEL/Fedora systems
- Platform-managed PostgreSQL data directory on non-RHEL systems

**Service endpoints to check**:

- `fastapi-tutorial`: `0.0.0.0:8000`
- `postgresql`: `localhost:5432`

**Unix sockets**: No socket path is explicitly configured. PostgreSQL may expose its platform-default local Unix socket.

**Templates rendered**: None. No ERB templates are used.

**Generated files**:

- `/opt/fastapi-tutorial/.env`: one managed Chef `file` resource
- `/etc/systemd/system/fastapi-tutorial.service`: one managed Chef `file` resource

## Pre-flight checks

### Package and runtime checks

```bash
python3 --version
python3 -m pip --version
git --version
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip --version
```

On Debian-family systems:

```bash
dpkg -l | grep -E 'postgresql|postgresql-contrib|libpq-dev'
```

On RHEL/Fedora systems:

```bash
rpm -qa | grep -E 'postgresql|libpq-devel'
```

### `fastapi-tutorial` application checks

```bash
test -d /opt/fastapi-tutorial
test -f /opt/fastapi-tutorial/requirements.txt
test -d /opt/fastapi-tutorial/venv
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
git -C /opt/fastapi-tutorial log -1 --oneline
```

The repository should resolve to the requested `main` revision.

Verify the application service:

```bash
systemctl status fastapi-tutorial --no-pager
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl cat fastapi-tutorial
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
ps aux | grep '[u]vicorn app.main:app'
ss -ltnp | grep ':8000'
curl -i http://127.0.0.1:8000/
```

Expected command configuration:

```text
ExecStart=/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
```

If the checked-out application provides a health endpoint, test it with:

```bash
curl -i http://127.0.0.1:8000/health
```

The cookbook itself does not define a health endpoint.

Verify the environment file without printing its password:

```bash
ls -l /opt/fastapi-tutorial/.env
grep '^PROJECT_NAME=' /opt/fastapi-tutorial/.env
grep '^API_VERSION=' /opt/fastapi-tutorial/.env
sed 's#://[^:]*:[^@]*@#://***:***@#' /opt/fastapi-tutorial/.env
```

Expected non-secret structure:

```text
DATABASE_URL=postgresql://***:***@localhost/fastapi_db
```

### `postgresql` database checks

```bash
systemctl status postgresql --no-pager
systemctl is-enabled postgresql
systemctl is-active postgresql
ss -ltnp | grep ':5432'
```

On RHEL/Fedora systems:

```bash
test -f /var/lib/pgsql/data/PG_VERSION
```

Verify the `fastapi` role:

```bash
sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname = 'fastapi';"
```

Expected result:

```text
1
```

Verify the `fastapi_db` database:

```bash
sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname = 'fastapi_db';"
```

Expected result:

```text
1
```

Verify database ownership:

```bash
sudo -u postgres psql -tAc "SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"
```

Expected result:

```text
fastapi
```

Verify application credentials and basic access:

```bash
PGPASSWORD='<vaulted-fastapi-password>' \
psql -h localhost -U fastapi -d fastapi_db -c "SELECT version();"

PGPASSWORD='<vaulted-fastapi-password>' \
psql -h localhost -U fastapi -d fastapi_db -c "SELECT 1;"
```

### Logs, restart, and ownership checks

```bash
journalctl -u postgresql --no-pager -n 50
journalctl -u fastapi-tutorial --no-pager -n 100
systemctl show fastapi-tutorial --property=Restart
sleep 5
systemctl is-active fastapi-tutorial
```

Expected restart policy:

```text
Restart=always
```

Verify ownership and modes:

```bash
stat -c '%U:%G %a %n' /opt/fastapi-tutorial
stat -c '%U:%G %a %n' /opt/fastapi-tutorial/.env
stat -c '%U:%G %a %n' /etc/systemd/system/fastapi-tutorial.service
```

For a direct Chef-equivalent migration, the application directory and generated files are `root:root`. For the improved Ansible implementation, restrict `.env` to mode `0600` because it contains the database password.