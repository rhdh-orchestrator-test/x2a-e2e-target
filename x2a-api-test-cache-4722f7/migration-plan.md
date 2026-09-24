# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI Python application with PostgreSQL backend. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with SSL-enabled multi-site hosting, security hardening via fail2ban/UFW firewall, and system-level security configurations
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-domain SSL sites (test/ci/status.cluster.local), fail2ban intrusion prevention, UFW firewall rules, SSH hardening, sysctl security tuning

**cache**:
- Description: Caching services layer providing both Redis and Memcached with authentication and custom configuration management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, custom log directory setup, configuration file patching via ruby_block, Memcached integration

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service integration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv setup, PostgreSQL database/user creation, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run_list and node attributes for site configuration and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning (likely for testing)
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and template-based configuration
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks

### Security Considerations
- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are embedded in recipes - migrate to Ansible Vault
- **SSL certificate management**: SSL paths defined but certificate provisioning not visible - requires certificate deployment strategy
- **SSH hardening**: Root login disabled, password authentication disabled - preserve in Ansible with lineinfile module
- **Firewall configuration**: UFW rules for SSH/HTTP/HTTPS - migrate to community.general.ufw module
- **System security**: sysctl security parameters - migrate to ansible.posix.sysctl module
- **Fail2ban configuration**: Intrusion prevention with custom jail.local - migrate to template-based configuration

### Technical Challenges
- **Ruby block configuration patching**: The cache cookbook uses ruby_block to modify Redis config files post-installation - requires conversion to Ansible lineinfile or replace modules
- **Multi-service coordination**: Services have interdependencies (nginx depends on sites, FastAPI depends on PostgreSQL) - requires careful task ordering and handlers
- **Git repository management**: FastAPI cookbook clones from GitHub - migrate to ansible.builtin.git module with proper idempotency
- **Template migration**: ERB templates (.erb files) need conversion to Jinja2 format for nginx.conf, security.conf, and fail2ban configurations
- **Package management differences**: Chef uses package resource, Ansible requires platform-specific package modules

### Migration Order
1. **cache** (low risk, foundational service with clear dependencies)
2. **fastapi-tutorial** (moderate complexity, database setup, but isolated application)
3. **nginx-multisite** (highest complexity due to SSL, security hardening, and multi-site configuration)

### Assumptions
- SSL certificates are managed externally or will be provided via Let's Encrypt/manual process (certificate generation not visible in current cookbooks)
- The target environment will maintain the same OS support matrix (Ubuntu 18.04+, CentOS 7+)
- External cookbook dependencies (nginx, memcached, redisio) functionality will be replicated using native Ansible modules rather than community cookbooks
- The Vagrant development environment will be preserved or replaced with molecule for testing
- Database initialization scripts and application deployment processes are handled by the FastAPI application itself
- The cluster.local domain configuration suggests a local/private network deployment rather than public internet
- Current Chef Solo execution model will migrate to standard Ansible playbook execution
- System service management (systemd) approach will remain consistent between Chef and Ansible implementations