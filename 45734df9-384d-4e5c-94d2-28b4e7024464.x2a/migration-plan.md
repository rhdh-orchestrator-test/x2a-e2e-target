# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with SSL termination, caching services (Memcached and Redis), and a FastAPI application backed by PostgreSQL. The migration to Ansible will modernize the infrastructure-as-code approach while maintaining all existing functionality and security configurations.

**Executive Summary:**
- **Scope**: 3 Chef cookbooks managing web server infrastructure, caching layer, and application deployment
- **Complexity**: Moderate - includes security hardening, SSL certificate management, and multiple service dependencies
- **Estimated Timeline**: 2-3 weeks for complete migration and testing
- **Risk Level**: Medium - hardcoded credentials present, complex nginx template logic, and external cookbook dependencies

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Multi-site Nginx web server with SSL/TLS termination, security hardening (fail2ban, UFW firewall, SSH configuration), sysctl kernel tuning, and per-site configuration for three virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local). Includes self-signed SSL certificate generation, HTTP to HTTPS redirection, security headers (HSTS, CSP, X-Frame-Options), and gzip compression
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: 
  - SSL/TLS with self-signed certificate generation
  - Multi-site configuration via attributes/solo.json
  - Security hardening: fail2ban, UFW firewall (SSH, HTTP, HTTPS only), SSH root login disabled, password authentication disabled
  - Sysctl kernel parameter tuning for security
  - Security headers (HSTS, X-Frame-Options, CSP, X-Content-Type-Options, X-XSS-Protection)
  - HTTP to HTTPS redirection
  - Per-site document roots with static HTML content deployment
  - Nginx sites-available/sites-enabled pattern
  - Custom resource for line-in-file operations
  - Template-driven configuration (nginx.conf, security.conf, site.conf, fail2ban.jail.local, sysctl-security.conf)

**cache**:
- Description: Caching layer services configuration deploying Memcached and Redis with authentication. Redis configured on port 6379 with password protection (requirepass). Includes workaround for Redis configuration file cleanup (removes replica-related directives) and custom log directory setup
- Path: cookbooks/cache
- Technology: Chef
- Key Features:
  - Memcached installation via external cookbook (memcached ~> 6.0)
  - Redis installation via external cookbook (redisio ~> 7.2.4)
  - Redis authentication with hardcoded password in attributes
  - Custom Redis log directory (/var/log/redis) with proper ownership
  - Ruby block hack to clean up Redis configuration file (removes replica-serve-stale-data, replica-read-only, etc.)
  - Redis service enablement via redisio::enable recipe

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend. Clones application from GitHub (dibanez/fastapi_tutorial), sets up Python 3 virtual environment, installs dependencies via pip, provisions PostgreSQL database and user, configures environment variables (.env file), and deploys systemd service for application lifecycle management. Service runs on port 8000 using uvicorn ASGI server
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features:
  - Python 3.x with pip and venv support
  - Git repository cloning (https://github.com/dibanez/fastapi_tutorial.git, main branch)
  - Virtual environment creation and dependency installation
  - PostgreSQL server installation and configuration
  - Database and user provisioning via shell commands (sudo -u postgres psql)
  - Hardcoded database credentials in recipe and .env file
  - Environment file generation (.env) with PROJECT_NAME, API_VERSION, DATABASE_URL
  - Systemd service unit file creation
  - Service runs as root user (security concern)
  - Uvicorn ASGI server on port 8000
  - Service dependencies: network.target, postgresql.service

### Infrastructure Files

- **Berksfile**: Berkshelf dependency management declaring 3 local cookbooks (nginx-multisite, cache, fastapi-tutorial) and 3 external cookbooks from Chef Supermarket (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4). The nginx external cookbook is declared but not actively used (nginx-multisite installs nginx directly via package resource)
- **solo.json**: Chef Solo node attributes defining run list [nginx-multisite, cache, fastapi-tutorial] and configuration data including 3 site definitions with SSL enabled, SSL certificate paths, and security settings (fail2ban, UFW, SSH hardening)
- **solo.rb**: Chef Solo configuration with file cache path, cookbook paths, log level, and log location settings
- **Vagrantfile**: Vagrant configuration for local testing using generic/fedora42 box with libvirt provider (2GB RAM, 2 CPUs), private network (192.168.121.10), port forwarding (80→8080, 443→8443), and rsync folder sync
- **vagrant-provision.sh**: Vagrant shell provisioner that installs Chef, Berkshelf, vendors cookbooks, and runs chef-solo with accept-silent license
- **cookbooks/nginx-multisite/attributes/default.rb**: Default attributes for sites configuration, SSL paths, and security settings (can be overridden by solo.json)
- **cookbooks/nginx-multisite/resources/lineinfile.rb**: Custom Chef resource for line-in-file operations (similar to Ansible lineinfile module)
- **cookbooks/nginx-multisite/files/default/**: Static HTML files for test, ci, and status sites (index.html for each)
- **cookbooks/nginx-multisite/templates/default/**: ERB templates for nginx.conf, security.conf, site.conf, fail2ban.jail.local, and sysctl-security.conf

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ are both supported per metadata.rb, but Vagrantfile uses Fedora 42 for testing. The cookbooks use Debian-style conventions (www-data user, sites-available/sites-enabled, apt-get in provision script), suggesting Ubuntu/Debian is the primary target. **Recommendation: Target Ubuntu 22.04 LTS or RHEL 9 family for migration.**
- **Virtual Machine Technology**: Libvirt/KVM based on Vagrantfile provider configuration (config.vm.provider "libvirt")
- **Cloud Platform**: Not specified - appears to be on-premises or local development environment (no cloud-init, cloud provider tools, or metadata service configurations detected)

## Migration Approach

### Key Dependencies to Address

**External Chef Cookbooks (from Chef Supermarket):**
- **nginx (~> 12.0)**: Declared in Berksfile but not actively used - nginx-multisite installs nginx package directly. Replace with `ansible.builtin.package` module and custom Ansible templates
- **memcached (~> 6.0)**: Used by cache cookbook via `include_recipe 'memcached'`. Replace with `ansible.builtin.package` module or `community.general.memcached` module, or use `geerlingguy.memcached` Ansible Galaxy role
- **redisio (~> 7.2.4)**: Used by cache cookbook for Redis installation and configuration. Replace with `ansible.builtin.package` module for Redis installation plus `community.general.redis` module for configuration, or use `geerlingguy.redis` Ansible Galaxy role

**System Package Dependencies:**
- Python 3, pip, venv, git, PostgreSQL (11+), libpq-dev
- Nginx, OpenSSL, CA certificates
- fail2ban, UFW firewall
- Memcached, Redis server

**Application Dependencies:**
- FastAPI tutorial GitHub repository (https://github.com/dibanez/fastapi_tutorial.git)
- Python requirements.txt from repository
- Uvicorn ASGI server

### Security Considerations

**Secrets Management - CRITICAL:**
- **Redis password**: Hardcoded in `cookbooks/cache/recipes/default.rb` as `requirepass => 'redis_secure_password_123'`
  - **Migration Strategy**: Move to Ansible Vault encrypted variable file (group_vars/all/vault.yml) or external secrets management (HashiCorp Vault, AWS Secrets Manager)
- **PostgreSQL credentials**: Hardcoded in `cookbooks/fastapi-tutorial/recipes/default.rb` as `fastapi:fastapi_password`
  - **Migration Strategy**: Use Ansible Vault for database credentials, implement `ansible.builtin.postgresql_user` and `ansible.builtin.postgresql_db` modules with no_log: true for secure credential handling
- **FastAPI .env file**: Contains hardcoded DATABASE_URL with credentials
  - **Migration Strategy**: Template .env file using Ansible Vault variables with `mode: '0600'` and restricted ownership
- **SSL certificates**: Currently self-signed, generated via openssl commands
  - **Migration Strategy**: Maintain self-signed generation for development, document process for production certificate deployment, or integrate Let's Encrypt via `community.crypto` collection modules (openssl_privatekey, openssl_csr, acme_certificate)
- **SSH hardening**: Root login disabled, password authentication disabled
  - **Migration Strategy**: Use `ansible.builtin.lineinfile` module for sshd_config modifications or `ansible.builtin.template` for full sshd_config management
- **Firewall configuration**: UFW with default deny, allows SSH/HTTP/HTTPS only
  - **Migration Strategy**: Use `community.general.ufw` module to replicate firewall rules

**Service Account Security:**
- **FastAPI service runs as root**: Security concern identified in fastapi-tutorial.service systemd unit
  - **Migration Strategy**: Create dedicated non-privileged service account (e.g., 'fastapi' user), adjust ownership of /opt/fastapi-tutorial, update systemd service User directive

**Credential Types Observed:**
- Database passwords (PostgreSQL): 2 instances (user password, connection string)
- Cache authentication (Redis): 1 instance
- No SSL/TLS certificate private keys hardcoded (generated at runtime)
- No API tokens or cloud credentials detected

### Technical Challenges

**1. Redis Configuration Workaround**
- **Challenge**: The cache cookbook includes a ruby_block that post-processes `/etc/redis/6379.conf` to remove replica-related directives using regex substitution. This suggests the redisio cookbook generates unwanted configuration lines
- **Mitigation Strategy**: 
  - Use `community.general.redis` module or `geerlingguy.redis` role with explicit configuration parameters
  - Alternatively, manage Redis configuration via Ansible template (redis.conf.j2) for full control
  - Test Redis functionality thoroughly to ensure no regression from chef-generated configuration

**2. Multi-Site Nginx Configuration Logic**
- **Challenge**: Complex ERB template logic in site.conf.erb with conditional SSL blocks, security headers, and per-site customization via node attributes hash iteration
- **Mitigation Strategy**: 
  - Convert ERB templates to Jinja2 templates for Ansible
  - Use `ansible.builtin.template` with `with_dict` or `loop` to iterate over site definitions
  - Maintain sites-available/sites-enabled pattern using `ansible.builtin.file` module with state: link
  - Test template rendering with multiple site configurations before deployment

**3. Chef Attribute Precedence vs. Ansible Variables**
- **Challenge**: Chef uses complex attribute precedence (default < normal < override) and allows solo.json to override cookbook attributes. solo.json overrides site document_root paths from attributes/default.rb
- **Mitigation Strategy**: 
  - Design Ansible variable hierarchy: defaults (role defaults) < group_vars < host_vars
  - Document variable override pattern for operators
  - Consider using Ansible inventory variables or group_vars/all.yml as equivalent to solo.json

**4. External Cookbook Vendoring**
- **Challenge**: Berksfile vendors external cookbooks into cookbooks/ directory. The provision script runs `berks vendor cookbooks` which may create conflicts with local cookbooks
- **Mitigation Strategy**: 
  - Replace external Chef cookbooks with Ansible Galaxy roles or custom roles
  - Use `ansible-galaxy install -r requirements.yml` for dependency management
  - No vendoring conflict concerns in Ansible (roles vs. playbooks are separate namespaces)

**5. Git Repository Cloning Idempotency**
- **Challenge**: fastapi-tutorial recipe uses Chef git resource with action :sync. Ansible equivalent must handle repository updates, branch changes, and local modifications
- **Mitigation Strategy**: 
  - Use `ansible.builtin.git` module with `version: main` and `force: yes` for clean checkouts
  - Consider using `update: yes` for production to pull latest changes
  - Add handlers to restart fastapi-tutorial service when repository changes

**6. Database Provisioning with Shell Commands**
- **Challenge**: PostgreSQL database and user creation uses execute resource with raw SQL via sudo -u postgres psql commands, with `|| true` to ignore errors if resources exist
- **Mitigation Strategy**: 
  - Replace with idempotent `ansible.builtin.postgresql_user` and `ansible.builtin.postgresql_db` modules from `community.postgresql` collection
  - Use `state: present` for proper idempotency without error suppression
  - Requires postgresql python library on managed nodes

**7. Systemd Service File Management**
- **Challenge**: fastapi-tutorial creates systemd unit file via file resource with inline content. Changes require daemon-reload and service restart
- **Mitigation Strategy**: 
  - Use `ansible.builtin.template` for systemd unit file with handler for daemon-reload
  - Use `ansible.builtin.systemd` module with `daemon_reload: yes` and `state: restarted` in handlers
  - Consider systemd_service module from community.general for advanced management

### Migration Order

**Phase 1: Foundation (Week 1, Days 1-2)**
1. **nginx-multisite::security** - Low risk, high value
   - Firewall rules (UFW), fail2ban, SSH hardening, sysctl tuning
   - No external dependencies, straightforward translation
   - Creates security baseline before deploying services
   - Estimated effort: 4-6 hours

**Phase 2: Core Services (Week 1, Days 3-5)**
2. **nginx-multisite::nginx, ::ssl, ::sites** - Moderate complexity, critical path
   - Nginx installation, configuration, SSL certificate generation
   - Site configuration with templates and static content
   - Dependencies: Security configuration (firewall rules for 80/443)
   - Estimated effort: 8-12 hours (template conversion requires careful testing)

3. **cache** - Moderate complexity, moderate risk
   - Memcached and Redis installation and configuration
   - External cookbook dependencies to replace
   - Hardcoded Redis password requires Ansible Vault
   - Configuration workaround requires custom template
   - Estimated effort: 6-8 hours

**Phase 3: Application Layer (Week 2)**
4. **fastapi-tutorial** - High complexity, multiple dependencies
   - Depends on: PostgreSQL, Python 3, Git, systemd
   - Requires: Secure credential management, service account creation, database provisioning
   - External GitHub repository dependency
   - Complex systemd service management
   - Estimated effort: 10-12 hours

**Phase 4: Testing and Validation (Week 2-3)**
5. Integration testing across all roles
   - Test multi-site nginx with SSL
   - Verify cache services (memcached, redis) connectivity
   - Validate FastAPI application startup and database connectivity
   - Security validation (firewall rules, SSH hardening, service isolation)
   - Estimated effort: 8-12 hours

**Phase 5: Documentation and Handoff (Week 3)**
6. Operator documentation, runbooks, and variable configuration guides
   - Estimated effort: 4-6 hours

### Assumptions

1. **Operating System Consistency**: Migration will target a single OS family (Ubuntu 22.04 LTS or RHEL 9) rather than maintaining cross-platform support for both Ubuntu and CentOS. The cookbook claims multi-OS support but uses Debian-specific conventions exclusively (www-data user, apt-get commands).

2. **Self-Signed Certificates Acceptable**: The current implementation generates self-signed SSL certificates for development/testing. Migration assumes this pattern continues initially, with production certificate management (Let's Encrypt or commercial CA) implemented as a separate enhancement phase.

3. **Redis Configuration Workaround is Still Required**: The ruby_block hack that removes replica-related configuration from Redis suggests an underlying issue with the redisio cookbook. Assumption is this workaround is still necessary due to specific Redis version or configuration requirements. This needs validation during testing - the workaround may be obsolete with current Redis packages.

4. **External GitHub Repository Availability**: The fastapi-tutorial cookbook clones from https://github.com/dibanez/fastapi_tutorial.git. Migration assumes this repository remains available and the main branch is stable. No local fork or mirroring strategy is currently defined.

5. **Static Site Content Migration**: The nginx-multisite cookbook deploys static HTML files (test/index.html, ci/index.html, status/index.html) from cookbook files. Migration assumes these files will be managed in Ansible files/ directory rather than transitioning to a separate content management or CI/CD pipeline.

6. **Database Schema Management Not in Scope**: The fastapi-tutorial cookbook creates database and user but does not manage schema migrations. Migration assumes the FastAPI application handles its own schema management (e.g., via Alembic), and Ansible is only responsible for database provisioning.

7. **No Existing Secrets Management**: The repository hardcodes all credentials (Redis password, PostgreSQL password). Migration assumes no existing secrets management infrastructure (Vault, AWS Secrets Manager, etc.) is in place, and Ansible Vault will be the initial secrets solution.

8. **Single-Node Deployment**: The Vagrantfile and cookbook configurations suggest single-server deployment. Migration assumes no clustering, load balancing, or high availability requirements initially. Redis replication features are explicitly disabled via the configuration workaround.

9. **Network Configuration is Static**: The nginx-multisite cookbook uses hardcoded site names (test.cluster.local, ci.cluster.local, status.cluster.local) without service discovery or dynamic DNS. Migration assumes static hostname configuration via /etc/hosts or DNS is managed externally.

10. **Berkshelf Vendoring Strategy**: The provision script runs `berks vendor cookbooks` which may overwrite local cookbook directories. It's unclear if this is intentional or a bug. Migration assumes local cookbooks (nginx-multisite, cache, fastapi-tutorial) are the source of truth and external dependencies should be clearly separated in Ansible (roles/ vs. collections/).

11. **Python Virtual Environment Location**: The fastapi-tutorial cookbook creates venv at `/opt/fastapi-tutorial/venv`. Migration assumes this path is acceptable for production and no system-wide Python package installation is required.

12. **Service Restart Strategies**: Chef uses delayed notification for service restarts. Migration assumes Ansible handlers with default behavior (run once at end of play) are acceptable, but this may need adjustment if immediate restarts are required for certain changes.

13. **UFW Firewall is Acceptable**: The security recipe uses UFW for firewall management. Migration assumes UFW is acceptable for the target environment, rather than migrating to firewalld (RHEL/CentOS default) or iptables-direct management.

14. **No Chef Server Dependencies**: The repository uses chef-solo with local cookbooks. Migration assumes no integration with Chef Server, Chef Infra, or Chef Automate is required, and Ansible can operate in masterless mode (ansible-playbook) or with Ansible Tower/AWX.

15. **Log File Locations are Standard**: Nginx logs to `/var/log/nginx/`, Redis to `/var/log/redis/`. Migration assumes these standard locations are acceptable and no centralized logging infrastructure (ELK, Splunk) integration is required initially.

16. **Systemd is Available**: The fastapi-tutorial cookbook creates systemd service units. Migration assumes systemd is the init system on target hosts (true for Ubuntu 18.04+, CentOS 7+, RHEL 7+), not SysV init or upstart.

17. **Root Ownership Acceptable for Application**: Despite identifying the fastapi service running as root as a security concern, migration assumes there are no immediate blockers to temporarily maintaining root ownership if service account creation requires additional approval or testing time.

18. **No Configuration Management Database (CMDB) Integration**: The repository has no hints of external CMDB, inventory systems, or orchestration platforms. Migration assumes Ansible inventory will be manually maintained or generated from simple sources (static INI/YAML files, cloud provider dynamic inventory).

19. **Vagrant is Development-Only**: The Vagrantfile is for local testing. Migration assumes production deployment uses different tooling (Terraform, cloud-init, PXE boot, etc.) and Vagrant configuration does not need Ansible translation.

20. **HTTP to HTTPS Redirect is Universal**: The site.conf.erb template redirects all HTTP traffic to HTTPS. Migration assumes this is desired behavior for all sites and no plain HTTP access is needed (except for redirect).
