---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys a FastAPI application from a Git repository under `/opt/fastapi-tutorial`, installs Python, Git, PostgreSQL, and PostgreSQL development packages, creates a Python virtual environment, installs `requirements.txt`, provisions the PostgreSQL user `fastapi` and database `fastapi_db`, writes an application `.env` file and a systemd unit, and enables and starts PostgreSQL and `fastapi-tutorial`. The cookbook contains one entry recipe and no iterable instance collections. The repository details, generated file contents, application port, and several file ownership and permission values require verification from the original recipe.

## Service Type and Instances

**Service Type**: Application Server backed by a PostgreSQL database

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application service
  - Application location: `/opt/fastapi-tutorial`
  - Python virtual environment: `/opt/fastapi-tutorial/venv`
  - Dependency file: `/opt/fastapi-tutorial/requirements.txt`
  - Environment file: `/opt/fastapi-tutorial/.env`
  - systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Service actions: enabled and started
  - Listening port: not specified in the supplied execution tree
  - Network binding: not specified in the supplied execution tree
  - Directory mode and ownership: require verification from the original recipe
  - Environment file mode and ownership: require verification from the original recipe
  - systemd unit mode and ownership: require verification from the original recipe

- **postgresql**: PostgreSQL database service
  - Service name: `postgresql`
  - Service actions: enabled and started
  - Database user: `fastapi`
  - Database name: `fastapi_db`
  - Database owner: `fastapi`
  - Privileges: `fastapi` receives all privileges on `fastapi_db`
  - Port: not explicitly configured; verify the target PostgreSQL configuration, including whether the default port `5432` is used

There are no `.each` loops, collection attributes, or multiple application instances shown in the execution tree.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

**Recipes:**
```text
recipes/default.rb
```

**Providers:**
```text
```

**Templates:**
```text
```

**Attributes:**
```text
```

**Files:**
```text
```

No provider, template, attribute, or static file is listed as used. The `.env` file and systemd unit are generated inline by Chef `file` resources rather than rendered from cookbook templates.

## Module Explanation

The cookbook performs operations in the following exact order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the following seven system packages:
     - `python3`
     - `python3-pip`
     - `python3-venv`
     - `git`
     - `postgresql`
     - `postgresql-contrib`
     - `libpq-dev`
   - Resource: one `package` resource containing seven packages.
   - No package version constraints are specified.
   - Creates the application directory `/opt/fastapi-tutorial`.
   - Resource: one `directory` resource.
   - The directory mode and ownership are not confirmed by the supplied analysis and must be verified from the original recipe.
   - Synchronizes a Git checkout into `/opt/fastapi-tutorial`.
   - Resource: one `git` resource.
   - The repository URL, branch, revision, and checkout user are not provided in the execution tree and must be obtained from the original recipe.
   - Runs `python3 -m venv /opt/fastapi-tutorial/venv`.
   - Resource: `execute[create_venv]`.
   - The Ansible implementation should create the virtual environment only when `/opt/fastapi-tutorial/venv/bin/python` does not already exist.
   - Installs Python dependencies with `/opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt`.
   - Resource: `execute[install_dependencies]`.
   - The Ansible implementation should use `ansible.builtin.pip` with `/opt/fastapi-tutorial/venv/bin/pip` and `/opt/fastapi-tutorial/requirements.txt`.
   - Enables and starts the PostgreSQL service.
   - Resource: one `service` resource for `postgresql`.
   - Creates the PostgreSQL user and database using `execute[create_db_user]`:
     - Creates user `fastapi`.
     - Sets its password to `fastapi_password`.
     - Creates database `fastapi_db` owned by `fastapi`.
     - Grants all privileges on `fastapi_db` to `fastapi`.
   - The original command block suppresses errors with `|| true`; the Ansible implementation should instead use idempotent PostgreSQL modules:
     - `community.postgresql.postgresql_user`
     - `community.postgresql.postgresql_db`
     - `community.postgresql.postgresql_privs`, if an explicit privilege task is required
   - Database initialization runs after PostgreSQL has started.
   - Writes `/opt/fastapi-tutorial/.env`.
   - Resource: one `file` resource.
   - The inline content, variables, mode, owner, and group are not supplied and must be obtained from the original recipe. Do not infer additional environment variables.
   - Writes `/etc/systemd/system/fastapi-tutorial.service`.
   - Resource: one `file` resource.
   - The inline systemd unit content, mode, owner, group, `ExecStart`, working directory, user, environment handling, restart policy, and network port are not supplied and must be obtained from the original recipe.
   - Defines `execute[systemd_reload]` with command `systemctl daemon-reload` and action `nothing`.
   - Resource: one `execute` resource.
   - The supplied execution tree does not show a notification relationship, so the reload command is not confirmed to execute.
   - Enables and starts the `fastapi-tutorial` service.
   - Resource: one `service` resource for `fastapi-tutorial`.
   - If the systemd unit changes, the Ansible implementation should reload systemd and restart or reload the service according to the behavior specified by the original unit.

**Iterations**: None. No `.each` loops or iterable instance collections are present.

## Dependencies

**External cookbook dependencies**: None listed in the supplied structured analysis.

**System package dependencies**:

- `python3`
- `python3-pip`
- `python3-venv`
- `git`
- `postgresql`
- `postgresql-contrib`
- `libpq-dev`

**Service dependencies**:

- `postgresql`: enabled and started before database initialization
- `fastapi-tutorial`: enabled and started after application files, Python dependencies, database setup, and the systemd unit are in place

**Execution dependency chain**:

```text
system packages
  → /opt/fastapi-tutorial
  → Git checkout
  → Python virtual environment
  → Python dependencies
  → PostgreSQL started
  → PostgreSQL user/database setup
  → /opt/fastapi-tutorial/.env
  → /etc/systemd/system/fastapi-tutorial.service
  → systemd daemon reload
  → fastapi-tutorial enabled and started
```

## Credentials

**Detection Summary**: 1 hardcoded database credential detected in `cookbooks/fastapi-tutorial/recipes/default.rb`.

**Source**:
  - **Provider**: Hardcoded
  - **URL**: None detected
  - **Path**: None detected

### PostgreSQL password for the `fastapi` database user

- **Variable(s)**: No Chef attribute variable is used; the literal password is embedded directly in the command as `PASSWORD 'fastapi_password'`.
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded inline in `execute[create_db_user]`
- **Usage context**: Password for PostgreSQL user `fastapi`, which owns database `fastapi_db`
- **Migration handling**:
  - Store the password in Ansible Vault.
  - Pass it to `community.postgresql.postgresql_user` using a vaulted variable.
  - Do not place the literal password in a non-encrypted vars file or command line.
  - Confirm whether `/opt/fastapi-tutorial/.env` also contains a database connection string; its exact content is not included in the supplied execution tree.

No `data_bag_item`, `encrypted_data_bag_item`, Chef Vault, CyberArk, Conjur, AWS Secrets Manager, Vault URL, certificate path, key path, or environment-variable secret reference is shown in the supplied analysis.

## Checks for the Migration

**Files to verify**:

- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`
- `/opt/fastapi-tutorial/venv/bin/python`
- `/opt/fastapi-tutorial/venv/bin/pip`

**Directories to verify**:

- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/venv`

**Database objects to verify**:

- PostgreSQL role: `fastapi`
- PostgreSQL database: `fastapi_db`
- Database owner: `fastapi`
- All privileges granted to `fastapi` on `fastapi_db`

**Service endpoints to check**:

- FastAPI application port: not specified in the supplied execution tree
- PostgreSQL port: not explicitly configured; verify the target configuration, including whether it listens on `5432`
- Unix sockets: not specified

**Templates rendered**:

- None
- `.env`: zero template renders; created by an inline Chef `file` resource
- `/etc/systemd/system/fastapi-tutorial.service`: zero template renders; created by an inline Chef `file` resource

## Pre-flight checks

### Package and directory checks

```bash
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev
test -d /opt/fastapi-tutorial
stat -c '%A %U %G %n' /opt/fastapi-tutorial
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -f /opt/fastapi-tutorial/requirements.txt
```

For RPM-based systems:

```bash
rpm -q python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev
```

Verify the directory mode and ownership against the original Chef recipe because the supplied analysis does not confirm them.

### Git checkout checks

```bash
git -C /opt/fastapi-tutorial status
git -C /opt/fastapi-tutorial rev-parse --show-toplevel
ls -la /opt/fastapi-tutorial
```

Verify the repository URL, branch, revision, and checkout user against the original Chef recipe.

### Python environment and dependency checks

```bash
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip --version
/opt/fastapi-tutorial/venv/bin/pip check
/opt/fastapi-tutorial/venv/bin/pip freeze
```

### PostgreSQL instance checks

```bash
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
```

Verify the configured PostgreSQL listener:

```bash
ss -tlnp | grep ':5432'
```

Use the actual configured PostgreSQL port if it differs from `5432`.

### PostgreSQL user and database checks

```bash
sudo -u postgres psql -tAc "SELECT rolname FROM pg_roles WHERE rolname = 'fastapi';"
sudo -u postgres psql -tAc "SELECT datname FROM pg_database WHERE datname = 'fastapi_db';"
sudo -u postgres psql -tAc "SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"
```

Expected results:

- The role query returns `fastapi`.
- The database query returns `fastapi_db`.
- The owner query returns `fastapi`.

Test database connectivity using the vaulted password without retaining it in shell history:

```bash
PGPASSWORD='use-the-vaulted-fastapi-password' \
psql -h localhost -U fastapi -d fastapi_db -c "SELECT version();"

PGPASSWORD='use-the-vaulted-fastapi-password' \
psql -h localhost -U fastapi -d fastapi_db -c "SELECT current_user, current_database();"
```

### FastAPI application instance checks

Verify the application files and configuration:

```bash
test -d /opt/fastapi-tutorial
test -f /opt/fastapi-tutorial/requirements.txt
test -f /opt/fastapi-tutorial/.env
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
```

Inspect configuration without exposing secrets:

```bash
stat -c '%A %U %G %n' /opt/fastapi-tutorial/.env
sed -E 's/(PASSWORD|SECRET|TOKEN|KEY)=.*/\1=<redacted>/' /opt/fastapi-tutorial/.env
```

Verify the environment file mode and ownership against the original Chef recipe because they are not confirmed by the supplied analysis.

Verify the systemd unit:

```bash
test -f /etc/systemd/system/fastapi-tutorial.service
stat -c '%A %U %G %n' /etc/systemd/system/fastapi-tutorial.service
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
systemctl daemon-reload
```

Verify the systemd unit mode and ownership against the original Chef recipe because they are not confirmed by the supplied analysis.

Check the application service:

```bash
systemctl status fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl show fastapi-tutorial --property=ExecStart,User,WorkingDirectory,EnvironmentFile
```

Check recent service logs:

```bash
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u fastapi-tutorial -p err --no-pager
```

The application port and health endpoint are not specified in the supplied execution tree. After inspecting the systemd unit or application configuration, test the configured endpoint:

```bash
curl -i http://127.0.0.1:<configured-port>/
curl -i http://127.0.0.1:<configured-port>/docs
```

Replace `<configured-port>` only with the port found in the actual systemd unit or application configuration.

### Network checks

```bash
ss -tlnp
```

Verify both named service instances individually:

- `postgresql`: confirm its configured TCP port or Unix socket is listening.
- `fastapi-tutorial`: confirm the application listens on the port and binding specified by the systemd unit or application configuration.

