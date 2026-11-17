---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, and platform-specific PostgreSQL development packages; creates a Python virtual environment; installs application requirements; creates the PostgreSQL role `fastapi` and database `fastapi_db`; writes `/opt/fastapi-tutorial/.env`; and manages the `fastapi-tutorial.service` systemd unit listening on `0.0.0.0:8000`. The migration must preserve Fedora/RHEL and Debian/Ubuntu package differences, move the database password to Ansible Vault, and flush systemd handlers before starting the application service.

## Service Type and Instances

**Service Type**: Application server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application served by Uvicorn
  - Location/Path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Service user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Listening address: `0.0.0.0`
  - Port: `8000`
  - Restart policy: `Restart=always`
  - Startup dependency: `network.target` and `postgresql.service`

- **postgresql**: Application database service
  - Database: `fastapi_db`
  - Role: `fastapi`
  - Database owner: `fastapi`
  - Privileges: `ALL` on `fastapi_db`
  - Host: `localhost`
  - Port: Platform default PostgreSQL port, normally `5432`
  - Connection string: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`

The cookbook contains no collection attributes or `.each` loops. All configured values are scalar.

## File Structure

The cookbook contains one executed recipe and one attribute file. It has no providers, templates, or static files.

```text
cookbooks/fastapi-tutorial/
├── attributes/
│   └── default.rb
├── providers/
│   └── None
├── recipes/
│   └── default.rb
├── templates/
│   └── None
└── files/
    └── None
```

No `cookbook_file`, `remote_file`, or `.erb` template resources are used. The `.env` file and systemd unit are created directly with Chef `file` resources and should be implemented with `ansible.builtin.copy` or an equivalent file-management module.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Detects whether the platform family is Fedora/RHEL using `platform_family?('fedora', 'rhel')`.
   - On Fedora/RHEL, installs `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, and `libpq-devel`.
   - On Fedora/RHEL, runs `postgresql-setup --initdb` only when `/var/lib/pgsql/data/PG_VERSION` does not exist.
   - On Debian/Ubuntu-style platforms, installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Creates `/opt/fastapi-tutorial` with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` into `/opt/fastapi-tutorial` at revision `main`.
   - Creates `/opt/fastapi-tutorial/venv` with `python3 -m venv`, guarded by `creates: /opt/fastapi-tutorial/venv`.
   - Installs dependencies from `/opt/fastapi-tutorial/requirements.txt` using `/opt/fastapi-tutorial/venv/bin/pip`.
   - Enables and starts the `postgresql` service.
   - Creates PostgreSQL role `fastapi` with password supplied by the migration secret variable.
   - Creates database `fastapi_db` owned by `fastapi`.
   - Grants all privileges on `fastapi_db` to `fastapi`.
   - Creates `/opt/fastapi-tutorial/.env` with the application configuration and database connection string.
   - Creates `/etc/systemd/system/fastapi-tutorial.service`.
   - Reloads systemd after the unit file changes.
   - Enables and starts the `fastapi-tutorial` service.
   - The Ansible implementation must flush handlers after copying the unit file and before enabling or starting `fastapi-tutorial`, or explicitly perform `daemon-reload` at that point.
   - Iterations: None; there are no `.each` loops.

### Attribute values

Source file: `cookbooks/fastapi-tutorial/attributes/default.rb`

The supplied plan identifies these defaults:

| Chef attribute | Default value | Ansible equivalent |
|---|---|---|
| `node['fastapi_tutorial']['app_path']` | `/opt/fastapi-tutorial` | `fastapi_app_path` |
| `node['fastapi_tutorial']['repository']` | `https://github.com/dibanez/fastapi_tutorial.git` | `fastapi_repository` |
| `node['fastapi_tutorial']['revision']` | `main` | `fastapi_revision` |
| `node['fastapi_tutorial']['service_port']` | `8000` | `fastapi_service_port` |

The structured analysis explicitly exposes only `app_path`; the other three attribute defaults must be verified directly in `cookbooks/fastapi-tutorial/attributes/default.rb` before treating them as validated.

Recommended Ansible variables:

```yaml
fastapi_app_path: /opt/fastapi-tutorial
fastapi_repository: https://github.com/dibanez/fastapi_tutorial.git
fastapi_revision: main
fastapi_service_name: fastapi-tutorial
fastapi_service_port: 8000
fastapi_database_name: fastapi_db
fastapi_database_user: fastapi
fastapi_database_password: "{{ vault_fastapi_database_password }}"
```

## Dependencies

**External cookbook dependencies**: None identified.

**System package dependencies**:

- Fedora/RHEL:
  - `python3`
  - `python3-pip`
  - `git`
  - `postgresql-server`
  - `postgresql-contrib`
  - `libpq-devel`
- Debian/Ubuntu:
  - `python3`
  - `python3-pip`
  - `python3-venv`
  - `git`
  - `postgresql`
  - `postgresql-contrib`
  - `libpq-dev`

**Service dependencies**:

- `postgresql`
- `fastapi-tutorial`

**Ansible collection dependencies**:

- `community.postgresql` for PostgreSQL users, databases, and privileges.

## Credentials

**Detection Summary**: 1 database credential detected in `cookbooks/fastapi-tutorial/recipes/default.rb`; the same credential is also embedded in the generated `/opt/fastapi-tutorial/.env` content.

**Source**:

- **Provider**: Hardcoded in the Chef recipe
- **URL**: None
- **Path**: None; the value is used in a PostgreSQL connection string and role-creation command

### PostgreSQL Database Password

- **Variable(s)**:
  - Chef uses no credential attribute.
  - Literal value: `fastapi_password`
  - Connection string: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in the recipe and written to `.env`
- **Usage context**:
  - Creates PostgreSQL role `fastapi`
  - Authenticates the application to `fastapi_db`
  - Populates `DATABASE_URL` in `/opt/fastapi-tutorial/.env`
- **Migration handling**:
  - Store the value in Ansible Vault as `vault_fastapi_database_password`.
  - Expose it to tasks through `fastapi_database_password`.
  - Do not commit the literal password in role defaults, tasks, or templates.
  - Prefer mode `0600` for `/opt/fastapi-tutorial/.env`; the original Chef mode is `0644`.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, environment-variable secret references, TLS certificate references, API tokens, or external secret-manager URLs were detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/fastapi-tutorial/attributes/default.rb`
- `cookbooks/fastapi-tutorial/recipes/default.rb`
- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- Fedora/RHEL PostgreSQL data directory: `/var/lib/pgsql/data`
- Debian/Ubuntu distribution-managed PostgreSQL data directory
- PostgreSQL database: `fastapi_db`
- PostgreSQL role: `fastapi`

**Service endpoints to check**:

- `fastapi-tutorial`: TCP `0.0.0.0:8000`
- `postgresql`: `localhost:5432`, unless the platform default differs
- PostgreSQL platform-default local Unix socket

**Templates rendered**:

- None.
- `/opt/fastapi-tutorial/.env`: created once by a Chef `file` resource.
- `/etc/systemd/system/fastapi-tutorial.service`: created once by a Chef `file` resource.

## Pre-flight checks

```bash
# Verify both managed services individually
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql

systemctl status fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial

# Validate the PostgreSQL role and database individually
sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='fastapi';"
sudo -u postgres psql -tAc "SELECT datname FROM pg_database WHERE datname='fastapi_db';"
sudo -u postgres psql -tAc "SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname='fastapi_db';"

# Verify application database connectivity
PGPASSWORD="$FASTAPI_DATABASE_PASSWORD" psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_user, current_database();"

# Verify application files and virtual environment
ls -ld /opt/fastapi-tutorial
test -f /opt/fastapi-tutorial/requirements.txt
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn
/opt/fastapi-tutorial/venv/bin/pip check

# Verify the environment file without exposing its password
stat -c '%U:%G %a %n' /opt/fastapi-tutorial/.env
grep '^PROJECT_NAME=' /opt/fastapi-tutorial/.env
grep '^API_VERSION=' /opt/fastapi-tutorial/.env
sed -E 's#(postgresql://[^:]+:)[^@]+@#\1REDACTED@#' /opt/fastapi-tutorial/.env

# Verify the systemd unit and daemon configuration
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl cat fastapi-tutorial
grep '^After=' /etc/systemd/system/fastapi-tutorial.service
grep '^User=' /etc/systemd/system/fastapi-tutorial.service
grep '^WorkingDirectory=' /etc/systemd/system/fastapi-tutorial.service
grep '^ExecStart=' /etc/systemd/system/fastapi-tutorial.service
grep '^Restart=' /etc/systemd/system/fastapi-tutorial.service

# Verify the FastAPI endpoint and listening port
curl -I http://127.0.0.1:8000/
curl -sS http://127.0.0.1:8000/
ss -tlnp | grep ':8000'
pgrep -af 'uvicorn app.main:app'

# Review service logs and restart behavior
journalctl -u postgresql --no-pager -n 50
journalctl -u fastapi-tutorial --no-pager -n 100
systemctl show fastapi-tutorial --property=NRestarts
```

Expected results:

- `postgresql` is enabled and active.
- The `fastapi-tutorial` service is enabled and active.
- Role `fastapi` and database `fastapi_db` exist, with `fastapi` as the database owner.
- The application virtual environment contains Python, pip, and Uvicorn.
- The FastAPI service listens on `0.0.0.0:8000`.
- `/opt/fastapi-tutorial/.env` contains the expected project, API, and database settings without exposing the password in diagnostics.
- The systemd unit passes validation and uses `root`, `/opt/fastapi-tutorial`, the expected Uvicorn command, and `Restart=always`.
- PostgreSQL and FastAPI logs contain no startup, dependency, import, or database connection errors.
- `NRestarts` does not continually increase.