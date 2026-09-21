---
source-path: site-modules/profile_app_stack
---

# Migration Plan: profile_app_stack

**TLDR**: A Python web application stack that installs Python runtime, sets up PostgreSQL database (if localhost), deploys a Flask/Django app from Git with virtual environment, configures systemd service with Gunicorn, and sets up monitoring with Prometheus exporters in production.

## Service Type and Instances

**Service Type**: Python Web Application Stack

**Configured Instances**:
- **myapp**: Python web application
  - Location/Path: `/opt/myapp`
  - Port/Socket: `8000`
  - Key Config: Gunicorn WSGI server, 4 workers, sync worker class, PostgreSQL backend

## File Structure

```
site-modules/profile_app_stack/
├── manifests/
│   ├── init.pp
│   ├── python.pp
│   ├── database.pp
│   ├── app.pp
│   ├── service.pp
│   └── monitoring.pp
├── templates/
│   ├── logrotate.conf.erb
│   ├── app.env.erb
│   └── app.service.epp
└── data/
    ├── common.yaml
    ├── environment/
    │   ├── production.yaml
    │   └── staging.yaml

site-modules/profile/
└── manifests/
    └── app/
        └── stack.pp

site-modules/role/
└── manifests/
    └── app_server.pp

site-modules/profile_postgresql/
└── manifests/
    └── init.pp
```

## Module Explanation

The module performs operations in this order:

1. **role::app_server** (`site-modules/role/manifests/app_server.pp`):
   - Entry point class that includes profile::base::base
   - Includes profile::loadbalancer::haproxy
   - Includes profile::cache::redis
   - Includes profile::app::stack

2. **profile::app::stack** (`site-modules/profile/manifests/app/stack.pp`):
   - Wrapper class that includes profile_app_stack
   - Uses fact('environment') for environment-specific behavior

3. **profile_app_stack** (`site-modules/profile_app_stack/manifests/init.pp`):
   - Sets class parameters from Hiera lookups
   - Builds database URL: `postgresql://myapp:ENCRYPTED_PASSWORD@localhost:5432/myapp_db`
   - Contains profile_app_stack::python
   - Contains profile_app_stack::database
   - Contains profile_app_stack::app
   - Contains profile_app_stack::service
   - Contains profile_app_stack::monitoring
   - Sets ordering: `profile_app_stack::python -> profile_app_stack::database -> profile_app_stack::app ~> profile_app_stack::service -> profile_app_stack::monitoring`

4. **profile_app_stack::python** (`site-modules/profile_app_stack/manifests/python.pp`):
   - Package python3 → ensure: present
   - Package python3-pip → ensure: present
   - Package python3-venv → ensure: present
   - Package python3-dev → ensure: present
   - Package build-essential → ensure: present
   - Package git → ensure: present
   - Group myapp → ensure: present, gid: 1001
   - User myapp → ensure: present, uid: 1001, gid: 1001, home: /opt/myapp, shell: /bin/bash
   - File /var/log/myapp → ensure: directory, owner: myapp, group: myapp, mode: 0755
   - File /etc/logrotate.d/myapp (template logrotate.conf.erb) → owner: root, group: root, mode: 0644

5. **profile_app_stack::database** (`site-modules/profile_app_stack/manifests/database.pp`):
   - Conditional: if db_host == 'localhost' (TRUE in staging/development):
     - Contains profile_postgresql
     - Exec create_db_user → command: createuser -h localhost -p 5432 myapp, user: postgres
     - Exec create_database → command: createdb -h localhost -p 5432 -O myapp myapp_db, user: postgres
     - Exec grant_db_privileges → command: psql -h localhost -p 5432 -c "GRANT ALL PRIVILEGES ON DATABASE myapp_db TO myapp;", user: postgres
   - File /usr/local/bin/db-backup.sh → owner: root, group: root, mode: 0755
   - Cron database_backup → command: /usr/local/bin/db-backup.sh, user: root, hour: 2, minute: 0

6. **profile_app_stack::app** (`site-modules/profile_app_stack/manifests/app.pp`):
   - File /opt/myapp → ensure: directory, owner: myapp, group: myapp, mode: 0755
   - Vcsrepo /opt/myapp → ensure: present, provider: git, source: https://github.com/company/myapp.git, revision: v1.2.3 (production) / develop (staging), owner: myapp, group: myapp
   - Exec create_app_venv → command: python3 -m venv /opt/myapp/venv, user: myapp, cwd: /opt/myapp
   - Exec install_requirements → command: /opt/myapp/venv/bin/pip install -r requirements.txt, user: myapp, cwd: /opt/myapp
   - Exec install_pip_packages → command: /opt/myapp/venv/bin/pip install gunicorn psycopg2-binary, user: myapp
   - File /opt/myapp/.env (template app.env.erb) → owner: myapp, group: myapp, mode: 0600
   - File /usr/local/bin/app-healthcheck.sh → owner: root, group: root, mode: 0755
   - Exec run_db_migrations → command: /opt/myapp/venv/bin/python manage.py migrate, user: myapp, cwd: /opt/myapp

7. **profile_app_stack::service** (`site-modules/profile_app_stack/manifests/service.pp`):
   - File /etc/systemd/system/myapp.service (template app.service.epp) → owner: root, group: root, mode: 0644
   - Exec systemd_daemon_reload → command: systemctl daemon-reload
   - Service myapp → ensure: running, enable: true
   - Notifies: file[myapp.service] ~> exec[systemd_daemon_reload] ~> service[myapp]

8. **profile_app_stack::monitoring** (`site-modules/profile_app_stack/manifests/monitoring.pp`):
   - Virtual Package prometheus-node-exporter → ensure: present
   - Virtual Service prometheus-node-exporter → ensure: running, enable: true
   - Virtual Package prometheus-pushgateway → ensure: present
   - Virtual Cron push_app_metrics → command: /usr/local/bin/app-healthcheck.sh | curl -X POST --data-binary @- http://localhost:9091/metrics/job/myapp, user: myapp, minute: */5
   - Conditional: if facts['environment'] == 'production':
     - Realize Package[prometheus-node-exporter]
     - Realize Service[prometheus-node-exporter]
     - Realize Package[prometheus-pushgateway]
     - Realize Cron[push_app_metrics]
   - Cron app_health_check → command: /usr/local/bin/app-healthcheck.sh, user: root, minute: */2

## Variables

**Variable Flow Summary**: 22 variables across 3 Hiera levels

### Variable Definitions

**common.yaml (defaults)** → Migration note: Base defaults for all nodes
- `profile_app_stack::app_name`: `myapp` (type: string)
- `profile_app_stack::app_repo`: `https://github.com/company/myapp.git` (type: string)
- `profile_app_stack::app_revision`: `main` (type: string)
- `profile_app_stack::app_port`: `8000` (type: integer)
- `profile_app_stack::app_dir`: `/opt/myapp` (type: string)
- `profile_app_stack::app_user`: `myapp` (type: string)
- `profile_app_stack::app_group`: `myapp` (type: string)
- `profile_app_stack::python_version`: `3.9` (type: string)
- `profile_app_stack::pip_packages`: `['gunicorn', 'psycopg2-binary']` (type: array)
- `profile_app_stack::db_host`: `localhost` (type: string)
- `profile_app_stack::db_port`: `5432` (type: integer)
- `profile_app_stack::db_name`: `myapp_db` (type: string)
- `profile_app_stack::db_user`: `myapp` (type: string)
- `profile_app_stack::db_password`: `changeme` (type: string)
- `profile_app_stack::worker_count`: `2` (type: integer)
- `profile_app_stack::worker_class`: `sync` (type: string)
- `profile_app_stack::max_requests`: `100` (type: integer)
- `profile_app_stack::graceful_timeout`: `30` (type: integer)
- `profile_app_stack::log_dir`: `/var/log/myapp` (type: string)
- `profile_app_stack::log_level`: `info` (type: string)
- `profile_app_stack::log_max_size`: `100M` (type: string)
- `profile_app_stack::log_rotate_count`: `7` (type: integer)

**environment/production.yaml (overrides)** → Migration note: Production-specific variables for performance and security
- `profile_app_stack::app_revision`: `v1.2.3` (type: string)
- `profile_app_stack::worker_count`: `4` (type: integer)
- `profile_app_stack::max_requests`: `1000` (type: integer)
- `profile_app_stack::log_level`: `info` (type: string)
- `profile_app_stack::db_host`: `db.prod.internal` (type: string)
- `profile_app_stack::db_port`: `5432` (type: integer)
- `profile_app_stack::secret_key`: `ENC[PKCS7,encrypted_value]` (type: string)

**environment/staging.yaml (overrides)** → Migration note: Staging-specific variables for development and testing
- `profile_app_stack::app_revision`: `develop` (type: string)
- `profile_app_stack::worker_count`: `2` (type: integer)
- `profile_app_stack::max_requests`: `100` (type: integer)
- `profile_app_stack::log_level`: `debug` (type: string)
- `profile_app_stack::db_host`: `localhost` (type: string)
- `profile_app_stack::secret_key`: `staging-secret-key` (type: string)

### Variable Migration Summary

- **Common defaults**: 22 variables from common.yaml (base configuration for all nodes)
- **OS-specific variables**: 0 variables that vary by operating system family
- **Environment-specific variables**: 12 variables that vary by deployment environment (production: 7, staging: 5)
- **Host-specific variables**: 0 variables for individual host overrides
- **Encrypted variables**: 2 variables that are encrypted (eyaml) and need secure storage

### Cross-Level Overrides

Variables defined at multiple Hiera levels:
- **profile_app_stack::app_revision**: defined at common and environment levels, merge strategy: first
- **profile_app_stack::worker_count**: defined at common and environment levels, merge strategy: first
- **profile_app_stack::max_requests**: defined at common and environment levels, merge strategy: first
- **profile_app_stack::log_level**: defined at common and environment levels, merge strategy: first
- **profile_app_stack::db_host**: defined at common and environment levels, merge strategy: first
- **profile_app_stack::secret_key**: defined at environment levels only, merge strategy: first

### Merge Strategy Notes

- Variables using `first` (default) - First value found wins, no merging

## Dependencies

**External module dependencies**:
- `puppetlabs-vcsrepo` (Git repository management)
- `puppetlabs-stdlib` (standard library functions)
- `puppet-systemd` (systemd service management)

**System package dependencies**:
- `python3`, `python3-pip`, `python3-venv`, `python3-dev`
- `build-essential`, `git`
- `postgresql-server` (when db_host=localhost)
- `prometheus-node-exporter`, `prometheus-pushgateway` (production only)

**Service dependencies**:
- PostgreSQL must be running before application starts
- Application service must reload when configuration changes
- Monitoring depends on application being configured

## Puppet Facts Used

- `$facts['environment']`: Determines production vs staging behavior for monitoring and application configuration
- `fact('environment')`: Used in profile::app::stack wrapper class for environment-specific behavior

## Template Conversion Notes

**logrotate.conf.erb**: Simple variable substitution template with 4 variables - log_dir, log_rotate_count, log_max_size, and app_name.

**app.env.erb**: Contains 1 conditional logic block based on environment fact with 8 variables - sets DEBUG, ALLOWED_HOSTS, and CORS_ORIGINS differently for production vs non-production environments. Variables: db_url, app_name, app_port, secret_key, log_level, log_dir, worker_count, facts['environment'].

**app.service.epp**: Complex systemd unit template with 1 logic block and 11 parameters including security hardening directives, resource limits, and logging configuration. Variables: app_name, app_dir, app_user, app_group, app_port, worker_count, worker_class, max_requests, graceful_timeout, log_dir, log_level.

## Checks for the Migration

**Files to verify**:
- `site-modules/role/manifests/app_server.pp`
- `site-modules/profile/manifests/app/stack.pp`
- `site-modules/profile_app_stack/manifests/init.pp`
- `site-modules/profile_app_stack/manifests/python.pp`
- `site-modules/profile_app_stack/manifests/database.pp`
- `site-modules/profile_app_stack/manifests/app.pp`
- `site-modules/profile_app_stack/manifests/service.pp`
- `site-modules/profile_app_stack/manifests/monitoring.pp`
- `site-modules/profile_app_stack/templates/logrotate.conf.erb`
- `site-modules/profile_app_stack/templates/app.env.erb`
- `site-modules/profile_app_stack/templates/app.service.epp`
- `site-modules/profile_app_stack/data/common.yaml`
- `site-modules/profile_app_stack/data/environment/production.yaml`
- `site-modules/profile_app_stack/data/environment/staging.yaml`
- `site-modules/profile_postgresql/manifests/init.pp`

**Service endpoints to check**:
- `http://localhost:8000` (myapp HTTP endpoint)
- `postgresql://localhost:5432` (database connection, staging only)
- `http://localhost:9100` (node exporter, production only)
- `http://localhost:9091` (pushgateway, production only)

**Templates rendered**:
- `logrotate.conf.erb` → `/etc/logrotate.d/myapp` (1 render)
- `app.env.erb` → `/opt/myapp/.env` (1 render)
- `app.service.epp` → `/etc/systemd/system/myapp.service` (1 render)

## Pre-flight checks:
```bash
# Service status commands
systemctl status myapp

# Instance-specific checks
curl -f http://localhost:8000/health
sudo -u myapp /opt/myapp/venv/bin/python -c "import app"

# Configuration validation commands
test -f /opt/myapp/.env
test -f /etc/systemd/system/myapp.service
test -d /var/log/myapp

# Network/connectivity checks (staging only)
psql -h localhost -U myapp -d myapp_db -c "SELECT 1;"
```