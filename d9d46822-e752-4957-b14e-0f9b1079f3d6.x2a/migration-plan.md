# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and a multi-site nginx web server with SSL and security hardening. The migration involves converting Chef cookbooks to Ansible playbooks and roles, addressing external cookbook dependencies, and migrating configuration management patterns. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached installation via external cookbook, Redis with password authentication, custom log directory creation, configuration file manipulation via Ruby block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment creation, PostgreSQL database and user provisioning, systemd service configuration, environment file management

**nginx-multisite**:
- Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening via fail2ban and UFW firewall, and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site configuration with SSL termination, fail2ban intrusion prevention, UFW firewall rules, SSH hardening, sysctl security tuning, self-signed certificate generation

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management - defines external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo node configuration - contains run list and attribute overrides for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file - likely contains cookbook paths and other Chef Solo settings
- `Vagrantfile`: Vagrant development environment configuration - provides local testing environment setup
- `vagrant-provision.sh`: Vagrant provisioning script - automates Chef Solo execution in development environment

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be generic Linux deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx installation and configuration
- **memcached (~> 6.0)**: Replace with ansible.builtin.package for memcached installation and ansible.builtin.service for management
- **redisio (~> 7.2.4)**: Replace with ansible.builtin.package for Redis installation, ansible.builtin.template for configuration, and ansible.builtin.service for management

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - consider using ansible.builtin.openssl_* modules or community.crypto collection
- **SSH hardening**: Root login disable and password authentication disable configured via sed commands - migrate to ansible.builtin.lineinfile module
- **Firewall configuration**: UFW rules managed via execute resources - migrate to community.general.ufw module
- **Fail2ban configuration**: Template-based jail configuration - migrate to ansible.builtin.template with Jinja2 templates
- **Credential types identified**: Database passwords (2), Redis authentication (1), SSL certificate generation (3 sites)

### Technical Challenges

- **Ruby block configuration manipulation**: The cache cookbook uses Ruby blocks to modify Redis configuration files post-installation - requires conversion to Ansible lineinfile or replace modules with proper regex patterns
- **Complex service dependencies**: FastAPI service depends on PostgreSQL being ready and database/user creation - requires proper Ansible task ordering and handlers
- **Multi-site SSL certificate generation**: Dynamic certificate generation for multiple sites based on attributes - requires Ansible loops and conditional logic
- **External cookbook dependencies**: Three external cookbooks need replacement with equivalent Ansible modules or community collections
- **Chef Solo to Ansible conversion**: Node attributes and run lists need conversion to Ansible inventory variables and playbook structure

### Migration Order

1. **cache** (low risk, moderate complexity) - Straightforward package installation with configuration file management challenges
2. **fastapi-tutorial** (moderate complexity) - Application deployment with database dependencies but well-defined service boundaries  
3. **nginx-multisite** (high complexity, multiple dependencies) - Complex multi-site configuration with SSL, security hardening, and firewall management

### Assumptions

- Target environments will maintain the same OS support matrix (Ubuntu 18.04+, CentOS 7+)
- Self-signed certificates are acceptable for the target environment (production may require CA-signed certificates)
- Current hardcoded passwords are acceptable for migration (should be moved to Ansible Vault post-migration)
- PostgreSQL and Redis service management patterns will remain similar to current Chef implementation
- UFW firewall is the preferred firewall solution for the target environment
- Systemd is available on target systems for service management
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible
- Current nginx site configuration patterns (test.cluster.local, ci.cluster.local, status.cluster.local) will be maintained
- Development environment will transition from Vagrant/Chef Solo to Ansible playbooks with molecule or similar testing framework