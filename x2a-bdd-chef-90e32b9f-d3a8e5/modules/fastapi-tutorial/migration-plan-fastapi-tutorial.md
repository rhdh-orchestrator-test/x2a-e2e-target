---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` under `/opt/fastapi-tutorial`. It installs Python, Git, PostgreSQL, and platform-specific PostgreSQL development packages; creates a Python virtual environment; installs the application requirements; enables PostgreSQL; creates the `fastapi` PostgreSQL role and `fastapi_db` database; writes an application environment file; and manages the `fastapi-tutorial` systemd service. The analyzed configuration targets `0.0.0.0:8000`, although the attribute defaults and inline file contents should be confirmed against the cookbook source before migration.

## Service Type and Instances

**Service Type**: Application server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application service
  - Application path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Runs as: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Startup command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Listening address: `0.0.0.0:8000` (configuration value to verify)
  - Restart policy: `always` (unit content to verify)
  - Dependency: `postgresql.service`

- **postgresql**: Local PostgreSQL database service
  - Service name: `postgresql`
  - Database role: `fastapi`
  - Database: `fastapi_db`
  - Database owner: `fastapi`
  - PostgreSQL endpoint: local host, normally port `5432`
  - Explicit port override: none identified
  - Initialization marker on Fedora/RHEL: `/var/lib/pgsql/data/PG_VERSION`

No collection iteration or `.each` loop is defined. The cookbook configures one application instance named **fastapi-tutorial** and one PostgreSQL service named **postgresql**.

## File Structure

The following are the only cookbook files shown as used by the execution analysis.

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

No ERB templates are rendered. Configuration files are created using inline `file` resources.

**Attributes:**
```text
cookbooks/fastapi-tutorial/attributes/default.rb
```

**Files:**
```text
```

No static files are deployed using `cookbook_file` or `remote_file`.

## Attributes

Source: `cookbooks/fastapi-tutorial/attributes/default.rb`

The following attributes are identified by the migration plan but require confirmation against the attributes analysis:

| Chef attribute | Reported default value | Ansible equivalent |
|---|---|---|
| `node['fastapi_tutorial']['app_path']` | `/opt/fastapi-tutorial` | `fastapi_tutorial_app_path` |
| `node['fastapi_tutorial']['repository']` | `https://github.com/dibanez/fastapi_tutorial.git` | `fastapi_tutorial_repository` |
| `node['fastapi_tutorial']['revision']` | `main` | `fastapi_tutorial_revision` |
| `node['fastapi_tutorial']['service_port']` | `8000` | `fastapi_tutorial_service_port` |

Use confirmed attribute values in Ansible role defaults or variables only after verifying `cookbooks/fastapi-tutorial/attributes/default.rb`. Reuse the application path, repository, revision, service port, and service name consistently in Git, command, copy, and systemd tasks.

## Module Explanation

The cookbook performs operations in this order:

1. **`default`** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Evaluates the Fedora/RHEL platform branch.
   - On Fedora/RHEL, installs `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, and `libpq-devel`.
   - On non-Fedora/RHEL platforms, installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - On Fedora/RHEL, runs `postgresql-setup --initdb` for `initialize_postgresql`; the reported guard is `/var/lib/pgsql/data/PG_VERSION`, subject to source verification.
   - Creates `/opt/fastapi-tutorial` recursively with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `/opt/fastapi-tutorial` from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main`.
   - Runs `python3 -m venv /opt/fastapi-tutorial/venv` for `create_venv`; the reported guard is `/opt/fastapi-tutorial/venv`, subject to source verification.
   - Runs `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt` from `/opt/fastapi-tutorial`.
   - Enables and starts the `postgresql` service.
   - Runs `create_db_user`, executing PostgreSQL commands as the `postgres` operating-system user to create:
     - Role `fastapi`
     - Database `fastapi_db`
     - Ownership of `fastapi_db` by `fastapi`
     - All privileges on `fastapi_db` for `fastapi`
   - Creates `/opt/fastapi-tutorial/.env` with the application configuration. The reported content, ownership, and mode require verification against the inline `file` resource.
   - Creates `/etc/systemd/system/fastapi-tutorial.service`. The reported unit binds Uvicorn to `0.0.0.0:8000`, runs as `root`, uses `/opt/fastapi-tutorial` as its working directory, sets the virtual-environment `PATH`, and uses `Restart=always`; these inline file details require verification.
   - Defines `systemd_reload`, which runs `systemctl daemon-reload` only when notified by a unit-file change.
   - Enables and starts the `fastapi-tutorial` service.
   - No `.each` loops or collection iterations are present.

The intended execution order is:

1. Package installation
2. PostgreSQL initialization on Fedora/RHEL
3. Application directory creation
4. Git synchronization
5. Virtual-environment creation
6. Python dependency installation
7. PostgreSQL service startup
8. PostgreSQL role and database creation
9. `.env` deployment
10. Systemd unit deployment
11. Systemd daemon reload
12. `fastapi-tutorial` service enablement and startup

## Dependencies

**External cookbook dependencies**: None listed in the analyzed metadata.

**System package dependencies**:

Fedora/RHEL:

- `python3`
- `python3-pip`
- `git`
- `postgresql-server`
- `postgresql-contrib`
- `libpq-devel`

Non-Fedora/RHEL:

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

**Application dependency source**:

- Git repository: `https://github.com/dibanez/fastapi_tutorial.git`
- Revision: `main`
- Requirements file: `/opt/fastapi-tutorial/requirements.txt`

## Credentials

**Detection Summary**: One hardcoded PostgreSQL credential is confirmed in the database-creation command. The original plan also reports the credential in the generated `.env` file, but that file content requires confirmation from the recipe source.

**Source**:
  - **Provider**: Hardcoded in the Chef recipe
  - **URL**: No external secret-management URL detected
  - **Path**: No data bag, vault path, CyberArk path, or secret-manager path detected

### PostgreSQL `fastapi` User Password

- **Variable(s)**:
  - No Chef attribute variable is used.
  - Confirmed literal password: `fastapi_password`
  - Reported connection string: `DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Confirmed hardcoded plaintext in the `create_db_user` command; presence in the generated `.env` requires verification
- **Usage context**:
  - Creates the PostgreSQL role `fastapi`
  - Authenticates the FastAPI application to the local database `fastapi_db`
  - Reportedly appears in `/opt/fastapi-tutorial/.env`

Store the password in Ansible Vault, for example as `fastapi_db_password`. Use it in the PostgreSQL user task and when rendering `/opt/fastapi-tutorial/.env`. Apply `no_log: true` to tasks that process the password.

No Chef data bags, encrypted data bags, Chef Vault calls, CyberArk integrations, Conjur variables, environment-variable lookups, TLS certificates, API keys, or additional secret namespaces were detected.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial/.env`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/etc/systemd/system/fastapi-tutorial.service`
- `/var/lib/pgsql/data/PG_VERSION` on Fedora/RHEL

**Application paths**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/venv`

**Database objects**:

- PostgreSQL role: `fastapi`
- PostgreSQL database: `fastapi_db`

**Service endpoints to check**:

- FastAPI instance `fastapi-tutorial`: `0.0.0.0:8000`
- PostgreSQL instance `postgresql`: local endpoint, normally port `5432`

**Unix sockets**:

- No socket path is explicitly configured.
- PostgreSQL may expose its platform-default local Unix socket.

**Templates rendered**:

- None; rendered count: `0`
- Inline file resources reported:
  - `/opt/fastapi-tutorial/.env`
  - `/etc/systemd/system/fastapi-tutorial.service`

## Pre-flight checks

```bash
# Confirm required packages and tools
python3 --version
python3 -m pip --version
git --version
psql --version

# On Fedora/RHEL, confirm PostgreSQL initialization
test -f /var/lib/pgsql/data/PG_VERSION && echo "PostgreSQL initialized"
```

### PostgreSQL instance checks

```bash
# Verify the PostgreSQL instance is enabled and active
systemctl is-enabled postgresql
systemctl is-active postgresql
systemctl status postgresql --no-pager

# Verify the PostgreSQL role
sudo -u postgres psql -tAc \
  "SELECT 1 FROM pg_roles WHERE rolname='fastapi';"

# Verify the database
sudo -u postgres psql -tAc \
  "SELECT 1 FROM pg_database WHERE datname='fastapi_db';"

# Verify database ownership
sudo -u postgres psql -tAc \
  "SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname='fastapi_db';"

# Verify the local PostgreSQL port
ss -tlnp | grep ':5432' || true
```

Use a protected environment variable or another secure authentication method for credential-based connection tests. Do not place the password directly in production command history.

### FastAPI instance checks

```bash
# Verify the application directory
ls -ld /opt/fastapi-tutorial

# Verify the Git checkout
git -C /opt/fastapi-tutorial status --short
git -C /opt/fastapi-tutorial branch --show-current
git -C /opt/fastapi-tutorial rev-parse HEAD

# Verify the requirements file
test -f /opt/fastapi-tutorial/requirements.txt

# Verify the virtual environment
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip

# Verify installed Python packages
/opt/fastapi-tutorial/venv/bin/pip list

# Verify the environment file without exposing its password
stat -c '%U:%G %a %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION)=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env | \
  sed -E 's#(postgresql://[^:]+:)[^@]+(@.*)#\1********\2#'

# Verify the FastAPI systemd unit
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl status fastapi-tutorial --no-pager

# Verify resolved service properties
systemctl show fastapi-tutorial | \
  grep -E 'User=|WorkingDirectory=|ExecStart=|Restart=|SubState='

# Verify the FastAPI instance is listening on port 8000
ss -tlnp | grep ':8000'
ps aux | grep '[u]vicorn'

# Test the application root endpoint
curl --fail --silent --show-error \
  -o /dev/null \
  -w 'HTTP status: %{http_code}\n' \
  http://127.0.0.1:8000/
```

The cookbook does not define a `/health` endpoint. Validate the application root or an endpoint confirmed to exist in the checked-out repository.

### Database connectivity checks for `fastapi-tutorial`

```bash
# Use a protected PGPASSWORD value or equivalent secure authentication
PGPASSWORD="${FASTAPI_DB_PASSWORD}" \
psql -h localhost -U fastapi -d fastapi_db -c "SELECT 1;"
```

### Service ordering and logs

```bash
# Confirm the FastAPI unit references PostgreSQL
grep -E '^After=' /etc/systemd/system/fastapi-tutorial.service

# Confirm the application command and port
grep -E '^(WorkingDirectory|Environment|ExecStart)=' \
  /etc/systemd/system/fastapi-tutorial.service

# Confirm both named service instances are active
systemctl is-active postgresql
systemctl is-active fastapi-tutorial

# Review logs for the PostgreSQL instance
journalctl -u postgresql --no-pager -n 100

# Review logs for the fastapi-tutorial instance
journalctl -u fastapi-tutorial --no-pager -n 100

# Check for recent application errors
journalctl -u fastapi-tutorial --since "15 minutes ago" --no-pager | \
  grep -Ei 'error|exception|traceback'
```

Expected results:

- `postgresql` is enabled and active.
- The `fastapi` role and `fastapi_db` database exist.
- `fastapi-tutorial` is enabled and active.
- The FastAPI process listens on port `8000`.
- The application uses `/opt/fastapi-tutorial/venv/bin/uvicorn`.
- The application can connect to `fastapi_db` using the `fastapi` PostgreSQL role.
