# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure that provisions a multi-site nginx web server with SSL, caching services (memcached/Redis), and a FastAPI application with PostgreSQL backend. The migration to Ansible is straightforward with moderate complexity due to external cookbook dependencies and security configurations. **Estimated timeline: 3-4 weeks** for a single engineer, or **2 weeks** for a team of 2-3 engineers working in parallel.

## Module Migration Plan

This repository contains **3 Chef cookbooks** that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server configured with multiple SSL-enabled virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local). Implements comprehensive security hardening with fail2ban intrusion prevention, UFW firewall, SSH hardening, sysctl kernel security parameters, and nginx security headers. Generates self-signed SSL certificates, configures HTTP-to-HTTPS redirects, TLS 1.2/1.3 with strong cipher suites, HSTS, rate limiting, and security-focused nginx configurations. Includes custom fail2ban jails for nginx-specific attack patterns
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site vhost management, self-signed SSL certificate generation, fail2ban with nginx-specific jails, UFW firewall automation, SSH hardening (root login disabled, password auth disabled), sysctl kernel security tuning, comprehensive HTTP security headers (HSTS, CSP, X-Frame-Options), rate limiting zones, TLS 1.2/1.3 configuration

- **cache**:
    - Description: Caching layer implementation using memcached and Redis 6379. Includes Redis authentication with requirepass, custom log directory creation, and configuration workarounds for replica settings. Integrates with community cookbooks 'memcached' (~> 6.0) and 'redisio' (~> 7.2.4) from Chef Supermarket
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Memcached installation via community cookbook, Redis with authentication, custom Redis configuration patching to remove replica-related directives, Redis service enablement, /var/log/redis directory creation with proper ownership

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment from GitHub repository (https://github.com/dibanez/fastapi_tutorial.git). Provisions complete Python 3 environment with virtual environment, installs PostgreSQL database server, creates dedicated database user and schema, configures environment variables via .env file, and deploys as systemd service on port 8000 using uvicorn ASGI server
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python 3 + pip + venv installation, git repository cloning, Python virtual environment management, PostgreSQL server installation and user/database provisioning, systemd service creation for uvicorn, environment variable configuration (.env file), database connection string management

### Infrastructure Files

- `Berksfile`: Berkshelf dependency manager manifest declaring local cookbooks and external dependencies from Chef Supermarket (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4). Migration note: External cookbooks must be replaced with equivalent Ansible Galaxy roles or custom playbooks
- `solo.json`: Chef Solo node attributes defining run list, nginx site configurations (3 SSL-enabled sites), SSL certificate paths, and security policy flags. Migration note: Convert to Ansible group_vars or host_vars YAML files
- `solo.rb`: Chef Solo configuration specifying cookbook paths, cache location, and logging. Migration note: Not needed in Ansible; replaced by ansible.cfg
- `Vagrantfile`: Vagrant VM definition using Fedora 42 base box on libvirt provider with 2 CPU/2GB RAM, rsync folder sync, port forwarding (80→8080, 443→8443), and shell provisioner. Migration note: Update provisioner to use Ansible instead of Chef
- `vagrant-provision.sh`: Bootstrap script installing Chef, Berkshelf, resolving cookbook dependencies, and executing Chef Solo. Migration note: Replace with ansible-playbook execution

### Target Details

Based on the Vagrantfile and cookbook metadata:

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (cookbooks support both); Vagrant test environment uses Fedora 42. For production migration, recommend **Red Hat Enterprise Linux 9** or **Ubuntu 22.04 LTS** as modern stable targets
- **Virtual Machine Technology**: Libvirt/KVM (configured in Vagrantfile with 2 CPUs, 2048 MB RAM, rsync synced folders)
- **Cloud Platform**: Not specified; current configuration is VM-based for development/testing with local networking (192.168.121.10 private network)

## Migration Approach

### Key Dependencies to Address

External Chef cookbooks from Supermarket must be replaced with Ansible equivalents:

- **nginx (~> 12.0)**: Replace with `geerlingguy.nginx` Ansible Galaxy role or custom nginx playbook using apt/yum modules. The existing cookbook is not actually used in recipes (only declared in Berksfile but not included), so migration is simpler — implement nginx installation directly
- **memcached (~> 6.0)**: Replace with `geerlingguy.memcached` Ansible Galaxy role or use `ansible.builtin.package` + `ansible.builtin.service` modules for simple memcached installation
- **redisio (~> 7.2.4)**: Replace with `geerlingguy.redis` Ansible Galaxy role or `ansible.builtin.package` + `ansible.builtin.template` for redis.conf. Note: Current Chef recipe uses 'redisio' cookbook and applies post-configuration patching to remove replica directives — Ansible version should avoid this hack by templating redis.conf correctly from the start

### Security Considerations

This infrastructure has extensive security hardening that must be preserved during migration:

- **Fail2ban Configuration**: Custom nginx-specific jails (nginx-http-auth, nginx-limit-req, nginx-botsearch) with 3600s ban times. Migration: Use `ansible.builtin.template` or community.general.ini_file module to deploy /etc/fail2ban/jail.local
- **UFW Firewall**: Default deny policy with explicit allow rules for SSH (22), HTTP (80), HTTPS (443). Migration: Use community.general.ufw Ansible module to replicate firewall rules in idempotent manner
- **SSH Hardening**: Root login disabled (`PermitRootLogin no`), password authentication disabled (`PasswordAuthentication no`). Migration: Use ansible.builtin.lineinfile to modify /etc/ssh/sshd_config or leverage community.general.ssh_config module
- **Sysctl Kernel Tuning**: 20+ kernel parameters for IP spoofing protection, ICMP hardening, SYN flood protection, IPv6 disabling. Migration: Use ansible.posix.sysctl module to set parameters idempotently
- **Nginx Security Headers**: HSTS, CSP, X-Frame-Options, X-Content-Type-Options, X-XSS-Protection in site templates. Migration: Preserve in Jinja2 templates for vhost configuration
- **SSL/TLS Configuration**: TLS 1.2/1.3 only, strong cipher suites (ECDHE-RSA-AES256-GCM-SHA512, etc.), self-signed certificate generation. Migration: Use community.crypto.openssl_certificate and community.crypto.openssl_privatekey modules for certificate generation
- **Vault/secrets management**: 
  - **Hardcoded credentials identified** in cache cookbook: Redis requirepass 'redis_secure_password_123' (cookbooks/cache/recipes/default.rb)
  - **Hardcoded credentials identified** in fastapi-tutorial cookbook: PostgreSQL user password 'fastapi_password' and database connection string (cookbooks/fastapi-tutorial/recipes/default.rb)
  - **Recommendation**: Migrate these to Ansible Vault encrypted variables. Create vault files for each environment (dev/staging/production) containing encrypted credentials. Use `{{ vault_redis_password }}` and `{{ vault_postgres_password }}` variables in playbooks

### Technical Challenges

1. **Berkshelf Dependency Resolution**: Chef uses Berkshelf to vendor external cookbooks. Ansible approach: Replace with `ansible-galaxy install -r requirements.yml` workflow. Create requirements.yml listing Galaxy roles for nginx, memcached, and redis

2. **Ruby ERB vs Jinja2 Templates**: Chef uses ERB templating syntax (`<%= @variable %>`). Ansible uses Jinja2 (`{{ variable }}`). Migration: Convert all 5 ERB templates (nginx.conf, site.conf, security.conf, fail2ban.jail.local, sysctl-security.conf) to Jinja2 syntax. This is mechanical but requires careful testing of conditionals and loops

3. **Chef Notifies vs Ansible Handlers**: Chef uses `notifies :reload, 'service[nginx]', :delayed` to trigger service restarts. Ansible equivalent: Define handlers in playbooks and use `notify: reload nginx` in tasks. Ensure handler names are consistent across roles

4. **Redis Configuration Hack**: cache cookbook applies post-install configuration patching using ruby_block to remove replica-related directives from /etc/redis/6379.conf. Root cause: redisio cookbook generates unwanted configuration. Ansible solution: Template redis.conf directly using Jinja2 without post-processing hacks, or use geerlingguy.redis role with proper variable configuration to avoid generating replica settings

5. **Chef execute vs Ansible command/shell**: Multiple cookbooks use Chef `execute` resources for one-time operations (ufw commands, PostgreSQL user creation, SSL certificate generation). Ansible equivalent: Use `ansible.builtin.command` or `ansible.builtin.shell` with `creates` parameter or conditional `when` clauses to ensure idempotency. Example: `creates: /etc/ssl/certs/test.cluster.local.crt` for SSL generation

6. **Node Attributes vs Ansible Variables**: Chef node attributes in solo.json and attributes/default.rb define site configurations. Migration: Convert to Ansible variables in group_vars/all.yml or host_vars files. Structure: Use dictionaries for multi-site configuration (nginx_sites dict with keys for each vhost)

7. **Git Repository Cloning**: fastapi-tutorial uses Chef git resource with `action :sync` to clone/update repository. Ansible equivalent: Use `ansible.builtin.git` module with `version: main` and `update: yes` parameters

8. **PostgreSQL User/Database Creation**: Chef uses inline shell commands with `sudo -u postgres psql`. Ansible solution: Use community.postgresql collection (community.postgresql.postgresql_db, community.postgresql.postgresql_user) for idempotent database operations. Requires postgresql Python library on managed nodes

9. **Self-Signed Certificate Generation**: ssl.rb recipe generates certificates using openssl command. Ansible solution: Use community.crypto.x509_certificate and community.crypto.openssl_privatekey modules from community.crypto collection for certificate lifecycle management

### Migration Order

Recommend the following migration sequence based on dependencies and risk:

1. **nginx-multisite** (Week 1, Priority 1 - Foundation)
   - Start with this as it has no dependencies on other cookbooks and provides the core web serving infrastructure
   - Break into sub-tasks: nginx installation → SSL certificate generation → site configuration → security hardening (fail2ban, UFW, sysctl, SSH)
   - Deliverable: Ansible role 'nginx_multisite' with all security features functional
   - Testing: Verify all 3 vhosts respond on HTTPS, HTTP redirects work, fail2ban jails active, firewall rules applied

2. **cache** (Week 2, Priority 2 - Moderate complexity)
   - Depends on external cookbooks but has no internal dependencies
   - Integrate geerlingguy.memcached and geerlingguy.redis roles or create custom playbook
   - Focus on eliminating the Redis configuration hack by proper templating
   - Deliverable: Ansible role 'cache_services' installing memcached and Redis with authentication
   - Testing: Verify memcached listens on default port, Redis accepts authenticated connections on 6379

3. **fastapi-tutorial** (Week 3, Priority 3 - Highest complexity)
   - Most complex due to Python virtual environment, git operations, PostgreSQL provisioning, systemd service management
   - Requires community.postgresql collection and testing of database creation idempotency
   - Consider using community.general.python_requirements_info for pip dependency management
   - Deliverable: Ansible role 'fastapi_app' deploying application with PostgreSQL backend
   - Testing: Verify systemd service starts, application responds on port 8000, database connectivity works

4. **Integration Testing** (Week 4, Validation and Documentation)
   - Update Vagrantfile to use Ansible provisioner instead of Chef
   - Create site.yml playbook orchestrating all roles in correct order
   - Test complete stack provisioning on clean VM
   - Document variable overrides, vault usage, and operational procedures
   - Deliverable: Complete playbook repository with README, requirements.yml, and migration notes

### Assumptions

1. **Target OS Decision Required**: Cookbooks support both Ubuntu 18.04+ and CentOS 7+, but production target OS is not specified. Ansible playbooks should maintain multi-OS support using `ansible_os_family` conditionals for package manager selection (apt vs yum) and service names. Alternatively, if target OS is known, playbooks can be simplified for single platform

2. **External Cookbook Versions**: Berksfile specifies version constraints (~> 12.0 for nginx, ~> 6.0 for memcached, ~> 7.2.4 for redisio) but actual resolved versions are unknown without Berksfile.lock. Assume latest compatible versions were used. Ansible Galaxy role versions should be pinned in requirements.yml after testing for reproducibility

3. **SSL Certificate Strategy**: Current implementation generates self-signed certificates for development. Production migration assumption: Certificates will either continue as self-signed for internal use, or migration plan should include Let's Encrypt integration using community.crypto.acme_certificate module for public-facing environments. Clarification needed on production certificate management strategy

4. **Secrets Management Current State**: While hardcoded passwords are visible in cookbooks, unclear if production deployments override these via Chef encrypted data bags or external secret stores. Migration approach assumes all secrets will be migrated to Ansible Vault, but actual production credential storage mechanism should be documented

5. **FastAPI Application Source Stability**: fastapi-tutorial clones from GitHub main branch without version pinning (`revision 'main'`). Assumption: This is acceptable for development, but production should pin to specific commit SHA or tag for reproducibility. Ansible migration should add variable for git revision with default to main

6. **Redis Replica Configuration Issue**: Cache cookbook applies configuration hack to remove replica-related directives. Root cause unclear — possibly redisio cookbook bug or misconfiguration. Assumption: Redis is intended as standalone instance (no replication). If replication is needed in future, proper master/replica configuration should be designed in Ansible rather than patching config files

7. **PostgreSQL Version**: fastapi-tutorial installs 'postgresql' package without version specification, defaulting to distribution default version (varies by OS). Assumption: Default PostgreSQL version is acceptable. If specific version required (e.g., PostgreSQL 14), playbooks should use PostgreSQL official repositories and specify version explicitly

8. **Network Configuration**: Vagrantfile uses 192.168.121.10 private network IP and localhost port forwarding. Assumption: Production deployment will have different networking (likely cloud or datacenter IPs). Ansible inventory should use variable substitution for IPs rather than hardcoding test network addresses

9. **Service Dependencies**: fastapi-tutorial systemd service depends on postgresql.service. Assumption: All services (nginx, memcached, redis, postgresql, fastapi-tutorial) run on same host. If future architecture requires service distribution across multiple hosts, playbooks should be refactored into separate host groups with appropriate service dependencies

10. **UFW Default Policy**: Security recipe sets UFW default deny and enables firewall. Assumption: Ansible control node has access via allowed SSH port before UFW activation. Migration should ensure SSH access is explicitly allowed before enabling firewall to avoid lockout. Consider using ansible_port variable for non-standard SSH ports

11. **Fail2ban Filter Availability**: fail2ban.jail.local references standard filter names (nginx-http-auth, nginx-limit-req, nginx-botsearch). Assumption: These filters exist in default fail2ban installation. Some filters may need custom definition — verify filter availability on target OS version during testing phase

12. **Python Version for FastAPI**: Recipe installs 'python3' without specifying minor version. FastAPI requirements may dictate minimum Python version (e.g., 3.7+). Assumption: Distribution default python3 meets application requirements. If specific Python version needed, consider using deadsnakes PPA (Ubuntu) or SCL (RHEL) in Ansible playbook

13. **Static Site Content**: nginx-multisite deploys static HTML files from cookbooks/nginx-multisite/files/default/{ci,test,status}/index.html. Migration assumption: These files will be included in Ansible role files/ directory and deployed via ansible.builtin.copy module. Verify if these are placeholder files or production content

14. **Chef Solo vs Chef Server**: Repository uses Chef Solo (solo.json, solo.rb) indicating standalone deployment without Chef Server. Migration benefit: Ansible's agentless architecture is similar to Chef Solo model — no server infrastructure needed. Ansible pull mode could replicate Chef Solo workflow if needed for specific use cases

15. **Log Retention and Rotation**: Nginx access/error logs and fail2ban logs will accumulate without rotation. Assumption: Log rotation is handled by system defaults (logrotate.d). Ansible migration should verify logrotate configuration exists for nginx and fail2ban, or add custom logrotate.d templates if needed
