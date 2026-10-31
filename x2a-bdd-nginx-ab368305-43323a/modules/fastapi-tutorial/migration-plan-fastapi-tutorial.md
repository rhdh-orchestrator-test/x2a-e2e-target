---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the `main` branch of `https://github.com/dibanez/fastapi_tutorial.git` as a FastAPI application under `/opt/fastapi-tutorial`. It installs Python, virtual-environment, Git, PostgreSQL, PostgreSQL development packages, and application dependencies; creates the `fastapi` PostgreSQL role and `fastapi_db` database; writes the database connection string to `/opt/fastapi-tutorial/.env`; and manages the `fastapi-tutorial` systemd service running Uvicorn on `0.0.0.0:8000`. The cookbook manages one FastAPI application instance and one PostgreSQL database instance.

## Service Type and Instances

**Service Type**: Application Server with PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application served by Uvicorn
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Location/Path: `/opt/fastapi-tutorial`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Environment file: `/opt/fastapi-tutorial/.env`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Port/Socket: `0.0.0.0:8000`
  - Process command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Runtime user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Restart behavior: `Restart=always`
  - Startup dependency: `network.target` and `postgresql.service`
  - Service state: enabled and started

- **postgresql**: PostgreSQL database service
  - Database user: `fastapi`
  - Database password: `fastapi_password`
  - Database name: `fastapi_db`
  - Database owner: `fastapi`
  - Location/Path: PostgreSQL package-managed data and log locations
  - Port/Socket: PostgreSQL listener configured by the target operating system; the cookbook does not set a custom port or socket
  - Connection host: `localhost`
  - Connection string: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
  - Key Config: `ALL PRIVILEGES` on `fastapi_db` granted to `fastapi`
  - Service state: enabled and started

No collection attributes or `.each` iterations are present. No additional application, database, or service instances require expansion.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

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

No custom resources or provider files are used.

**Templates:**

```text
```

No ERB templates are rendered. The environment file and systemd unit are created with inline Chef `file` resources.

**Attributes:**

```text
```

No attribute files are shown or used.

**Files:**

```text
```

No static files are deployed with `cookbook_file` or `remote_file`.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the seven system packages `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Uses Debian/Ubuntu-style package names. CentOS/RHEL migration requires platform-specific package mapping.
   - No package versions are pinned.

2. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/opt/fastapi-tutorial` recursively.
   - Sets owner and group to `root:root` and mode to `0755`.

3. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` to `/opt/fastapi-tutorial`.
   - Checks out revision `main`.
   - Runs before dependency installation so `/opt/fastapi-tutorial/requirements.txt` is available.

4. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/opt/fastapi-tutorial/venv` with:
     ```bash
     python3 -m venv /opt/fastapi-tutorial/venv
     ```
   - Runs only when `/opt/fastapi-tutorial/venv` does not exist.

5. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs Python dependencies from `/opt/fastapi-tutorial/requirements.txt`.
   - Uses `/opt/fastapi-tutorial/venv/bin/pip`.
   - Runs with `/opt/fastapi-tutorial` as the working directory.
   - The Chef resource has no requirements-file checksum or change guard.

6. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Enables and starts the `postgresql` service before database operations.

7. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates PostgreSQL role `fastapi` with password `fastapi_password`.
   - Creates database `fastapi_db` owned by `fastapi`.
   - Grants `ALL PRIVILEGES` on `fastapi_db` to `fastapi`.
   - Executes database commands as the PostgreSQL administrative system user.
   - The original shell commands use `|| true`, suppressing errors for existing objects and unrelated SQL failures.
   - The migration should use idempotent PostgreSQL modules with `become_user: postgres`.

8. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/opt/fastapi-tutorial/.env`.
   - Sets owner and group to `root:root` and mode to `0644`.
   - Writes:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - The file contains a plaintext password; production migration should assess changing its mode to `0600`.

9. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/etc/systemd/system/fastapi-tutorial.service`.
   - Sets owner and group to `root:root` and mode to `0644`.
   - Deploys the following unit configuration:
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
   - Preserves the `root` service user, application working directory, virtual-environment path, Uvicorn target, bind address, port, restart policy, startup ordering, and enablement target.

10. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
    - Defines `systemd_reload` to run `systemctl daemon-reload`.
    - The action is `nothing` during normal convergence.
    - Runs immediately when `/etc/systemd/system/fastapi-tutorial.service` changes.

11. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
    - Enables and starts the `fastapi-tutorial` service.
    - Ensures the systemd daemon reload occurs before service startup when the unit is created or modified.

**Resource summary**:

- `package`: 1 resource installing 7 packages
- `directory`: 1 resource
- `git`: 1 resource
- `execute`: 4 resources: `create_venv`, `install_dependencies`, `create_db_user`, and `systemd_reload`
- `file`: 2 resources for `/opt/fastapi-tutorial/.env` and `/etc/systemd/system/fastapi-tutorial.service`
- `service`: 2 resources for `postgresql` and `fastapi-tutorial`
- Custom resources: none
- Included recipes: none
- Provider files: none
- Iterations: none
- Rendered ERB templates: none

## Dependencies

**External cookbook dependencies**: None listed in cookbook metadata.

**System package dependencies**:

- `python3`
- `python3-pip`
- `python3-venv`
- `git`
- `postgresql`
- `postgresql-contrib`
- `libpq-dev`

**Application source dependency**:

- Repository: `https://github.com/dibanez/fastapi_tutorial.git`
- Revision: `main`

**Service dependencies**:

- `postgresql`
- `fastapi-tutorial`
- `fastapi-tutorial.service` starts after `network.target` and `postgresql.service`

## Credentials

**Detection Summary**: 1 credential detected across 1 file.

**Source**:
  - **Provider**: Hardcoded
  - **URL**: None
  - **Path**: None

### PostgreSQL application password

- **Variable(s)**: `fastapi_password`; `DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the Chef recipe, embedded in the database creation command, and written in plaintext to `/opt/fastapi-tutorial/.env`
- **Usage context**:
  - Creates the PostgreSQL role `fastapi`
  - Authenticates the FastAPI application to `fastapi_db`
  - Provides the `DATABASE_URL` connection string
  - Is used by direct PostgreSQL connectivity checks

No Chef data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, HashiCorp Vault, AWS Secrets Manager, environment-variable secret lookups, TLS certificates, private keys, or API tokens were detected. The Ansible migration should move the password to Ansible Vault or another approved AAP secret mechanism.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- PostgreSQL package-managed data and log locations on the target operating system

**Service endpoints to check**:

- FastAPI HTTP endpoint: `0.0.0.0:8000`
- PostgreSQL host: `localhost`
- PostgreSQL port: active target installation port; no custom port is configured
- Unix socket: no explicit socket path is configured

**Templates rendered**:

- None; render count: `0`
- Inline configuration files created: `2`
  - `/opt/fastapi-tutorial/.env`
  - `/etc/systemd/system/fastapi-tutorial.service`

## Pre-flight checks

```bash
# Verify the FastAPI application instance directory and repository
ls -ld /opt/fastapi-tutorial
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
git -C /opt/fastapi-tutorial rev-parse HEAD
test -f /opt/fastapi-tutorial/requirements.txt
ls -l /opt/fastapi-tutorial/requirements.txt

# Verify the FastAPI virtual environment and dependencies
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip --version
/opt/fastapi-tutorial/venv/bin/pip list

# Verify the FastAPI environment file
stat -c '%a %U:%G %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' /opt/fastapi-tutorial/.env

# Verify the PostgreSQL instance
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
sudo -u postgres psql -tAc "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"
sudo -u postgres psql -tAc "SELECT datname, pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"
sudo -u postgres psql -d fastapi_db -c "\l+ fastapi_db"
sudo -u postgres psql -tAc "SHOW port;"
sudo -u postgres psql -tAc "SHOW listen_addresses;"
ss -tlnp | grep postgres

# Verify PostgreSQL connectivity for the fastapi database user
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_database(), current_user;"

# Verify the FastAPI systemd unit
systemctl cat fastapi-tutorial
grep -E '^(Description|After|Type|User|WorkingDirectory|Environment|ExecStart|Restart|WantedBy)=' \
  /etc/systemd/system/fastapi-tutorial.service
systemctl daemon-reload
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service

# Verify the FastAPI service instance
systemctl status fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
ps aux | grep '[u]vicorn app.main:app'
ss -tlnp | grep ':8000'
lsof -iTCP:8000 -sTCP:LISTEN

# Verify the FastAPI HTTP endpoint
curl -I http://127.0.0.1:8000/
curl -sS http://127.0.0.1:8000/

# Review service logs
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u postgresql --no-pager -n 100

# Verify FastAPI restart behavior
sudo systemctl restart fastapi-tutorial
systemctl is-active fastapi-tutorial
curl -I http://127.0.0.1:8000/
```

Expected validation results:

- The `postgresql` instance is enabled and active.
- PostgreSQL role `fastapi` exists.
- Database `fastapi_db` exists and is owned by `fastapi`.
- The `fastapi` role can connect to `fastapi_db` using the configured credentials.
- The `fastapi-tutorial` instance is enabled and active.
- Uvicorn listens on TCP port `8000`.
- `http://127.0.0.1:8000/` returns an application response.
- The systemd unit passes `systemd-analyze verify`.
- FastAPI and PostgreSQL logs contain no import, dependency, or database connection errors.