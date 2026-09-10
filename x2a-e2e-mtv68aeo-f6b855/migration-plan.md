# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI Python application with PostgreSQL backend. The migration involves 3 custom cookbooks with moderate complexity, requiring careful attention to SSL certificate management, security hardening configurations, and database credential handling. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site hosting, security hardening (fail2ban, UFW firewall), and comprehensive HTTP security headers
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: SSL/TLS termination with strong cipher suites, HSTS headers, fail2ban intrusion prevention, UFW firewall rules, SSH hardening, sysctl security tuning, gzip compression

**cache**:
- Description: Caching services configuration providing both Redis and Memcached with authentication and custom Redis configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis 6379 with password authentication, Memcached service, custom Redis configuration patching via ruby_block, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment variable configuration

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Node configuration with run_list and attribute overrides for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file for local cookbook execution
- `Vagrantfile`: Development environment provisioning (requires review for Vagrant-specific configurations)
- `vagrant-provision.sh`: Shell provisioning script for development setup

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached or ansible.builtin.package for memcached installation
- **redisio (~> 7.2.4)**: Replace with community.general.redis or ansible.builtin.template for Redis configuration
- **External cookbook dependencies**: All external Chef Supermarket cookbooks need replacement with equivalent Ansible modules or custom tasks

### Security Considerations

- **SSL Certificate Management**: Current implementation references certificate paths (/etc/ssl/certs, /etc/ssl/private) but doesn't show certificate provisioning - requires investigation of certificate deployment strategy
- **Hardcoded Credentials**: 
  - Redis password "redis_secure_password_123" hardcoded in cache cookbook
  - PostgreSQL credentials "fastapi:fastapi_password" hardcoded in fastapi-tutorial cookbook
  - Database connection string with embedded credentials in .env file
- **SSH Security Configuration**: SSH hardening (root login disable, password auth disable) needs careful migration to avoid lockout
- **Firewall Rules**: UFW firewall configuration requires proper sequencing to avoid connectivity issues during deployment
- **Security Headers**: Comprehensive HTTP security headers in nginx configuration need preservation in Ansible templates

### Technical Challenges

- **Ruby Block Workarounds**: The cache cookbook contains a ruby_block hack to fix Redis configuration files - this custom logic needs reimplementation in Ansible using lineinfile or replace modules
- **Service Dependencies**: Complex service startup dependencies (PostgreSQL before FastAPI, nginx after SSL certificates) require careful Ansible handler and dependency management
- **Template Complexity**: Nginx site template with conditional SSL logic needs conversion to Jinja2 with equivalent conditional rendering
- **Git Repository Management**: FastAPI cookbook clones from GitHub - requires ansible.builtin.git module with proper authentication and update strategies
- **Virtual Environment Management**: Python venv creation and pip dependency installation needs conversion to ansible.builtin.pip with virtualenv parameters

### Migration Order

1. **cache** (low risk, standalone service, clear dependencies)
2. **nginx-multisite** (moderate complexity, security-critical, template conversion required)
3. **fastapi-tutorial** (high complexity, multiple dependencies, database integration, service management)

### Assumptions

- SSL certificates are manually deployed or managed outside of this configuration (no certificate provisioning logic found in cookbooks)
- The target environment has internet access for package installation and git repository cloning
- PostgreSQL installation assumes default package repository versions are acceptable
- UFW firewall rules assume standard SSH (port 22), HTTP (port 80), and HTTPS (port 443) access patterns
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and the main branch is stable
- Current Redis configuration "fixes" in ruby_block are still necessary for the target Redis version
- Development environment (Vagrant) configuration is not part of production migration scope
- Node attribute overrides in solo.json represent the desired production configuration values
- The target environment supports systemd for service management (FastAPI service configuration)