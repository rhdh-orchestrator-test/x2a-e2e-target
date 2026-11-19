---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the `fastapi-tutorial` FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` under `/opt/fastapi-tutorial`. It installs platform-specific Python, Git, PostgreSQL, and development packages, creates a Python virtual environment, installs application requirements, provisions the PostgreSQL user `fastapi` and database `fastapi_db`, writes an environment file containing the database connection string, and manages the application with the `fastapi-tutorial` systemd service. The application runs as `root`, listens on `0.0.0.0:8000`, and depends on the `postgresql` service. The cookbook supports RHEL/Fedora and Debian/Ubuntu package layouts.

## Service Type and Instances

**Service Type**: Application Server with PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application service
  - Application path: `/opt/fastapi-tutorial`
  - Git repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Git revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Service user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Listen address: `0.0.0.0`
  - Listen port: `8000`
  - Application command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Restart policy: `Restart=always`
  - Dependency: `postgresql.service`

- **postgresql**: PostgreSQL database service
  - Service name: `postgresql`
  - Database user: `fastapi`
  - Database password: `fastapi_password`
  - Database: `fastapi_db`
  - Database owner: `fastapi`
  - Database privileges: `ALL` on `fastapi_db`
  - Expected local endpoint: TCP port `5432` and/or the distribution PostgreSQL Unix socket

**Iterations**: None. The cookbook configures one FastAPI service and one PostgreSQL database/user pair. No collection attributes or `.each` loops are defined.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**
```text
cookbooks/fastapi-tutorial/recipes/default.rb
```

**Providers:**
```text
```

No custom Chef providers are used.

**Templates:**
```text
```

No ERB templates are used. The `.env` file and systemd unit are written directly by Chef `file` resources.

**Attributes:**
```text
cookbooks/fastapi-tutorial/attributes/default.rb
```

**Files:**
```text
```

No static files are deployed by `cookbook_file` or `remote_file`.

## Attributes

The execution analysis directly confirms use of `node['fastapi_tutorial']['app_path']`. The following values and references are documented in the original plan but were not independently confirmed by the supplied structured analysis and must be verified against `cookbooks/fastapi-tutorial/attributes/default.rb`:

| Chef attribute | Documented default value | Intended Ansible use | Validation status |
|---|---|---|---|
| `node['fastapi_tutorial']['app_path']` | `/opt/fastapi-tutorial` | Application checkout and working directory | Used by the execution tree |
| `node['fastapi_tutorial']['repository']` | `https://github.com/dibanez/fastapi_tutorial.git` | Git repository URL | Verify in attributes/recipe |
| `node['fastapi_tutorial']['revision']` | `main` | Git branch or revision | Verify in attributes/recipe |
| `node['fastapi_tutorial']['service_port']` | `8000` | Uvicorn listen port and systemd command | Verify in attributes/recipe |

Suggested Ansible variables:

```yaml
fastapi_app_path: /opt/fastapi-tutorial
fastapi_repository: https://github.com/dibanez/fastapi_tutorial.git
fastapi_revision: main
fastapi_service_port: 8000
```

No iterable dictionary or collection attribute requires item expansion.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs platform-specific system packages.
   - On RHEL/Fedora systems, installs `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, and `libpq-devel`.
   - On RHEL/Fedora systems, runs `postgresql-setup --initdb` through `execute[initialize_postgresql]` when `/var/lib/pgsql/data/PG_VERSION` does not exist.
   - On Debian/Ubuntu systems, installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Creates `/opt/fastapi-tutorial` as `root:root` with mode `0755` and recursive creation enabled.
   - Checks out `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates `/opt/fastapi-tutorial/venv` with `python3 -m venv` when the virtual-environment path does not exist.
   - Installs dependencies from `/opt/fastapi-tutorial/requirements.txt` using `/opt/fastapi-tutorial/venv/bin/pip`.
   - Enables and starts the `postgresql` service.
   - Creates PostgreSQL role `fastapi` with password `fastapi_password`.
   - Creates database `fastapi_db` owned by `fastapi`.
   - Grants `ALL` privileges on `fastapi_db` to `fastapi`.
   - Writes `/opt/fastapi-tutorial/.env` with owner `root`, group `root`, mode `0644`, and the following content:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Writes `/etc/systemd/system/fastapi-tutorial.service` with owner `root`, group `root`, and mode `0644`.
   - Configures the systemd unit to run as `root`, use `/opt/fastapi-tutorial` as its working directory, place `/opt/fastapi-tutorial/venv/bin` first in `PATH`, bind Uvicorn to `0.0.0.0:8000`, restart automatically, and start after `network.target` and `postgresql.service`.
   - Runs `systemctl daemon-reload` through `execute[systemd_reload]` immediately when the systemd unit changes.
   - Enables and starts the `fastapi-tutorial` service.
   - Iterations: none; the recipe contains no `.each` loops.

**Resource summary for `cookbooks/fastapi-tutorial/recipes/default.rb`:**

- `package`: 2 conditional resources
- `execute`: 5 resources:
  - `initialize_postgresql`
  - `create_venv`
  - `install_dependencies`
  - `create_db_user`
  - `systemd_reload`
- `directory`: 1 resource
- `git`: 1 resource
- `service`: 2 resources:
  - `postgresql`
  - `fastapi-tutorial`
- `file`: 2 resources:
  - `/opt/fastapi-tutorial/.env`
  - `/etc/systemd/system/fastapi-tutorial.service`
- `group`: 0 resources

## Dependencies

**External cookbook dependencies**: None declared in the provided metadata.

**System package dependencies**:

RHEL/Fedora:

```text
python3
python3-pip
git
postgresql-server
postgresql-contrib
libpq-devel
```

Debian/Ubuntu:

```text
python3
python3-pip
python3-venv
git
postgresql
postgresql-contrib
libpq-dev
```

**Application dependency source**:

```text
/opt/fastapi-tutorial/requirements.txt
```

Dependencies are installed into:

```text
/opt/fastapi-tutorial/venv
```

**Service dependencies**:

- `postgresql`
- `fastapi-tutorial`

The FastAPI systemd unit declares:

```ini
After=network.target postgresql.service
```

## Credentials

**Detection Summary**: 2 sensitive references detected in `cookbooks/fastapi-tutorial/recipes/default.rb`: the hardcoded PostgreSQL password and the same password embedded in the database connection URL.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None
- **Path**: None

### PostgreSQL user password

- **Variable(s)**: No Chef attribute variable is used; the literal value is `fastapi_password`.
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`, line 49
  - `cookbooks/fastapi-tutorial/recipes/default.rb`, line 61
- **Current storage**: Hardcoded in the recipe and written to a plaintext `.env` file.
- **Usage context**:
  ```sql
  CREATE USER fastapi WITH PASSWORD 'fastapi_password';
  ```
  The value is also embedded in `DATABASE_URL`.

The Ansible migration must store this value in Ansible Vault or an approved external secret provider. It must not be exposed in task output.

### Database connection string

- **Variable(s)**: `DATABASE_URL`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`, lines 57–62
- **Current storage**: Plaintext file generated by a Chef `file` resource.
- **Usage context**: FastAPI connection to the local PostgreSQL database `fastapi_db`.
- **Value pattern**:
  ```text
  postgresql://fastapi:<password>@localhost/fastapi_db
  ```

The migrated `.env` file should use restrictive permissions, preferably `0600`, rather than retaining the Chef-specified `0644` mode.

No Chef data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable lookups, TLS certificates, private keys, API keys, or external secret-manager URLs were detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/app/main.py`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- RHEL/Fedora PostgreSQL data directory: `/var/lib/pgsql/data/`
- Debian/Ubuntu distribution-managed PostgreSQL data directory

**Database objects to verify**:

- PostgreSQL role `fastapi`
- PostgreSQL database `fastapi_db`
- Database owner `fastapi`
- `ALL` privileges on `fastapi_db` for `fastapi`

**Service endpoints to check**:

- `fastapi-tutorial`: TCP `0.0.0.0:8000`
- `postgresql`: local TCP port `5432` and/or the distribution PostgreSQL Unix socket

**Templates rendered**:

No templates are rendered. Two inline Chef `file` resources create configuration files, each rendered once:

- `/opt/fastapi-tutorial/.env`: 1 render
- `/etc/systemd/system/fastapi-tutorial.service`: 1 render

## Pre-flight checks

```bash
# Identify the operating system
cat /etc/os-release

# Verify Python
python3 --version
python3 -m pip --version

# Verify Git
git --version

# Verify PostgreSQL client
psql --version
```

### RHEL/Fedora package and PostgreSQL checks

```bash
rpm -q python3 python3-pip git postgresql-server postgresql-contrib libpq-devel
ls -l /var/lib/pgsql/data/PG_VERSION
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
```

### Debian/Ubuntu package and PostgreSQL checks

```bash
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
```

### FastAPI instance checks

```bash
# Verify the application checkout
git -C /opt/fastapi-tutorial status
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
git -C /opt/fastapi-tutorial rev-parse HEAD

# Verify application files
ls -ld /opt/fastapi-tutorial
ls -l /opt/fastapi-tutorial/requirements.txt
ls -l /opt/fastapi-tutorial/app/main.py

# Verify the virtual environment
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip list

# Verify the environment file
ls -l /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' /opt/fastapi-tutorial/.env

# Verify the systemd unit
systemctl cat fastapi-tutorial
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
grep -E '^(User|WorkingDirectory|Environment|ExecStart|Restart)=' \
  /etc/systemd/system/fastapi-tutorial.service

# Verify the FastAPI service
systemctl status fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
ss -tlnp | grep ':8000'
curl -i http://127.0.0.1:8000/
curl -i http://127.0.0.1:8000/openapi.json
curl -i http://localhost:8000/

# Verify FastAPI logs and restart behavior
journalctl -u fastapi-tutorial --no-pager -n 100
sudo systemctl restart fastapi-tutorial
systemctl is-active fastapi-tutorial
curl -i http://127.0.0.1:8000/
```

Expected FastAPI unit values:

```text
User=root
WorkingDirectory=/opt/fastapi-tutorial
Environment="PATH=/opt/fastapi-tutorial/venv/bin"
ExecStart=/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
```

### PostgreSQL instance checks

```bash
# Verify the PostgreSQL service
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql

# Verify the fastapi role
sudo -u postgres psql -tAc \
  "SELECT usename FROM pg_catalog.pg_user WHERE usename = 'fastapi';"

# Verify database name and owner
sudo -u postgres psql -tAc \
  "SELECT datname, pg_catalog.pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"

# Verify application credentials and connectivity
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT version();"

PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT 1;"

# Verify database privileges
sudo -u postgres psql -tAc \
  "SELECT datacl FROM pg_database WHERE datname = 'fastapi_db';"

# Review PostgreSQL logs
journalctl -u postgresql --no-pager -n 100
```

Expected database results:

```text
fastapi
fastapi_db|fastapi
```

### Ownership and permissions checks

```bash
stat -c '%A %U:%G %n' /opt/fastapi-tutorial
stat -c '%A %U:%G %n' /opt/fastapi-tutorial/.env
stat -c '%A %U:%G %n' /etc/systemd/system/fastapi-tutorial.service
ls -ld /opt/fastapi-tutorial/venv
```

Chef-specified ownership and modes:

```text
/opt/fastapi-tutorial                         root:root, mode 0755
/opt/fastapi-tutorial/.env                    root:root, mode 0644
/etc/systemd/system/fastapi-tutorial.service  root:root, mode 0644
```

The migrated `.env` should preferably use `root:root` and mode `0600` because it contains a database password.