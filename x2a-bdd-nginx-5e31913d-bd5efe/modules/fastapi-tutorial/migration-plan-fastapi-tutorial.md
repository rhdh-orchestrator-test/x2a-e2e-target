---
source-path: cookbooks/fastapi-tutorial
---

# Migration Plan: fastapi-tutorial

**TLDR**: This cookbook installs Python, Git, PostgreSQL, and PostgreSQL development packages; checks out the FastAPI tutorial application into `/opt/fastapi-tutorial`; creates a Python virtual environment; installs the application requirements; creates the PostgreSQL user and database; writes an environment file containing the database connection string; and manages the application with the `fastapi-tutorial.service` systemd unit. The FastAPI application listens on TCP port `8000`. PostgreSQL uses its default local configuration; port `5432` is inferred as the default and is not explicitly configured by the cookbook.

## Service Type and Instances

**Service Type**: Application Server with PostgreSQL database dependency

**Configured Instances**:

- **fastapi-tutorial**: FastAPI application served by Uvicorn
  - Application directory: `/opt/fastapi-tutorial`
  - Virtual environment: `/opt/fastapi-tutorial/venv`
  - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
  - Repository revision: `main`
  - Application module: `app.main:app`
  - Process command: `/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Bind address: `0.0.0.0`
  - Port: `8000`
  - Systemd unit: `/etc/systemd/system/fastapi-tutorial.service`
  - Service user: `root`
  - Working directory: `/opt/fastapi-tutorial`
  - Restart policy: `Restart=always`

- **postgresql**: PostgreSQL database service
  - Service name: `postgresql`
  - Database user: `fastapi`
  - Database name: `fastapi_db`
  - Database owner: `fastapi`
  - Database host: `localhost`
  - Port: PostgreSQL default port `5432`; inferred, not explicitly configured by the cookbook
  - Required privileges: `ALL PRIVILEGES` on `fastapi_db` for user `fastapi`

There are no collection attributes, `.each` loops, or repeated instances.

## File Structure

**MANDATORY: Preserve this section from the original plan.**

```text
cookbooks/fastapi-tutorial/
├── recipes/
│   └── default.rb
├── providers/
│   └── None
├── templates/
│   └── None
├── attributes/
│   └── None
└── files/
    └── None
```

**Recipes:**
```text
recipes/default.rb
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

The `.env` file and systemd unit are generated directly by `file` resources in `cookbooks/fastapi-tutorial/recipes/default.rb`; they are not cookbook templates or static files.

## Module Explanation

The cookbook has one recipe and no `include_recipe` calls. The complete execution order is:

1. **default** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Installs the operating-system packages:
     - `python3`
     - `python3-pip`
     - `python3-venv`
     - `git`
     - `postgresql`
     - `postgresql-contrib`
     - `libpq-dev`
   - Resource: `package (1)`
   - Use distribution-specific package naming if supporting both Ubuntu and CentOS.

2. **default — application directory** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/opt/fastapi-tutorial`.
   - Owner: `root`
   - Group: `root`
   - Mode: `0755`
   - Recursive creation is enabled.
   - Resource: `directory (1)`

3. **default — source checkout** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Synchronizes the Git repository into `/opt/fastapi-tutorial`.
   - Repository: `https://github.com/dibanez/fastapi_tutorial.git`
   - Revision: `main`
   - Resource: `git (1)`

4. **default — Python virtual environment** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Executes:
     ```bash
     python3 -m venv /opt/fastapi-tutorial/venv
     ```
   - The command is guarded by the existence of `/opt/fastapi-tutorial/venv`.
   - Resource: `execute[create_venv] (1)`

5. **default — Python dependencies** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Executes:
     ```bash
     /opt/fastapi-tutorial/venv/bin/pip install -r /opt/fastapi-tutorial/requirements.txt
     ```
   - Working directory: `/opt/fastapi-tutorial`
   - Resource: `execute[install_dependencies] (1)`
   - The Git checkout must complete before `/opt/fastapi-tutorial/requirements.txt` is consumed.

6. **default — PostgreSQL service** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Enables and starts the `postgresql` service.
   - Resource: `service[postgresql] (1)`

7. **default — PostgreSQL user and database** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Executes `execute[create_db_user]`.
   - Resource: `execute[create_db_user] (1)`
   - The original command performs these operations:
     ```bash
     sudo -u postgres psql -c "CREATE USER fastapi WITH PASSWORD 'fastapi_password';" || true
     sudo -u postgres psql -c "CREATE DATABASE fastapi_db OWNER fastapi;" || true
     sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE fastapi_db TO fastapi;" || true
     ```
   - The `psql` commands do not explicitly configure a host or port.
   - The Ansible migration should use idempotent PostgreSQL modules where available:
     - `community.postgresql.postgresql_user`
     - `community.postgresql.postgresql_db`
     - `community.postgresql.postgresql_privs`
   - Execute database administration as the PostgreSQL administrative account, normally `postgres`.
   - Create user `fastapi`, set its password, create `fastapi_db`, set `fastapi` as owner, and grant all privileges to `fastapi`.
   - Do not retain shell-level `|| true` behavior unless intentionally matching the cookbook’s error suppression.

8. **default — application environment file** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/opt/fastapi-tutorial/.env`.
   - Owner: `root`
   - Group: `root`
   - Mode: `0644`
   - Resource: `file (1)`
   - Content:
     ```dotenv
     PROJECT_NAME="FastAPI Tutorial"
     API_VERSION=1.0.0
     DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
     ```
   - Store the password in Ansible Vault or an approved secret backend and use the vaulted value when rendering `DATABASE_URL`.

9. **default — systemd service unit** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
   - Creates `/etc/systemd/system/fastapi-tutorial.service`.
   - Owner: `root`
   - Group: `root`
   - Mode: `0644`
   - Resource: `file (1)`
   - Unit contents:
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
   - Preserve the unit name, PostgreSQL ordering, service user, working directory, Uvicorn command, port `8000`, restart policy, and install target.

10. **default — systemd reload** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
    - Defines `execute[systemd_reload]`.
    - Command:
      ```bash
      systemctl daemon-reload
      ```
    - Action: `nothing`
    - Resource: `execute (1)`
    - The supplied structured analysis does not confirm that `file[/etc/systemd/system/fastapi-tutorial.service]` notifies this resource.
    - Treat the reload as a defined but normally inactive resource unless the notification is confirmed.
    - Implement the desired behavior in Ansible with a handler:
      ```yaml
      - name: daemon reload
        ansible.builtin.systemd:
          daemon_reload: true
      ```

11. **default — FastAPI service** (`cookbooks/fastapi-tutorial/recipes/default.rb`):
    - Enables and starts `fastapi-tutorial`.
    - Resource: `service[fastapi-tutorial] (1)`
    - Start only after the repository, virtual environment, Python dependencies, PostgreSQL service, database user, database, `.env` file, systemd unit, and systemd daemon reload are complete.
    - Use:
      ```yaml
      name: fastapi-tutorial
      enabled: true
      state: started
      daemon_reload: true
      ```

**Iterations**: None. No `.each` loops are present.

## Dependencies

**External cookbook dependencies**: None declared in `metadata.rb`.

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
  - Enabled and started by the recipe.
  - The FastAPI unit declares `After=network.target postgresql.service`.

**Application dependencies**:

- Git repository: `https://github.com/dibanez/fastapi_tutorial.git`
- Git revision: `main`
- Python requirements file: `/opt/fastapi-tutorial/requirements.txt`
- Ansible PostgreSQL collection, if PostgreSQL modules are used: `community.postgresql`

## Credentials

**Detection Summary**: 1 hardcoded database credential detected in 1 recipe file. The credential is used in both the database creation command and the application database URL.

**Source**:

- **Provider**: Hardcoded
- **URL**: None
- **Path**: None
- **Source file**: `cookbooks/fastapi-tutorial/recipes/default.rb`

### PostgreSQL password for user `fastapi`

- **Variable(s)**: No Chef attribute variable is used. Literal password: `fastapi_password`
- **Source file(s)**:
  - `cookbooks/fastapi-tutorial/recipes/default.rb`
- **Current storage**: Hardcoded in a shell command and generated `.env` content
- **Usage context**:
  - PostgreSQL user creation:
    ```bash
    CREATE USER fastapi WITH PASSWORD 'fastapi_password';
    ```
  - Application database connection:
    ```dotenv
    DATABASE_URL=postgresql://fastapi:fastapi_password@localhost/fastapi_db
    ```
- **Generated file containing the credential**: `/opt/fastapi-tutorial/.env`
- **Recommended Ansible storage**: Ansible Vault or an approved secret-management system. Use the vaulted variable in both the PostgreSQL user task and the generated `DATABASE_URL`.

No data bags, encrypted data bags, Chef Vault, CyberArk, Conjur, AWS Secrets Manager, environment-variable secret lookups, TLS certificates, private keys, API tokens, or SSH keys were detected.

## Checks for the Migration

**Files to verify**:

- `cookbooks/fastapi-tutorial/recipes/default.rb`
- `/opt/fastapi-tutorial`
- `/opt/fastapi-tutorial/venv`
- `/opt/fastapi-tutorial/requirements.txt`
- `/opt/fastapi-tutorial/.env`
- `/etc/systemd/system/fastapi-tutorial.service`

PostgreSQL data and log paths are not explicitly configured by this cookbook. Verify the distribution’s PostgreSQL service status and journal logs rather than assuming cookbook-defined paths.

**Service endpoints to check**:

- `fastapi-tutorial`: `0.0.0.0:8000`
- `postgresql`: `localhost:5432`, using PostgreSQL’s default port; the cookbook does not explicitly configure this port

**Unix sockets**:

- No socket path is explicitly configured.
- PostgreSQL local administration uses `sudo -u postgres psql`, which may use the distribution’s default PostgreSQL Unix socket.

**Templates rendered**:

- None. The recipe creates both configuration files directly with `file` resources.
- Environment file render count: `1` direct file resource.
- Systemd unit render count: `1` direct file resource.

## Pre-flight checks

### `fastapi-tutorial` instance

```bash
test -d /opt/fastapi-tutorial
stat -c '%U:%G %a %n' /opt/fastapi-tutorial

test -x /opt/fastapi-tutorial/venv/bin/python
/opt/fastapi-tutorial/venv/bin/python --version

test -f /opt/fastapi-tutorial/requirements.txt
git -C /opt/fastapi-tutorial status --short
git -C /opt/fastapi-tutorial branch --show-current
git -C /opt/fastapi-tutorial rev-parse --verify HEAD

stat -c '%U:%G %a %n' /opt/fastapi-tutorial/.env
grep '^PROJECT_NAME=' /opt/fastapi-tutorial/.env
grep '^API_VERSION=' /opt/fastapi-tutorial/.env
grep '^DATABASE_URL=' /opt/fastapi-tutorial/.env

stat -c '%U:%G %a %n' /etc/systemd/system/fastapi-tutorial.service
systemctl cat fastapi-tutorial.service
systemctl show fastapi-tutorial.service \
  --property=User,WorkingDirectory,ExecStart,Restart,After,UnitFileState,ActiveState

systemctl daemon-reload
systemctl is-enabled fastapi-tutorial
systemctl is-active fastapi-tutorial
systemctl status fastapi-tutorial

ss -ltnp | grep ':8000'
curl -i http://127.0.0.1:8000/
journalctl -u fastapi-tutorial --no-pager -n 100
```

Verify:

- `WorkingDirectory=/opt/fastapi-tutorial`
- `User=root`
- `ExecStart=/opt/fastapi-tutorial/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000`
- `Restart=always`
- The application accepts TCP connections on port `8000`.
- Uvicorn starts without import or dependency errors.
- The service is not repeatedly restarting.

The cookbook does not define a dedicated health-check endpoint; do not assume `/health` or `/ready` exists.

### `postgresql` instance

```bash
dpkg -l python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev 2>/dev/null || \
rpm -q python3 python3-pip python3-venv git postgresql postgresql-contrib libpq-dev

systemctl status postgresql
systemctl is-enabled postgresql
systemctl is-active postgresql

ss -ltnp | grep ':5432'
sudo -u postgres psql -c "SELECT version();"
journalctl -u postgresql --no-pager -n 100
```

Port `5432` is the expected PostgreSQL default, not an explicitly configured cookbook value.

### PostgreSQL user `fastapi` and database `fastapi_db`

```bash
sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='fastapi';"
sudo -u postgres psql -tAc "SELECT datname FROM pg_database WHERE datname='fastapi_db';"

PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT current_user, current_database();"

PGPASSWORD='fastapi_password' psql \
  -h localhost \
  -U fastapi \
  -d fastapi_db \
  -c "SELECT 1;"
```

Expected results:

- The `fastapi` role exists.
- The `fastapi_db` database exists.
- `fastapi` owns `fastapi_db`.
- The connection succeeds as user `fastapi`.
- `current_database()` returns `fastapi_db`.
- The user has the required privileges.

Avoid printing the database password to shared logs or terminal captures.