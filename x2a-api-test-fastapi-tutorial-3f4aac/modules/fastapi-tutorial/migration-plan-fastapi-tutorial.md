---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys a FastAPI application and PostgreSQL database. The analyzed recipe installs platform-specific Python, Git, PostgreSQL, and development packages; creates an application directory and virtual environment; checks out the application; installs Python requirements; initializes and starts PostgreSQL; creates the `fastapi` role and `fastapi_db` database; writes an inline `.env` file and systemd unit; and enables and starts the FastAPI service. The source analysis identifies the application path, repository, revision, service name, file contents, file modes, ownership, and FastAPI port only through Chef attributes or inline content in `cookbooks/fastapi-tutorial/recipes/default.rb`; values not exposed by the analysis must be verified from the source before migration. The cookbook also contains three inventory-only `nginx_sites` data bags and one encrypted `nginx_secrets` item that are not consumed by the analyzed FastAPI recipe.

## Service Type and Instances

**Service Type**: Application server backed by PostgreSQL

**Configured Instances**:

- **FastAPI application**
  - Purpose: Application server deployed from the cookbook's Git repository.
  - Location/Path: `node['fastapi_tutorial']['app_path']`; the original plan identifies this as `/opt/fastapi-tutorial`, which must be verified from `cookbooks/fastapi-tutorial/attributes/default.rb` or the recipe.
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git` — verify from the recipe.
  - Revision: `main` — verify from the recipe.
  - Virtual environment: `/opt/fastapi-tutorial/venv` if the application path resolves to `/opt/fastapi-tutorial`.
  - Requirements file: `/opt/fastapi-tutorial/requirements.txt` if the application path resolves to `/opt/fastapi-tutorial`.
  - Environment file: `/opt/fastapi-tutorial/.env` if the application path resolves to `/opt/fastapi-tutorial`.
  - Port/Socket: Port `8000` is the expected port from the original plan but must be confirmed from the inline systemd unit content.
  - Systemd unit: `/etc/systemd/system/#{service_name}.service`; the resolved service name must be obtained from the original recipe.
  - Configuration: The unit and `.env` file are written by inline Chef `file` resources. Their exact content must be preserved from the source.

- **PostgreSQL**
  - Purpose: Database service for the FastAPI application.
  - Service name: `postgresql`
  - Database user: `fastapi`
  - Database password: `fastapi_password` in the current Chef recipe; migrate this value to Ansible Vault or an approved AAP credential.
  - Database name: `fastapi_db`
  - Database owner: `fastapi`
  - Privileges: `ALL PRIVILEGES` on `fastapi_db`
  - Port/Socket: PostgreSQL default TCP port `5432` and the platform-default Unix socket, unless target configuration specifies otherwise.

**Inventory-only nginx sites**:

- **`ci.cluster.local`**
  - Document root: `/var/www/ci.cluster.local`
  - SSL enabled: `true`
  - FastAPI execution flow: Not consumed by the analyzed recipe.

- **`status.cluster.local`**
  - Document root: `/var/www/status.cluster.local`
  - SSL enabled: `true`
  - FastAPI execution flow: Not consumed by the analyzed recipe.

- **`test.cluster.local`**
  - Document root: `/var/www/test.cluster.local`
  - SSL enabled: `true`
  - FastAPI execution flow: Not consumed by the analyzed recipe.

No `.each` loops or collection iterations are present in the analyzed execution tree.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

```text
cookbooks/fastapi-tutorial/
├── attributes/
│   └── default.rb
└── recipes/
    └── default.rb

data_bags/
├── nginx_secrets/
│   └── site.json
└── nginx_sites/
    ├── ci.cluster.local.json
    ├── status.cluster.local.json
    └── test.cluster.local.json
```

**Recipes:**
```text
cookbooks/fastapi-tutorial/recipes/default.rb
```

**Providers:**
```text
```

No custom resources or provider files are present.

**Templates:**
```text
```

No `.erb` templates are rendered.

**Attributes:**
```text
cookbooks/fastapi-tutorial/attributes/default.rb
```

**Files:**
```text
```

No static files are deployed by `cookbook_file` or `remote_file`.

**Data bags:**
```text
data_bags/nginx_secrets/site.json
data_bags/nginx_sites/ci.cluster.local.json
data_bags/nginx_sites/status.cluster.local.json
data_bags/nginx_sites/test.cluster.local.json
```

## Module Explanation

The cookbook performs operations in this order:

1. **`default`** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Evaluates the platform family.
   - On RHEL/Fedora systems, installs `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, and `libpq-devel`.
   - On non-RHEL/Fedora systems, installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - On RHEL/Fedora systems, runs `postgresql-setup --initdb`.
   - Creates the application directory represented by `node['fastapi_tutorial']['app_path']`; the original plan identifies `/opt/fastapi-tutorial`, but mode and ownership must be verified from the recipe.
   - Checks out the configured Git repository and revision into the application path. The original plan identifies `https://github.com/dibanez/fastapi_tutorial.git` at `main`; both values require source verification.
   - Creates the virtual environment at `/opt/fastapi-tutorial/venv` when the application path is `/opt/fastapi-tutorial`.
   - Installs dependencies from `/opt/fastapi-tutorial/requirements.txt` into that virtual environment.
   - Enables and starts the `postgresql` service.
   - As the PostgreSQL operating-system user, creates role `fastapi` with the current password `fastapi_password`.
   - Creates database `fastapi_db` owned by `fastapi`.
   - Grants `ALL PRIVILEGES` on `fastapi_db` to `fastapi`.
   - Writes the inline application environment file at `/opt/fastapi-tutorial/.env`; preserve the exact source content and verify whether it contains database credentials.
   - Writes the inline systemd unit at `/etc/systemd/system/#{service_name}.service`; obtain the resolved service name and exact unit content from the recipe.
   - Defines `execute[systemd_reload]` for `systemctl daemon-reload` with action `:nothing`. The analyzed tree shows no notification relationship, so an automatic reload is not confirmed.
   - Enables and starts the dynamic FastAPI service resource `service[service_name]`.
   - No `.each` loops require expansion.

**Source provider**: `cookbooks/fastapi-tutorial/recipes/default.rb` is the source recipe. No custom provider files are present.

## Dependencies

**External cookbook dependencies**: None identified. No `include_recipe` or external cookbook custom resource appears in the analyzed execution tree.

**System package dependencies**:

- RHEL/Fedora:
  - `python3`
  - `python3-pip`
  - `git`
  - `postgresql-server`
  - `postgresql-contrib`
  - `libpq-devel`
- Non-RHEL/Fedora:
  - `python3`
  - `python3-pip`
  - `python3-venv`
  - `git`
  - `postgresql`
  - `postgresql-contrib`
  - `libpq-dev`

**Python dependency source**: `/opt/fastapi-tutorial/requirements.txt`

**Service dependencies**:

- PostgreSQL: `postgresql`
- FastAPI: dynamic value of `service_name`, which must be resolved from the recipe
- FastAPI depends on the application checkout, virtual environment, requirements installation, `.env` file, and systemd unit

## Credentials

**Detection Summary**: 2 credential sources detected across the executed recipe and data bag inventory.

### PostgreSQL `fastapi` database password

- **Variable(s)**: No Chef attribute variable; literal `fastapi_password`
- **Source file(s)**: `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in an inline shell command
- **Usage context**: PostgreSQL role creation; whether the same value is written to `.env` must be verified from the inline heredoc
- **Migration handling**: Store the value in Ansible Vault or an approved AAP credential. Use the protected value for `community.postgresql.postgresql_user` and the application configuration only if the source `.env` confirms that usage.

### Encrypted `nginx_secrets/site` data bag

- **Variable(s)/keys**: `id`, `token`
- **Source file(s)**: `data_bags/nginx_secrets/site.json`
- **Current storage**: Encrypted Chef data bag item
- **Usage context**: Not read by the analyzed FastAPI execution tree
- **Migration handling**: Do not copy values into ordinary Ansible variables. Migrate only if another execution path requires this item.

No additional credential references can be ruled out until the inline `.env` content is inspected.

### Non-secret `nginx_sites` data bag items

- **`ci.cluster.local`**
  - Source: `data_bags/nginx_sites/ci.cluster.local.json`
  - Document root: `/var/www/ci.cluster.local`
  - SSL enabled: `true`
  - Usage: Not shown in the FastAPI flow

- **`status.cluster.local`**
  - Source: `data_bags/nginx_sites/status.cluster.local.json`
  - Document root: `/var/www/status.cluster.local`
  - SSL enabled: `true`
  - Usage: Not shown in the FastAPI flow

- **`test.cluster.local`**
  - Source: `data_bags/nginx_sites/test.cluster.local.json`
  - Document root: `/var/www/test.cluster.local`
  - SSL enabled: `true`
  - Usage: Not shown in the FastAPI flow

## Checks for the Migration

**Files to verify**:

- `cookbooks/fastapi-tutorial/recipes/default.rb`
- `cookbooks/fastapi-tutorial/attributes/default.rb`
- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv/bin/python`
- `/opt/fastapi-tutorial/venv/bin/pip`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/<resolved-service-name>.service`
- PostgreSQL data directory
- PostgreSQL logs
- `data_bags/nginx_secrets/site.json`
- `data_bags/nginx_sites/ci.cluster.local.json`
- `data_bags/nginx_sites/status.cluster.local.json`
- `data_bags/nginx_sites/test.cluster.local.json`

**Service endpoints to check**:

- FastAPI: TCP port `8000`, pending confirmation from the systemd unit
- PostgreSQL: TCP port `5432` unless changed by platform configuration
- PostgreSQL platform-default Unix socket
- `ci.cluster.local`: no deployed endpoint in this recipe
- `status.cluster.local`: no deployed endpoint in this recipe
- `test.cluster.local`: no deployed endpoint in this recipe

**Templates rendered**: 0

No templates are rendered. Two inline files are written by Chef `file` resources:

1. `/opt/fastapi-tutorial/.env`
2. `/etc/systemd/system/<resolved-service-name>.service`

Their exact contents, modes, ownership, and service name must be obtained from the source recipe.

## Pre-flight checks

```bash
# Verify source-derived values before deployment
grep -nE "app_path|service_name|git|repository|revision|ExecStart|8000|\\.env" \
  cookbooks/fastapi-tutorial/recipes/default.rb
grep -n "fastapi_tutorial" cookbooks/fastapi-tutorial/attributes/default.rb

# Verify Python and Git
python3 --version
git --version

# Verify the PostgreSQL instance
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
sudo -u postgres pg_isready

# Verify the FastAPI instance.
# Replace <resolved-service-name> with the value obtained from the recipe.
systemctl status <resolved-service-name>
systemctl is-enabled <resolved-service-name>
systemctl is-active <resolved-service-name>
test -f /etc/systemd/system/<resolved-service-name>.service
systemd-analyze verify /etc/systemd/system/<resolved-service-name>.service

# Verify the FastAPI application path and checkout
test -d /opt/fastapi-tutorial
git -C /opt/fastapi-tutorial remote -v
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
git -C /opt/fastapi-tutorial status --short
test -f /opt/fastapi-tutorial/requirements.txt

# Verify the virtual environment and dependencies
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
/opt/fastapi-tutorial/venv/bin/python --version
/opt/fastapi-tutorial/venv/bin/pip check

# Verify the PostgreSQL role and database
sudo -u postgres psql -tAc \
  "SELECT 1 FROM pg_roles WHERE rolname = 'fastapi';"
sudo -u postgres psql -tAc \
  "SELECT datname, pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"
sudo -u postgres psql -d fastapi_db -c \
  "SELECT datname, datacl FROM pg_database WHERE datname = 'fastapi_db';"

# Verify application database connectivity using an approved secret source
PGPASSWORD='<retrieve-from-approved-secret-store>' \
  psql -h localhost -U fastapi -d fastapi_db -c "SELECT version();"

# Verify the application environment file without exposing secrets
test -f /opt/fastapi-tutorial/.env
sed -E 's/(PASSWORD|PASS|TOKEN|SECRET|KEY)=.*/\1=<redacted>/' \
  /opt/fastapi-tutorial/.env

# Verify the FastAPI endpoint if port 8000 is confirmed from the unit
ss -tlnp | grep ':8000'
lsof -iTCP:8000 -sTCP:LISTEN
curl -I http://127.0.0.1:8000/
curl -sS http://127.0.0.1:8000/

# Verify PostgreSQL network endpoints
ss -tlnp | grep ':5432'
lsof -iTCP:5432 -sTCP:LISTEN

# Check service logs
journalctl -u <resolved-service-name> --no-pager -n 100
journalctl -u postgresql --no-pager -n 100
journalctl -u <resolved-service-name> --no-pager -n 100 | \
  grep -iE 'error|traceback|failed'
journalctl -u postgresql --no-pager -n 100 | \
  grep -iE 'error|fatal|failed'

# Verify inventory-only data bag items individually
test -f data_bags/nginx_sites/ci.cluster.local.json
test -f data_bags/nginx_sites/status.cluster.local.json
test -f data_bags/nginx_sites/test.cluster.local.json
test -f data_bags/nginx_secrets/site.json
```

The migration order must remain:

1. Install platform-specific packages.
2. Initialize PostgreSQL on RHEL/Fedora systems.
3. Create the application directory.
4. Check out the configured Git repository and revision.
5. Create the Python virtual environment.
6. Install `requirements.txt`.
7. Enable and start PostgreSQL.
8. Create PostgreSQL role `fastapi`.
9. Create database `fastapi_db` owned by `fastapi`.
10. Grant `ALL PRIVILEGES` on `fastapi_db` to `fastapi`.
11. Write `.env` using protected values where confirmed by the source.
12. Write the FastAPI systemd unit.
13. Reload systemd only as an intentional migration improvement or when required by the migrated unit deployment; the analyzed Chef resource is action `:nothing` with no confirmed notification.
14. Enable and start the resolved FastAPI systemd service.