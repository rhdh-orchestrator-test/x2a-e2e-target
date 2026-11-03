---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys one FastAPI tutorial application backed by PostgreSQL on Ubuntu or CentOS. It installs Python, PostgreSQL, Git, and PostgreSQL development packages; clones the application from GitHub; creates a Python virtual environment; installs application dependencies; creates the `fastapi` PostgreSQL role and `fastapi_db` database; writes an environment file containing the database connection string; and manages the application with a systemd service listening on port `8000`. The PostgreSQL password is hardcoded in the Chef recipe and must be externalized in Ansible.

## Service Type and Instances

**Service Type**: Application Server with PostgreSQL database dependency

**Supported platforms**:

- Ubuntu `>= 18.04`
- CentOS `>= 7.0`

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application served by Uvicorn through systemd
  - Application path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Git revision: `main`
  - Python virtual environment: `/opt/fastapi-tutorial/venv`
  - Application module: `app.main:app`
  - Process executable: `/opt/fastapi-tutorial/venv/bin/uvicorn`
  - Bind address: `0.0.0.0`
  - Port: `8000`
  - Running user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Restart policy: `always`
  - Environment file: `/opt/fastapi-tutorial/.env`
  - systemd unit: `/etc/systemd/system/fastapi-tutorial.service`

**Configured PostgreSQL objects**:

- **fastapi**: PostgreSQL application role
  - Password: `fastapi_password`
  - Database owner: `fastapi_db`
- **fastapi_db**: PostgreSQL application database
  - Owner: `fastapi`
  - Host: `localhost`
  - Default port: `5432`
  - Connection URL: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`

## File Structure

```text
Recipes:
cookbooks/fastapi-tutorial/recipes/default.rb

Providers:
None

Templates:
None

Attributes:
None

Files:
None
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Uses one Chef `package` resource declaration containing seven packages.
   - On Ubuntu, these package names can generally be passed directly to `ansible.builtin.apt`.
   - On CentOS, verify the equivalent PostgreSQL development package because `libpq-dev` may have a different name.
   - No package versions are pinned.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial` using the Chef `git` resource.
   - Creates the virtual environment with:
     ```bash
     python3 -m venv /opt/fastapi-tutorial/venv
     ```
   - Uses a `creates` guard so virtual-environment creation is skipped when `/opt/fastapi-tutorial/venv` already exists.
   - Installs Python dependencies with:
     ```bash
     /opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt
     ```
   - Runs the dependency installation from `/opt/fastapi-tutorial` after the repository and virtual environment exist.
   - Enables and starts the `postgresql` service.
   - Executes PostgreSQL commands as the operating-system user `postgres` to create the `fastapi` role, create the `fastapi_db` database owned by `fastapi`, and grant all privileges on `fastapi_db` to `fastapi`.
   - The PostgreSQL shell commands use `|| true`, tolerating already-existing objects; the Ansible migration should instead use idempotent PostgreSQL modules.
   - Writes `/opt/fastapi-tutorial/.env` as a root-owned, mode `0644` inline file containing:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Deploys `/etc/systemd/system/fastapi-tutorial.service` as a root-owned, mode `0644` inline file with:
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
   - Immediately notifies `execute[systemd_reload]` when `/etc/systemd/system/fastapi-tutorial.service` changes.
   - Runs `systemctl daemon-reload` through `execute[systemd_reload]`, whose normal action is `nothing`.
   - Enables and starts the `fastapi-tutorial` systemd service.
   - There are no `.each` loops or collection-based iterations to expand.

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

**Service dependencies**:

- `postgresql.service`
- `fastapi-tutorial.service`

**Application dependency order**:

1. Install system packages.
2. Create `/opt/fastapi-tutorial`.
3. Synchronize the Git repository.
4. Create `/opt/fastapi-tutorial/venv`.
5. Install `/opt/fastapi-tutorial/requirements.txt`.
6. Enable and start PostgreSQL.
7. Create the `fastapi` PostgreSQL role and `fastapi_db` database.
8. Write `/opt/fastapi-tutorial/.env`.
9. Write the FastAPI systemd unit.
10. Reload systemd when the unit changes.
11. Enable and start `fastapi-tutorial.service`.

## Credentials

**Detection Summary**: 1 database credential detected in 1 recipe file.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None
- **Path**: None
- **Storage**: Inline PostgreSQL command and generated `.env` file

### PostgreSQL application password

- **Variable(s)**: No symbolic Chef attribute is used; the literal password is `fastapi_password`.
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded
- **Usage context**:
  - Used in the PostgreSQL `CREATE USER` command.
  - Embedded in `DATABASE_URL` in `/opt/fastapi-tutorial/.env`.
  - Used by the FastAPI application to connect to PostgreSQL.
- **Database user**: `fastapi`
- **Database**: `fastapi_db`
- **Host**: `localhost`

The Ansible implementation must store the password in Ansible Vault or another approved secret-management system. It must not be placed in a publicly readable task file. The generated `.env` file should use mode `0600` rather than the Chef-configured `0644`, unless broader access is required by the application.

No data bags, encrypted data bags, Chef Vault items, CyberArk integrations, Conjur variables, HashiCorp Vault references, AWS Secrets Manager references, TLS certificate references, API keys, or environment-variable-based external secrets were detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**PostgreSQL objects to verify**:

- `postgresql` service
- `fastapi` PostgreSQL role
- `fastapi_db` database
- `fastapi_db` ownership by `fastapi`
- Privileges granted to `fastapi`

**Service endpoints to check**:

- `fastapi-tutorial`: TCP `0.0.0.0:8000`
- PostgreSQL: `localhost:5432`, unless the target installation uses another port

**Templates rendered**:

- None; render count: `0`
- `.env` is created by an inline Chef `file` resource.
- The systemd unit is created by an inline Chef `file` resource.

## Pre-flight checks

### Package and filesystem checks

```bash
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev 2>/dev/null || \
rpm -q python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

test -d /opt/fastapi-tutorial
stat -c '%A %U:%G %n' /opt/fastapi-tutorial

test -d /opt/fastapi-tutorial/venv
test -f /opt/fastapi-tutorial/requirements.txt
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
```

### `fastapi-tutorial` repository checks

```bash
cd /opt/fastapi-tutorial
git remote -v
git branch --show-current
git rev-parse --verify HEAD
test -f /opt/fastapi-tutorial/app/main.py
test -f /opt/fastapi-tutorial/requirements.txt
```

Expected repository:

```text
https://github.com/dibanez/fastapi_tutorial.git
```

Expected revision:

```text
main
```

### PostgreSQL checks

```bash
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
```

Verify the `fastapi` role:

```bash
sudo -u postgres psql -tAc \
  "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"
```

Expected output:

```text
fastapi
```

Verify `fastapi_db` ownership:

```bash
sudo -u postgres psql -tAc \
  "SELECT datname, pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"
```

Expected output:

```text
fastapi_db | fastapi
```

Verify application connectivity:

```bash
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_database(), current_user;"
```

Expected values:

```text
current_database | fastapi_db
current_user     | fastapi
```

Verify the PostgreSQL listener:

```bash
ss -tlnp | grep ':5432'
```

### Environment file checks

```bash
stat -c '%A %U:%G %n' /opt/fastapi-tutorial/.env
grep '^PROJECT_NAME=' /opt/fastapi-tutorial/.env
grep '^API_VERSION=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env
```

Expected non-secret values:

```text
PROJECT_NAME="FastAPI Tutorial"
API_VERSION=1.0.0
```

Do not print the complete `.env` file to shared logs because it contains the PostgreSQL password. Verify that the migrated file uses mode `0600` where possible.

### `fastapi-tutorial` systemd unit checks

```bash
systemctl cat fastapi-tutorial
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
```

Verify the unit settings:

```bash
grep '^After=' /etc/systemd/system/fastapi-tutorial.service
grep '^User=' /etc/systemd/system/fastapi-tutorial.service
grep '^WorkingDirectory=' /etc/systemd/system/fastapi-tutorial.service
grep '^Environment=' /etc/systemd/system/fastapi-tutorial.service
grep '^ExecStart=' /etc/systemd/system/fastapi-tutorial.service
grep '^Restart=' /etc/systemd/system/fastapi-tutorial.service
```

Expected command:

```text
ExecStart=/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Expected restart policy:

```text
Restart=always
```

### `fastapi-tutorial` application endpoint checks

```bash
systemctl status fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
ps aux | grep '[u]vicorn'
```

Check the HTTP endpoint:

```bash
curl -I http://127.0.0.1:8000/
curl -sS http://127.0.0.1:8000/
```

The service must accept connections on port `8000`. The exact HTTP status for `/` depends on the checked-out application implementation.

Verify the listener:

```bash
ss -tlnp | grep ':8000'
lsof -iTCP:8000 -sTCP:LISTEN
```

Expected listener:

```text
0.0.0.0:8000
```

### Application logs and restart behavior

```bash
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u fastapi-tutorial -f
systemctl show fastapi-tutorial | grep '^Restart='
```

After changing the systemd unit through Ansible, verify that the playbook performs a systemd daemon reload and restarts the `fastapi-tutorial` service when required by the change.