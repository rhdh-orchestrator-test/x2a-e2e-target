---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: `fastapi-tutorial` deploys the FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` under `/opt/fastapi-tutorial`, creates a Python virtual environment, installs `requirements.txt`, configures PostgreSQL with the `fastapi` role and `fastapi_db` database, writes the application environment file, and runs Uvicorn through the `fastapi-tutorial` systemd service on TCP port `8000`. The Ansible migration must preserve the effective database password through an Ansible Vault variable and create a non-empty `ansible/Makefile` whose default `all` target invokes `ansible-playbook`.

## Service Type and Instances

**Service Type**: Application Server with PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application server
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Location/Path: `/opt/fastapi-tutorial`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Runtime user/group: `root:root`
  - Working directory: `/opt/fastapi-tutorial`
  - Startup command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Port/Socket: `8000/tcp`
  - Restart behavior: `Restart=always`
  - Environment file: `/opt/fastapi-tutorial/.env`

- **postgresql**: Local PostgreSQL database service
  - Service name: `postgresql`
  - Port/Socket: `5432/tcp`
  - State: enabled and started
  - Database user: `fastapi`
  - Database password: `fastapi_password`
  - Database: `fastapi_db`
  - Database owner: `fastapi`
  - Database host: `localhost`

No `.each` loops or collection iterations are present. The cookbook configures exactly one FastAPI application instance and one PostgreSQL database configuration.

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

The `.env` file and systemd unit are created directly with Chef `file` resources and are not sourced from cookbook templates or static files.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Selects a platform-specific package list.
   - On Fedora/RHEL, installs `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, and `libpq-devel`.
   - On non-Fedora/RHEL systems, installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - On Fedora/RHEL, runs `postgresql-setup --initdb` only when `/var/lib/pgsql/data/PG_VERSION` does not exist.
   - Creates `/opt/fastapi-tutorial` as `root:root` with mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates `/opt/fastapi-tutorial/venv` with `python3 -m venv /opt/fastapi-tutorial/venv`.
   - Installs dependencies with `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt` from `/opt/fastapi-tutorial`.
   - Enables and starts the `postgresql` service.
   - Creates the PostgreSQL role `fastapi` with password `fastapi_password`.
   - Creates the `fastapi_db` database owned by `fastapi`.
   - Ensures `fastapi` has all privileges on `fastapi_db`.
   - Writes `/opt/fastapi-tutorial/.env` with:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Creates `/etc/systemd/system/fastapi-tutorial.service` with:
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
   - Sets the systemd unit owner and group to `root:root` with mode `0644`.
   - Reloads systemd when `/etc/systemd/system/fastapi-tutorial.service` changes.
   - Enables and starts the `fastapi-tutorial` service.
   - Ansible implementation should use `ansible.builtin.package`, `ansible.builtin.command`, `ansible.builtin.file`, `ansible.builtin.git`, `ansible.builtin.service` or `ansible.builtin.systemd_service`, and `ansible.builtin.copy` or `ansible.builtin.template`.
   - PostgreSQL administration should use `community.postgresql.postgresql_user`, `community.postgresql.postgresql_db`, and `community.postgresql.postgresql_privs` when applicable, executing administrative tasks as `postgres`.
   - The Fedora/RHEL initialization command must use `creates: /var/lib/pgsql/data/PG_VERSION`.
   - Systemd reload must be implemented as a handler with `daemon_reload: true`, notified only when the unit changes.
   - Iterations: none.

The Ansible execution order is:

1. Select the operating-system-specific package list.
2. Install system packages.
3. Initialize PostgreSQL on Fedora/RHEL when required.
4. Create `/opt/fastapi-tutorial`.
5. Synchronize the Git repository.
6. Create the virtual environment.
7. Install Python dependencies.
8. Enable and start `postgresql`.
9. Create the `fastapi` PostgreSQL role.
10. Create `fastapi_db` owned by `fastapi`.
11. Grant privileges on `fastapi_db`.
12. Write `/opt/fastapi-tutorial/.env`.
13. Write `/etc/systemd/system/fastapi-tutorial.service`.
14. Reload systemd when the unit changes.
15. Enable and start `fastapi-tutorial`.

### Ansible Makefile

The migration must create `ansible/Makefile`. It must be non-empty, define `all` as the default target, and invoke `ansible-playbook`.

```makefile
.PHONY: all

all:
	ansible-playbook -i inventory site.yml
```

## Dependencies

**External cookbook dependencies**: None listed in `metadata.rb`.

**System package dependencies**:

- Fedora/RHEL:
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

**Application dependencies**:

- Git repository: `https://github.com/dibanez/fastapi_tutorial.git`
- Git revision: `main`
- Python dependency file: `/opt/fastapi-tutorial/requirements.txt`

**Service dependencies**:

- `postgresql`
- `network.target`
- `postgresql.service`

**Ansible collection dependencies**:

- `community.postgresql` is recommended for PostgreSQL role, database, and privilege management.

## Credentials

**Detection Summary**: 1 credential detected in 1 source file. The credential is hardcoded and reused in the database creation command and connection string.

**Source**:
- **Provider**: Hardcoded in Chef recipe; migrate to Ansible Vault
- **URL**: None
- **Path**: None

### PostgreSQL Database Password

- **Variable(s)**: `fastapi_password` in Chef; use vaulted `fastapi_db_password` in Ansible
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded literal
- **Value in Chef**: `fastapi_password`
- **Usage context**:
  - Creates the PostgreSQL role:
    ```sql
    CREATE USER fastapi WITH PASSWORD 'fastapi_password';
    ```
  - Appears in:
    ```text
    postgresql://fastapi:fastapi_password@localhost/fastapi_db
    ```
  - Is rendered into `/opt/fastapi-tutorial/.env`
- **Migration storage**: Store the effective value in an encrypted Ansible Vault variable and use it for both PostgreSQL role creation and `DATABASE_URL` rendering.

No data bags, encrypted data bags, Chef Vault calls, CyberArk integration, Conjur integration, environment-variable secret lookups, TLS certificates, private keys, API tokens, or external secret-manager URLs were detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/fastapi-tutorial/recipes/default.rb`
- `ansible/Makefile`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- Fedora/RHEL PostgreSQL data directory: `/var/lib/pgsql/data`
- Distribution-specific PostgreSQL data directory on non-Fedora/RHEL systems

**Service endpoints to check**:

- `postgresql`: `localhost:5432`
- `fastapi-tutorial`: `0.0.0.0:8000`

**Templates rendered**:

- No Chef templates are used.
- `/opt/fastapi-tutorial/.env`: generated directly from inline Chef file content, rendered once.
- `/etc/systemd/system/fastapi-tutorial.service`: generated directly from inline Chef file content, rendered once.

**Configuration checks**:

- `/opt/fastapi-tutorial/.env` contains `PROJECT_NAME`, `API_VERSION`, and `DATABASE_URL`.
- The database URL targets `fastapi_db` on `localhost` with user `fastapi`.
- `/etc/systemd/system/fastapi-tutorial.service` contains the required ordering, runtime user, working directory, virtual-environment PATH, Uvicorn command, port, restart policy, and `multi-user.target`.
- The `fastapi-tutorial` process listens on TCP port `8000`.
- PostgreSQL accepts connections on port `5432`.
- `ansible/Makefile` is non-empty and its default `all` target invokes `ansible-playbook`.

## Pre-flight checks

### `fastapi-tutorial` application instance

```bash
test -d /opt/fastapi-tutorial
test -f /opt/fastapi-tutorial/requirements.txt
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn

git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
git -C /opt/fastapi-tutorial rev-parse HEAD

/opt/fastapi-tutorial/venv/bin/pip list
/opt/fastapi-tutorial/venv/bin/python -c "import fastapi; print(fastapi.__version__)"

stat -c '%U:%G %a %n' /opt/fastapi-tutorial/.env
grep '^PROJECT_NAME=' /opt/fastapi-tutorial/.env
grep '^API_VERSION=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env

systemctl daemon-reload
systemctl cat fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl status fastapi-tutorial
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service

ss -tlnp | grep ':8000'
ps aux | grep '[u]vicorn'
curl -i http://127.0.0.1:8000/
```

Expected application settings include:

- Owner and group: `root:root`
- Environment file mode: `0644`
- Working directory: `/opt/fastapi-tutorial`
- Uvicorn executable: `/opt/fastapi-tutorial/venv/bin/uvicorn`
- Bind address and port: `0.0.0.0:8000`
- Restart policy: `always`

If the checked-out application provides `/health`, validate it with:

```bash
curl -i http://127.0.0.1:8000/health
```

Do not print the complete `.env` file in shared CI logs.

### `postgresql` database instance

```bash
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql

sudo -u postgres psql -tAc "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"
sudo -u postgres psql -tAc "SELECT datname, pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"
sudo -u postgres psql -h localhost -d fastapi_db -c "SELECT 1;"
ss -tlnp | grep ':5432'
```

Expected values:

```text
fastapi
fastapi_db | fastapi
```

Verify authenticated application credentials without exposing the password:

```bash
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env | sed 's/:fastapi_password@/:REDACTED@/'

PGPASSWORD='fastapi_password' \
psql -h localhost -U fastapi -d fastapi_db -c "SELECT current_database(), current_user;"
```

Expected values:

```text
current_database | fastapi_db
current_user     | fastapi
```

### Operating system and package checks

```bash
cat /etc/os-release
python3 --version
python3 -m pip --version
git --version
psql --version
```

On Fedora/RHEL:

```bash
rpm -q python3 python3-pip git postgresql-server postgresql-contrib libpq-devel
test -f /var/lib/pgsql/data/PG_VERSION
```

On Debian/Ubuntu-compatible systems:

```bash
dpkg -s python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev
```

### Ansible migration checks

```bash
test -s ansible/Makefile
make -C ansible -n all
grep -E '^[[:space:]]*ansible-playbook' ansible/Makefile
```

### Logs and restart behavior

```bash
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u postgresql --no-pager -n 100
journalctl -u fastapi-tutorial --no-pager | grep -E 'ERROR|Traceback|failed|Failed'

sudo systemctl restart fastapi-tutorial
sleep 2
systemctl is-active fastapi-tutorial
ss -tlnp | grep ':8000'
```

The `fastapi-tutorial` service must return to the active state and listen on port `8000` after restart.