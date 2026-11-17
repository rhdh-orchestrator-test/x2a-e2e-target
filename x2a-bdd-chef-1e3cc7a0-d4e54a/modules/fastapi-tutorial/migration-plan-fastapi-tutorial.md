---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook deploys the FastAPI Tutorial application from `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`. It installs platform-specific Python, Git, and PostgreSQL dependencies, initializes PostgreSQL where required, creates a Python virtual environment, installs application requirements, provisions the `fastapi` PostgreSQL role and `fastapi_db` database, writes the application `.env` file, and manages the `fastapi-tutorial` systemd service. The application listens on `0.0.0.0:8000`.

## Service Type and Instances

**Service Type**: Application Server with a PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application server
  - Application path: `/opt/fastapi-tutorial`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Revision: `main`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Systemd service: `fastapi-tutorial.service`
  - Service unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Port/Socket: TCP `0.0.0.0:8000`
  - Start command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Service user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Restart policy: `always`
  - Database: `fastapi_db`
  - Database user: `fastapi`
  - Database endpoint: `localhost`

**PostgreSQL objects**:

- **Role**: `fastapi`
- **Password**: `fastapi_password`
- **Database**: `fastapi_db`
- **Database owner**: `fastapi`
- **Privileges**: All privileges on `fastapi_db` granted to `fastapi`

## File Structure

The following are the complete relevant files identified by the execution tree and directory listing.

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

No ERB templates are used. Configuration files are created with inline Chef `file` resources.

**Attributes:**
```text
cookbooks/fastapi-tutorial/attributes/default.rb
```

**Files:**
```text
```

No static files are deployed with `cookbook_file` or `remote_file`.

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs platform-specific system packages.
   - On Fedora/RHEL, installs `python3`, `python3-pip`, `git`, `postgresql-server`, `postgresql-contrib`, and `libpq-devel`.
   - On Fedora/RHEL, runs `postgresql-setup --initdb` only when `/var/lib/pgsql/data/PG_VERSION` is absent.
   - On non-Fedora/RHEL platforms, installs `python3`, `python3-pip`, `python3-venv`, `git`, `postgresql`, `postgresql-contrib`, and `libpq-dev`.
   - Creates `/opt/fastapi-tutorial` with owner `root`, group `root`, and mode `0755`.
   - Synchronizes `https://github.com/dibanez/fastapi_tutorial.git` at revision `main` into `/opt/fastapi-tutorial`.
   - Creates the virtual environment with:
     ```bash
     python3 -m venv /opt/fastapi-tutorial/venv
     ```
     The command is guarded by `/opt/fastapi-tutorial/venv`.
   - Installs Python dependencies from `/opt/fastapi-tutorial/requirements.txt` using:
     ```bash
     /opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt
     ```
     with `/opt/fastapi-tutorial` as the working directory.
   - Enables and starts the `postgresql` service.
   - Creates PostgreSQL role `fastapi` with password `fastapi_password`.
   - Creates database `fastapi_db` owned by `fastapi`.
   - Grants all privileges on `fastapi_db` to `fastapi`.
   - Writes `/opt/fastapi-tutorial/.env` with owner `root`, group `root`, and mode `0644`:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Writes `/etc/systemd/system/fastapi-tutorial.service` with owner `root`, group `root`, and mode `0644`.
   - Configures the systemd unit with:
     - Description: `FastAPI Tutorial Service`
     - Dependency ordering after `network.target` and `postgresql.service`
     - `User=root`
     - Working directory `/opt/fastapi-tutorial`
     - `PATH=/opt/fastapi-tutorial/venv/bin`
     - Uvicorn target `app.main:app`
     - Bind address `0.0.0.0`
     - TCP port `8000`
     - `Restart=always`
     - `WantedBy=multi-user.target`
   - Immediately runs `systemctl daemon-reload` when the systemd unit changes.
   - Enables and starts `fastapi-tutorial.service`.
   - No `.each` loops or collection iterations are present.

## Attributes

Source: `cookbooks/fastapi-tutorial/attributes/default.rb`

| Attribute | Value | Ansible equivalent |
|---|---|---|
| `node['fastapi_tutorial']['app_path']` | `/opt/fastapi-tutorial` | `app_path` |
| `node['fastapi_tutorial']['repository']` | `https://github.com/dibanez/fastapi_tutorial.git` | `repository` |
| `node['fastapi_tutorial']['revision']` | `main` | `repository_revision` |
| `node['fastapi_tutorial']['service_port']` | `8000` | `service_port` |

Recommended Ansible defaults:

```yaml
app_path: /opt/fastapi-tutorial
repository: https://github.com/dibanez/fastapi_tutorial.git
repository_revision: main
service_port: 8000
service_name: fastapi-tutorial
```

## Dependencies

**External cookbook dependencies**: None identified in the supplied metadata and execution tree.

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

- `/opt/fastapi-tutorial/requirements.txt`
- Installation target: `/opt/fastapi-tutorial/venv`

## Credentials

**Detection Summary**: 2 credential references detected in 2 source locations. One hardcoded PostgreSQL password is used during database provisioning and in the generated application connection string.

**Source**:

- **Provider**: Hardcoded in the Chef recipe; no Vault, CyberArk, AWS Secrets Manager, data bag, encrypted data bag, or environment-based secret retrieval was detected.
- **URL**: None detected.
- **Path**: None detected.

### PostgreSQL application password

- **Variable(s)**:
  - No named Chef attribute variable is used.
  - Literal password: `fastapi_password`
  - Resulting database URL: `postgresql://fastapi:fastapi_password@localhost/fastapi_db`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**:
  - Hardcoded in the PostgreSQL `execute` resource.
  - Written into `/opt/fastapi-tutorial/.env`.
- **Usage context**:
  - PostgreSQL role creation:
    ```sql
    CREATE USER fastapi WITH PASSWORD 'fastapi_password';
    ```
  - FastAPI database connection:
    ```text
    DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
    ```

The migration should store the password in Ansible Vault, AAP credentials, or an approved external secret provider. The same vaulted value must be used when creating the PostgreSQL role and rendering `/opt/fastapi-tutorial/.env`. The literal password must not be committed to the Ansible repository.

No TLS certificate, private key, API token, SSH key, data bag, Chef Vault item, Conjur variable, or environment-variable secret reference was detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/fastapi-tutorial/recipes/default.rb`
- `cookbooks/fastapi-tutorial/attributes/default.rb`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

**Service endpoints to check**:

- FastAPI: `0.0.0.0:8000`
- PostgreSQL: `localhost`
- Unix sockets: no explicit socket path configured

**Database objects to verify**:

- PostgreSQL role: `fastapi`
- PostgreSQL database: `fastapi_db`
- Database owner: `fastapi`
- Database privileges: all privileges granted to `fastapi`

**Templates rendered**:

- No templates rendered: `0`
- `/opt/fastapi-tutorial/.env`: inline `file` resource
- `/etc/systemd/system/fastapi-tutorial.service`: inline `file` resource

## Pre-flight checks

### Platform and package checks

```bash
python3 --version
python3 -m pip --version
git --version
```

Fedora/RHEL:

```bash
rpm -q python3 python3-pip git postgresql-server postgresql-contrib libpq-devel
test -f /var/lib/pgsql/data/PG_VERSION
```

Debian/Ubuntu-style systems:

```bash
dpkg -s python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev
```

### fastapi-tutorial instance checks

```bash
ls -ld /opt/fastapi-tutorial
git -C /opt/fastapi-tutorial remote -v
git -C /opt/fastapi-tutorial rev-parse --abbrev-ref HEAD
git -C /opt/fastapi-tutorial rev-parse HEAD
test -f /opt/fastapi-tutorial/requirements.txt
test -x /opt/fastapi-tutorial/venv/bin/python
test -x /opt/fastapi-tutorial/venv/bin/pip
test -x /opt/fastapi-tutorial/venv/bin/uvicorn
```

Expected repository state:

- Remote: `https://github.com/dibanez/fastapi_tutorial.git`
- Revision: `main`
- Application path: `/opt/fastapi-tutorial`
- Virtual environment: `/opt/fastapi-tutorial/venv`

### PostgreSQL service checks

```bash
systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql
```

### PostgreSQL database checks

```bash
sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname = 'fastapi';"
sudo -u postgres psql -tAc "SELECT datname FROM pg_database WHERE datname = 'fastapi_db';"
sudo -u postgres psql -tAc "SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname = 'fastapi_db';"
```

Expected results:

- The role query returns `1`.
- The database query returns `fastapi_db`.
- The owner query returns `fastapi`.

Test the application credentials without exposing the password in shared logs:

```bash
PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_user, current_database();"
```

### Environment configuration checks

```bash
stat -c '%U:%G %a %n' /opt/fastapi-tutorial/.env
grep -E '^(PROJECT_NAME|API_VERSION|DATABASE_URL)=' /opt/fastapi-tutorial/.env
grep '^PROJECT_NAME="FastAPI Tutorial"$' /opt/fastapi-tutorial/.env
grep '^API_VERSION=1.0.0$' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=postgresql://fastapi:' /opt/fastapi-tutorial/.env
```

Expected file ownership and permissions:

```text
root:root 0644 /opt/fastapi-tutorial/.env
```

### fastapi-tutorial systemd checks

```bash
systemctl cat fastapi-tutorial
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl status fastapi-tutorial
systemctl show fastapi-tutorial \
  --property=User,WorkingDirectory,ExecStart,Restart,ActiveState,SubState
systemd-analyze verify /etc/systemd/system/fastapi-tutorial.service
```

Verify the expected unit configuration:

```bash
grep '^Description=FastAPI Tutorial Service$' \
  /etc/systemd/system/fastapi-tutorial.service

grep '^WorkingDirectory=/opt/fastapi-tutorial$' \
  /etc/systemd/system/fastapi-tutorial.service

grep '^ExecStart=/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000$' \
  /etc/systemd/system/fastapi-tutorial.service

grep '^Restart=always$' \
  /etc/systemd/system/fastapi-tutorial.service
```

### FastAPI endpoint checks

```bash
ss -tlnp | grep ':8000'
curl -i http://127.0.0.1:8000/
ps aux | grep '[u]vicorn app.main:app'
```

The endpoint must return an HTTP response from the FastAPI application. No health endpoint is defined by the cookbook.

### Service logs

```bash
journalctl -u fastapi-tutorial --no-pager -n 100
journalctl -u postgresql --no-pager -n 100
```

### Fedora/RHEL PostgreSQL initialization check

```bash
ls -lah /var/lib/pgsql/data/
test -f /var/lib/pgsql/data/PG_VERSION
```

### Deployment filesystem checks

```bash
find /opt/fastapi-tutorial -maxdepth 2 -type f -print
du -sh /opt/fastapi-tutorial
```

### Migration acceptance criteria

1. The correct platform-specific package set is installed.
2. Fedora/RHEL PostgreSQL initialization runs only when `/var/lib/pgsql/data/PG_VERSION` is absent.
3. `/opt/fastapi-tutorial` contains the configured repository at revision `main`.
4. `/opt/fastapi-tutorial/venv` exists and contains the installed requirements.
5. PostgreSQL is enabled and running.
6. PostgreSQL contains role `fastapi` and database `fastapi_db`.
7. `/opt/fastapi-tutorial/.env` contains the expected FastAPI and PostgreSQL configuration.
8. `/etc/systemd/system/fastapi-tutorial.service` contains the expected command and port `8000`.
9. Systemd is reloaded after the unit file changes.
10. `fastapi-tutorial.service` is enabled and active.
11. The FastAPI service listens on TCP port `8000`.
12. The FastAPI process can connect to `fastapi_db` using the configured credentials.