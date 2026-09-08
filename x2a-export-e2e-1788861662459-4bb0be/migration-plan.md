# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to external dependencies and security configurations. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with multi-site SSL configuration, security hardening via fail2ban/UFW, and system-level security controls including SSH hardening and sysctl tuning
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: SSL-enabled virtual hosts for test/ci/status subdomains, fail2ban jail configuration, UFW firewall rules, SSH security hardening, sysctl security parameters

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached service setup, Redis with password authentication, custom Redis configuration cleanup via ruby_block, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment creation, PostgreSQL database and user provisioning, systemd service configuration, environment file management

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook paths
- `solo.json`: Chef Solo configuration with run_list and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file (likely contains cookbook paths and other Chef settings)
- `Vagrantfile`: Development environment provisioning configuration
- `vagrant-provision.sh`: Shell script for Vagrant environment setup

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (based on Vagrantfile presence)
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom configuration tasks

### Security Considerations
- SSH hardening configurations: Root login disabled, password authentication disabled - migrate using ansible.posix.sshd_config module
- Firewall management: UFW rules for SSH, HTTP, HTTPS - migrate using community.general.ufw module
- Fail2ban configuration: Custom jail.local template - migrate using ansible.builtin.template module
- Sysctl security parameters: Custom security.conf template - migrate using ansible.posix.sysctl module
- Vault/secrets management: Hardcoded credentials identified:
  - Redis password: 'redis_secure_password_123' in cache cookbook
  - PostgreSQL password: 'fastapi_password' in fastapi-tutorial cookbook
  - Database connection string with embedded credentials in .env file
  - SSL certificate paths referenced but certificates not managed in code

### Technical Challenges
- **Ruby block configuration fixes**: The cache cookbook uses a ruby_block to manually edit Redis configuration files - this will need to be replaced with Ansible lineinfile or template modules with proper configuration management
- **Git repository management**: FastAPI cookbook clones from GitHub - ensure Ansible git module handles repository updates and authentication properly
- **Service dependencies**: PostgreSQL must be running before FastAPI application starts - implement proper task ordering and handlers in Ansible
- **Template variable mapping**: Chef ERB templates need conversion to Jinja2 with attribute mapping from Chef node attributes to Ansible variables

### Migration Order
1. **cache** (low risk, standalone caching services with clear external dependencies)
2. **nginx-multisite** (moderate complexity, security configurations but well-defined scope)
3. **fastapi-tutorial** (high complexity, application deployment with database dependencies and service management)

### Assumptions
- SSL certificates are managed externally and only paths are configured in the cookbooks
- The Vagrant environment is used for development/testing and production deployment method is not specified
- External cookbook dependencies (nginx, memcached, redisio) provide standard configurations that can be replaced with equivalent Ansible modules
- The ruby_block hack in the Redis configuration suggests potential issues with the redisio cookbook that may not exist with direct Ansible Redis management
- Database initialization scripts and schema management are handled by the FastAPI application itself, not by Chef
- The three sites (test.cluster.local, ci.cluster.local, status.cluster.local) serve static content and don't require complex application server configuration