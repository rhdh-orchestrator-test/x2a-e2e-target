---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys a FastAPI tutorial application from a Git repository into `/opt/fastapi-tutorial`, installs Python, Git, PostgreSQL, and PostgreSQL development dependencies, creates a Python virtual environment, installs application requirements, provisions the PostgreSQL role `fastapi` and database `fastapi_db`, writes an application `.env` file and systemd unit, and enables and starts PostgreSQL and the `fastapi-tutorial` service. The application port is not specified in the analyzed execution tree and must be obtained from the deployed systemd unit or application configuration.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application service
  - Location/Path: `/opt/fastapi-tutorial`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Requirements file: `/opt/fastapi-tutorial/requirements.txt`
  - Environment file: `/opt/fastapi-tutorial/.env`
  - systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Port/Socket: Not specified in the analyzed execution tree
  - Key Config: Service is enabled and started; application port, listen address, `ExecStart`, user, working directory, and environment settings must be taken from the actual unit or application configuration.

- **postgresql**: PostgreSQL database service
  - Location/Path: System PostgreSQL installation
  - Port/Socket: Not explicitly configured by the cookbook; verify the active listener on the deployed system
  - Key Config: Service is enabled and started; role `fastapi` and database `fastapi_db` are provisioned, with `fastapi` as the database owner.

## File Structure

```text
Recipes:
  recipes/default.rb

Providers:

Templates:

Attributes:

Files:
```

The `.env` file and systemd unit are created dynamically by inline Chef `file` resources. They are not cookbook static files or templates in the supplied analysis.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the operating-system packages `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Creates `/opt/fastapi-tutorial` with mode `0755`.
   - Synchronizes the application Git checkout into `/opt/fastapi-tutorial`.
   - Creates the virtual environment with:
     ```bash
     python3 -m venv /opt/fastapi-tutorial/venv
     ```
   - Installs Python dependencies from `/opt/fastapi-tutorial/requirements.txt` into `/opt/fastapi-tutorial/venv`.
   - Enables and starts the `postgresql` service.
   - Attempts to create PostgreSQL role `fastapi` with password `fastapi_password`.
   - Attempts to create database `fastapi_db` owned by `fastapi`.
   - Attempts to grant all privileges on `fastapi_db` to `fastapi`.
   - Writes `/opt/fastapi-tutorial/.env` with mode `0644`; the exact inline contents were not included in the analysis and must be obtained from the recipe.
   - Writes `/etc/systemd/system/fastapi-tutorial.service` with mode `0644`; the exact inline unit contents were not included in the analysis.
   - Declares `systemctl daemon-reload` through `execute[systemd_reload]` with action `nothing`; the execution tree does not show a notification relationship.
   - Enables and starts the `fastapi-tutorial` service.
   - No `.each` loops or collection-based iterations were present, so there are no additional instances to expand.
   - No `group['root']` resource was identified; ownership must not be prescribed beyond what is explicitly present in the source recipe or confirmed on the target system.

## Dependencies

**External cookbook dependencies**: None shown in the supplied metadata or execution tree.

**System package dependencies**:

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

**Execution dependency order**:

1. Install system packages.
2. Create `/opt/fastapi-tutorial`.
3. Synchronize the Git checkout.
4. Create `/opt/fastapi-tutorial/venv`.
5. Install Python requirements.
6. Enable and start `postgresql`.
7. Create the PostgreSQL role and database.
8. Write `/opt/fastapi-tutorial/.env`.
9. Write `/etc/systemd/system/fastapi-tutorial.service`.
10. Reload systemd after unit changes and before starting or restarting the application service.
11. Enable and start `fastapi-tutorial`.

## Credentials

**Detection Summary**: 1 explicit hardcoded credential detected in 1 database provisioning command. The inline `.env` content was not available, so it may contain additional credentials that require inspection.

**Source**:

- **Provider**: Hardcoded in the Chef command; no Vault, CyberArk, AWS Secrets Manager, data bag, or encrypted data bag integration was shown.
- **URL**: None detected.
- **Path**: None detected.
- **Target storage**: Store secrets in Ansible Vault.

### PostgreSQL Password

- **Variable(s)**: No Chef variable name is shown; literal value is `fastapi_password`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded plaintext in `execute[create_db_user]`
- **Usage context**: Sets the password for PostgreSQL role `fastapi`
- **Target storage**: An Ansible Vault variable such as `fastapi_db_password`
- **Handling**: Use `no_log: true` for tasks that may expose the password and do not place it directly in task files.

### Potential Credentials in `.env`

- **Variable(s)**: Not available in the supplied execution tree
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`, inline content for `/opt/fastapi-tutorial/.env`
- **Current storage**: Inline Chef file content; exact values are unavailable
- **Usage context**: Application environment configuration, potentially including database connection settings
- **Migration action**: Inspect the actual `.env` content and move passwords, tokens, API keys, and connection strings into Ansible Vault
- **File permissions**: Review the source mode `0644`; use `0600` if the file contains secrets

No Chef data bags, encrypted data bags, Chef Vault calls, external secret-provider integrations, TLS certificate references, or static key files were shown.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Database objects to verify**:

- PostgreSQL role: `fastapi`
- PostgreSQL database: `fastapi_db`
- Database owner: `fastapi`
- Role password authentication

**Service endpoints to check**:

- `fastapi-tutorial`: Application port and health endpoint are not specified; inspect the deployed unit and application configuration before adding an endpoint check.
- `postgresql`: Port is not explicitly configured; verify the active PostgreSQL listener and Unix socket on the deployed system.

**Templates rendered**: None; no templates were shown or rendered.

**Static files deployed**: None shown. The Git resource synchronizes the application repository, but no cookbook static file deployment was listed.

## Pre-flight checks

```bash
# Confirm required packages for fastapi-tutorial and postgresql
dpkg-query -W python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

# Verify the fastapi-tutorial application directory
ls -ld /opt/fastapi-tutorial
test -f /opt/fastapi-tutorial/requirements.txt

# Verify the fastapi-tutorial virtual environment
ls -ld /opt/fastapi-tutorial/venv
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip

# Verify the fastapi-tutorial environment file
ls -l /opt/fastapi-tutorial/.env
stat /opt/fastapi-tutorial/.env

# Verify the fastapi-tutorial systemd unit
ls -l /etc/systemd/system/fastapi-tutorial.service
stat /etc/systemd/system/fastapi-tutorial.service
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
```

### PostgreSQL instance

```bash
# Confirm the postgresql service is running and enabled
systemctl status postgresql --no-pager
systemctl is-enabled postgresql
systemctl is-active postgresql

# Verify the fastapi role exists
sudo -u postgres psql -tAc \
  "SELECT 1 FROM pg_roles WHERE rolname='fastapi';"

# Verify the fastapi_db database exists
sudo -u postgres psql -tAc \
  "SELECT 1 FROM pg_database WHERE datname='fastapi_db';"

# Verify database ownership
sudo -u postgres psql -tAc \
  "SELECT datname, pg_get_userbyid(datdba)
   FROM pg_database
   WHERE datname='fastapi_db';"

# Verify privileges for the fastapi role
sudo -u postgres psql -d fastapi_db -tAc \
  "SELECT has_database_privilege('fastapi', 'fastapi_db', 'CONNECT');"

# Verify PostgreSQL listeners and sockets
ss -ltnp | grep postgres || true
ss -lx | grep postgres || true

# Verify application-role connectivity using a protected credential method.
# Do not place the password directly on the command line in production.
psql -h localhost -U fastapi -d fastapi_db \
  -c "SELECT current_user, current_database();"
```

### fastapi-tutorial instance

```bash
# Reload systemd metadata after deploying or changing the unit
sudo systemctl daemon-reload

# Confirm the fastapi-tutorial service is running and enabled
systemctl status fastapi-tutorial --no-pager
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial

# Inspect the effective unit configuration
systemctl cat fastapi-tutorial

# Inspect recent application logs
journalctl -u fastapi-tutorial --no-pager -n 100

# Inspect service process state
systemctl show fastapi-tutorial \
  --property=MainPID,ActiveState,SubState,ExecMainStartTimestamp

# Verify the virtual environment Python executable
/opt/fastapi-tutorial/venv/bin/python --version

# Verify installed Python packages
/opt/fastapi-tutorial/venv/bin/pip list
```

After inspecting the deployed systemd unit, add a health check using the actual configured port and endpoint:

```bash
curl -I http://127.0.0.1:<configured-port>/<configured-health-endpoint>
```

Do not invent an application port or health endpoint.

### Configuration and security checks

```bash
# Confirm the application checkout and requirements file
git -C /opt/fastapi-tutorial status --short
test -f /opt/fastapi-tutorial/requirements.txt

# Confirm systemd unit syntax
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service

# Review configuration metadata without exposing secret values
stat /opt/fastapi-tutorial/.env
stat /etc/systemd/system/fastapi-tutorial.service

# Review the active PostgreSQL listener rather than assuming a port
ss -ltnp | grep postgres || true
```

When inspecting `.env`, verify variable names and value presence without printing secret values in CI logs or Ansible output.