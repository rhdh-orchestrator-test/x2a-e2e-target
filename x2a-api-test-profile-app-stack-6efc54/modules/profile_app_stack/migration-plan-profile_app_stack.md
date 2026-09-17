---
source-path: site-modules/profile_app_stack
---

# Migration Plan: role::app_server

**TLDR**: A complete application server role that deploys a Python web application stack with HAProxy load balancer, Redis cache, PostgreSQL database, and base system utilities. Manages the full service architecture including load balancing, caching, application deployment from Git, database provisioning, monitoring, and foundational system services.

## Service Type and Instances

**Service Type**: Application Server (Multi-Service Stack)

**Configured Instances**:
- **haproxy**: Load balancer frontend
  - Location/Path: `/etc/haproxy/haproxy.cfg`
  - Port/Socket: `80`, `443`, `8404` (stats)
  - Key Config: SSL termination, backend health checks, statistics interface

- **myapp-api**: Python FastAPI/Django web application
  - Location/Path: `/opt/myapp-api`
  - Port/Socket: `8000`
  - Key Config: Gunicorn WSGI server with 2-8 workers (environment-dependent), PostgreSQL backend, systemd service management

- **redis-cluster**: Redis cache cluster
  - Location/Path: `/etc/redis/redis.conf`
  - Port/Socket: `6379`
  - Key Config: Cluster mode, persistence, memory management

- **postgresql**: Database server (staging only)
  - Location/Path: `/var/lib/postgresql/14/main`
  - Port/Socket: `5432`
  - Key Config: Database myapp_db, user myapp_app, automated backups

- **chrony**: NTP time synchronization
  - Location/Path: `/etc/chrony/chrony.conf`
  - Port/Socket: `123/udp`
  - Key Config: Multiple time servers, drift correction

- **rsyslog**: System logging
  - Location/Path: `/etc/rsyslog.conf`
  - Port/Socket: `514/udp`
  - Key Config: Centralized logging, log rotation

## File Structure

```
site-modules/role/manifests/app_server.pp
site-modules/profile/manifests/base/base.pp
site-modules/profile/manifests/loadbalancer/haproxy.pp
site-modules/profile/manifests/app/stack.pp
site-modules/profile/manifests/cache/redis.pp
site-modules/base_utils/manifests/init.pp
site-modules/profile_app_stack/manifests/init.pp
site-modules/profile_app_stack/manifests/python.pp
site-modules/profile_app_stack/manifests/database.pp
site-modules/profile_app_stack/manifests/app.pp
site-modules/profile_app_stack/manifests/service.pp
site-modules/profile_app_stack/manifests/monitoring.pp
site-modules/profile_app_stack/templates/logrotate.conf.erb
site-modules/profile_app_stack/templates/app.env.erb
site-modules/profile_app_stack/templates/app.service.epp
site-modules/profile_app_stack/data/common.yaml
site-modules/profile_app_stack/data/environment/production.yaml
site-modules/profile_app_stack/data/environment/staging.yaml
site-modules/profile_app_stack/hiera.yaml
```

## Module Explanation

The module performs operations in this order:

1. **role::app_server** (`site-modules/role/manifests/app_server.pp`):
   - Entry point role class that orchestrates the complete application server stack
   - `contain profile::base::base`
   - `contain profile::loadbalancer::haproxy`
   - `contain profile::app::stack`
   - `contain profile::cache::redis`
   - Sets ordering: `profile::base::base -> profile::loadbalancer::haproxy -> profile::cache::redis -> profile::app::stack`

2. **profile::base::base** (`site-modules/profile/manifests/base/base.pp`):
   - `contain base_utils`
   - `contain profile::base::ntp`
   - `contain profile::base::syslog`
   - Sets ordering: `base_utils -> profile::base::ntp -> profile::base::syslog`

3. **base_utils** (`site-modules/base_utils/manifests/init.pp`):
   - `package 'curl'` → ensure: `present`
   - `package 'wget'` → ensure: `present`
   - `package 'vim'` → ensure: `present`
   - `package 'htop'` → ensure: `present`
   - `package 'git'` → ensure: `present`
   - `service 'ssh'` → ensure: `running`, enable: `true`

4. **profile::base::ntp** (chrony service):
   - `package 'chrony'` → ensure: `present`
   - `file '/etc/chrony/chrony.conf'` → owner: `root`, group: `root`, mode: `0644`
   - `service 'chrony'` → ensure: `running`, enable: `true`

5. **profile::base::syslog** (rsyslog service):
   - `package 'rsyslog'` → ensure: `present`
   - `file '/etc/rsyslog.conf'` → owner: `root`, group: `root`, mode: `0644`
   - `service 'rsyslog'` → ensure: `running`, enable: `true`

6. **profile::loadbalancer::haproxy** (`site-modules/profile/manifests/loadbalancer/haproxy.pp`):
   - `contain profile_haproxy`
   - Manages HAProxy load balancer configuration, SSL certificates, backend health checks

7. **profile::cache::redis** (`site-modules/profile/manifests/cache/redis.pp`):
   - `contain profile_redis_cluster`
   - Manages Redis cluster configuration, persistence, memory management

8. **profile::app::stack** (`site-modules/profile/manifests/app/stack.pp`):
   - `contain profile_app_stack`
   - Wrapper for the Python application stack

9. **profile_app_stack** (`site-modules/profile_app_stack/manifests/init.pp`):
   - Sets class parameters from Hiera: app_name=myapp-api, app_dir=/opt/myapp-api, db_host=localhost (staging) or db-primary.prod.internal (production)
   - `contain profile_app_stack::python`
   - `contain profile_app_stack::database`
   - `contain profile_app_stack::app`
   - `contain profile_app_stack::service`
   - `contain profile_app_stack::monitoring`
   - Sets ordering: `profile_app_stack::python -> profile_app_stack::database -> profile_app_stack::app ~> profile_app_stack::service -> profile_app_stack::monitoring`

10. **profile_app_stack::python** (`site-modules/profile_app_stack/manifests/python.pp`):
    - `package 'python3'` → ensure: `present`
    - `package 'python3-pip'` → ensure: `present`
    - `package 'python3-venv'` → ensure: `present`
    - `package 'python3-dev'` → ensure: `present`
    - `package 'build-essential'` → ensure: `present`
    - `group 'myapp'` → ensure: `present`, gid: `1001`
    - `user 'myapp'` → ensure: `present`, uid: `1001`, gid: `1001`, home: `/opt/myapp-api`, shell: `/bin/bash`, managehome: `true`
    - `file '/var/log/myapp-api'` → ensure: `directory`, owner: `myapp`, group: `myapp`, mode: `0755`
    - `file '/etc/logrotate.d/myapp-api'` (template `site-modules/profile_app_stack/templates/logrotate.conf.erb`) → owner: `root`, group: `root`, mode: `0644`

11. **profile_app_stack::database** (`site-modules/profile_app_stack/manifests/database.pp`):
    - **Conditional**: if db_host == 'localhost' (true in staging, false in production)
      - **When true (staging)**:
        - `contain profile_postgresql`
        - `exec 'create_db_user'` → command: `sudo -u postgres createuser myapp_app`
        - `exec 'create_database'` → command: `sudo -u postgres createdb -O myapp_app myapp_db`
        - `exec 'grant_db_privileges'` → command: `sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE myapp_db TO myapp_app;"`
    - `file '/usr/local/bin/db-backup.sh'` → owner: `root`, group: `root`, mode: `0755`
    - `cron 'database_backup'` → command: `/usr/local/bin/db-backup.sh`, user: `postgres`, hour: `2`, minute: `0`

12. **profile_app_stack::app** (`site-modules/profile_app_stack/manifests/app.pp`):
    - `file '/opt/myapp-api'` → ensure: `directory`, owner: `myapp`, group: `myapp`, mode: `0755`
    - `vcsrepo '/opt/myapp-api'` → ensure: `present`, provider: `git`, source: `https://github.com/example-org/myapp-api.git`, revision: `main` (staging) or `v2.4.1` (production), user: `myapp`
    - `exec 'create_app_venv'` → command: `python3 -m venv /opt/myapp-api/venv`, user: `myapp`, creates: `/opt/myapp-api/venv/bin/python`
    - `exec 'install_requirements'` → command: `/opt/myapp-api/venv/bin/pip install -r requirements.txt`, user: `myapp`, cwd: `/opt/myapp-api`
    - `exec 'install_pip_packages'` → command: `/opt/myapp-api/venv/bin/pip install uvicorn gunicorn psycopg2-binary`, user: `myapp`
    - `file '/opt/myapp-api/.env'` (template `site-modules/profile_app_stack/templates/app.env.erb`) → owner: `myapp`, group: `myapp`, mode: `0600`
    - `file '/usr/local/bin/app-healthcheck.sh'` → owner: `root`, group: `root`, mode: `0755`
    - `exec 'run_db_migrations'` → command: `/opt/myapp-api/venv/bin/python manage.py migrate`, user: `myapp`, cwd: `/opt/myapp-api`

13. **profile_app_stack::service** (`site-modules/profile_app_stack/manifests/service.pp`):
    - `file '/etc/systemd/system/myapp-api.service'` (template `site-modules/profile_app_stack/templates/app.service.epp`) → owner: `root`, group: `root`, mode: `0644`
    - `exec 'systemd_daemon_reload'` → command: `systemctl daemon-reload`, refreshonly: `true`
    - `service 'myapp-api'` → ensure: `running`, enable: `true`

14. **profile_app_stack::monitoring** (`site-modules/profile_app_stack/manifests/monitoring.pp`):
    - `@package 'prometheus-node-exporter'` → ensure: `present` (virtual resource)
    - `@service 'prometheus-node-exporter'` → ensure: `running`, enable: `true` (virtual resource)
    - `@package 'prometheus-pushgateway'` → ensure: `present` (virtual resource)
    - `@cron 'push_app_metrics'` → command: `/usr/local/bin/push-metrics.sh`, user: `myapp`, minute: `*/5` (virtual resource)
    - **Conditional**: if facts['environment'] == 'production' (true in production only)
      - **When true (production)**:
        - Collector `Package <| |>` → realizes prometheus-node-exporter, prometheus-pushgateway
        - Collector `Service <| |>` → realizes prometheus-node-exporter
        - Collector `Cron <| |>` → realizes push_app_metrics
    - `cron 'app_health_check'` → command: `/usr/local/bin/app-healthcheck.sh`, user: `root`, minute: `*/2`

## Variables

**Variable Flow Summary**: 25+ variables across 3 Hiera levels

### Variable Definitions

**common.yaml (defaults)** → Migration note: Base defaults for all nodes
- `profile_app_stack::app_name`: `myapp-api` (type: string)
- `profile_app_stack::app_repo`: `https://github.com/example-org/myapp-api.git` (type: string)
- `profile_app_stack::app_revision`: `main` (type: string)
- `profile_app_stack::app_port`: `8000` (type: integer)
- `profile_app_stack::app_dir`: `/opt/myapp-api` (type: string)
- `profile_app_stack::app_user`: `myapp` (type: string)
- `profile_app_stack::app_group`: `myapp` (type: string)
- `profile_app_stack::python_version`: `python3` (type: string)
- `profile_app_stack::pip_packages`: `[uvicorn, gunicorn, psycopg2-binary]` (type: array)
- `profile_app_stack::db_host`: `localhost` (type: string)
- `profile_app_stack::db_port`: `5432` (type: integer)
- `profile_app_stack::db_name`: `myapp_db` (type: string)
- `profile_app_stack::db_user`: `myapp_app` (type: string)
- `profile_app_stack::db_password`: `ENC[PKCS7,...]` (type: string, encrypted)
- `profile_app_stack::worker_count`: `2` (type: integer)
- `profile_app_stack::worker_class`: `uvicorn.workers.UvicornWorker` (type: string)
- `profile_app_stack::max_requests`: `1000` (type: integer)
- `profile_app_stack::graceful_timeout`: `30` (type: integer)
- `profile_app_stack::log_dir`: `/var/log/myapp-api` (type: string)
- `profile_app_stack::log_level`: `info` (type: string)
- `profile_app_stack::log_max_size`: `100M` (type: string)
- `profile_app_stack::log_rotate_count`: `7` (type: integer)

**environment/production.yaml (production overrides)** → Migration note: Production-specific variables, loaded for production environment
- `profile_app_stack::app_revision`: `v2.4.1` (type: string)
- `profile_app_stack::worker_count`: `8` (type: integer)
- `profile_app_stack::max_requests`: `5000` (type: integer)
- `profile_app_stack::log_level`: `warning` (type: string)
- `profile_app_stack::db_host`: `db-primary.prod.internal` (type: string)
- `profile_app_stack::secret_key`: `ENC[PKCS7,...]` (type: string, encrypted)

**environment/staging.yaml (staging overrides)** → Migration note: Staging-specific variables, loaded for staging environment
- `profile_app_stack::app_revision`: `main` (type: string)
- `profile_app_stack::worker_count`: `1` (type: integer)
- `profile_app_stack::max_requests`: `100` (type: integer)
- `profile_app_stack::log_level`: `debug` (type: string)
- `profile_app_stack::db_host`: `localhost` (type: string)
- `profile_app_stack::secret_key`: `staging-not-secret-at-all` (type: string)

### Variable Migration Summary

- **Common defaults**: 22 variables from common.yaml (base configuration for all nodes)
- **OS-specific variables**: 0 variables that vary by operating system family
- **Environment-specific variables**: 12 variables that vary by deployment environment (6 production, 6 staging)
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
- `puppetlabs-vcsrepo` (version: 6.1.0) - Git repository management
- `puppetlabs-apt` (version: 9.4.0) - APT package management for PostgreSQL repo
- `profile_postgresql` (internal) - PostgreSQL database server
- `profile_haproxy` (internal) - HAProxy load balancer configuration
- `profile_redis_cluster` (internal) - Redis cluster management

**System package dependencies**:
- `curl`, `wget`, `vim`, `htop`, `git` - Base system utilities
- `chrony` - NTP time synchronization
- `rsyslog` - System logging
- `python3`, `python3-pip`, `python3-venv`, `python3-dev`, `build-essential` - Python runtime and development tools
- `postgresql-14`, `postgresql-client-14`, `postgresql-contrib-14`, `libpq-dev` - PostgreSQL database (staging only)
- `prometheus-node-exporter`, `prometheus-pushgateway` - Monitoring tools (production only)

**Service dependencies**:
- Base utilities must be installed before other services
- NTP and syslog services must be running for proper system operation
- HAProxy and Redis must be configured before application deployment
- PostgreSQL service must be running before application service starts (staging)
- Application service depends on database availability
- Monitoring depends on application service being configured

## Puppet Facts Used

- `$facts['environment']` - Determines production vs staging configuration in templates and monitoring
- `$facts['kernel']` - Used by base profile for OS-specific package management
- `$facts['os']['family']` - Used by APT module for Debian/Ubuntu detection

## Template Conversion Notes

**logrotate.conf.erb**:
- Variables: log_dir, log_rotate_count, log_max_size, app_name
- Simple variable substitution, no complex logic

**app.env.erb**:
- Variables: db_url, app_name, app_port, secret_key, log_level, log_dir, worker_count, facts['environment']
- Ruby logic: Conditional block for production vs non-production environment settings (DEBUG, ALLOWED_HOSTS, CORS_ORIGINS)
- Logic block: `<% if @facts['environment'] == 'production' %>`

**app.service.epp**:
- Variables: app_name, app_dir, app_user, app_group, app_port, worker_count, worker_class, max_requests, graceful_timeout, log_dir, log_level
- Ruby logic: Arithmetic expression for TimeoutStopSec calculation
- Logic block: `TimeoutStopSec=<%= $graceful_timeout + 5 %>`

## PuppetDB Dependencies

**Virtual resources**: 4 monitoring-related virtual resources (`@package`, `@service`, `@cron`) that are only realized in production environment via collectors.

**Exported Resources**: None detected in this module.

**Resource Collectors**: 
- `Package <| |>` - Collects all virtual Package resources, realizes prometheus-node-exporter and prometheus-pushgateway packages in production
- `Service <| |>` - Collects all virtual Service resources, realizes prometheus-node-exporter service in production  
- `Cron <| |>` - Collects all virtual Cron resources, realizes push_app_metrics cron job in production

Migration notes: Virtual resource pattern allows conditional realization based on environment facts, requiring careful handling of cross-node resource dependencies.

## Checks for the Migration

**Files to verify**:
- `/opt/myapp-api` (application directory)
- `/opt/myapp-api/.env` (environment configuration)
- `/etc/systemd/system/myapp-api.service` (systemd unit file)
- `/etc/logrotate.d/myapp-api` (log rotation configuration)
- `/usr/local/bin/db-backup.sh` (database backup script)
- `/usr/local/bin/app-healthcheck.sh` (health check script)
- `/var/log/myapp-api/` (log directory)
- `/etc/haproxy/haproxy.cfg` (load balancer configuration)
- `/etc/redis/redis.conf` (cache configuration)
- `/etc/chrony/chrony.conf` (NTP configuration)
- `/etc/rsyslog.conf` (syslog configuration)

**Service endpoints to check**:
- Port 80, 443, 8404 (HAProxy load balancer and stats)
- Port 8000 (myapp-api application HTTP endpoint)
- Port 6379 (Redis cache)
- Port 5432 (PostgreSQL database, staging only)
- Port 123/udp (chrony NTP)
- Port 514/udp (rsyslog)

**Templates rendered**:
- `site-modules/profile_app_stack/templates/logrotate.conf.erb` → `/etc/logrotate.d/myapp-api` (1 render)
- `site-modules/profile_app_stack/templates/app.env.erb` → `/opt/myapp-api/.env` (1 render)
- `site-modules/profile_app_stack/templates/app.service.epp` → `/etc/systemd/system/myapp-api.service` (1 render)

## Pre-flight checks:
```bash
# Base system services
systemctl status ssh
systemctl status chrony
systemctl status rsyslog

# Load balancer service
systemctl status haproxy
curl -I http://localhost:80
curl -s http://localhost:8404/stats

# Cache service
systemctl status redis-server
redis-cli ping

# Database service (staging only)
systemctl status postgresql
sudo -u postgres psql -l

# Application service
systemctl status myapp-api
curl http://localhost:8000/health
python3 --version
/opt/myapp-api/venv/bin/python --version

# Monitoring (production only)
systemctl status prometheus-node-exporter
curl -s http://localhost:9100/metrics | head -5
```