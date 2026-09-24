# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI Python application with PostgreSQL backend. The migration involves 3 custom cookbooks with moderate complexity, requiring approximately 4-6 weeks for a complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with multi-site SSL configuration, security hardening via fail2ban/UFW firewall, and SSH security controls
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: SSL-enabled virtual hosts for test/ci/status subdomains, fail2ban intrusion prevention, UFW firewall rules, SSH hardening (root login disabled, password auth disabled), sysctl security tuning

**cache**:
- Description: Caching services layer providing both Redis and Memcached with authentication and custom configuration management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis 6379 with password authentication, Memcached service, custom Redis configuration cleanup via ruby_block, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, systemd service management, and virtual environment setup
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning from GitHub, Python virtual environment creation, PostgreSQL database and user provisioning, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Node configuration with run_list and attribute overrides for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file for local cookbook execution
- `Vagrantfile`: Development environment provisioning for testing cookbook functionality
- `vagrant-provision.sh`: Bootstrap script for Vagrant environment setup

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be platform-agnostic configuration

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached or ansible.builtin.package for memcached installation
- **redisio (~> 7.2.4)**: Replace with community.general.redis or ansible.builtin.template for Redis configuration management
- **External Git Repository**: Replace git resource with ansible.builtin.git module for FastAPI tutorial repository cloning

### Security Considerations

- **Hardcoded Credentials**: Multiple plaintext passwords identified requiring Ansible Vault migration:
  - Redis password: 'redis_secure_password_123' in cache cookbook
  - PostgreSQL password: 'fastapi_password' in fastapi-tutorial cookbook
  - Database connection strings with embedded credentials in .env file
- **SSH Security Configuration**: SSH hardening settings (root login disabled, password auth disabled) need migration to ansible.posix.sshd_config module
- **SSL Certificate Management**: SSL certificate paths defined but certificate provisioning method unclear - requires investigation of certificate deployment strategy
- **Firewall Rules**: UFW firewall configuration needs migration to community.general.ufw module with proper rule ordering
- **Fail2ban Configuration**: Intrusion prevention settings require migration to community.general.fail2ban module

### Technical Challenges

- **Ruby Block Workaround**: The cache cookbook contains a complex ruby_block that manually edits Redis configuration files to remove problematic directives - this Chef-specific workaround needs redesign using Ansible template or lineinfile modules
- **Service Dependencies**: Complex service startup ordering between PostgreSQL, Redis, Memcached, and FastAPI application requires careful Ansible handler and dependency management
- **Multi-Site Nginx Configuration**: Dynamic site generation based on node attributes needs conversion to Ansible loops with template modules
- **PostgreSQL Database Initialization**: Database and user creation using sudo commands needs migration to community.postgresql modules for idempotent database management
- **Systemd Service Management**: Custom systemd service file creation and daemon-reload orchestration requires proper Ansible systemd module usage

### Migration Order

1. **cache** (Priority 1: Standalone caching services, minimal external dependencies)
2. **fastapi-tutorial** (Priority 2: Application layer with database dependencies, moderate complexity)
3. **nginx-multisite** (Priority 3: Front-end proxy with security hardening, highest complexity due to SSL and security configurations)

### Assumptions

- SSL certificates are manually deployed or managed outside of this configuration (certificate files not present in repository)
- The FastAPI tutorial application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and stable during migration
- Target systems have internet connectivity for package installation and git repository access
- Current Chef Solo execution model will be replaced with Ansible playbook execution
- The three-tier architecture (web proxy, application, caching/database) will be maintained in the Ansible implementation
- Security hardening requirements (fail2ban, UFW, SSH restrictions) remain the same in the target environment
- PostgreSQL version compatibility between Chef and Ansible managed installations
- Redis configuration cleanup workaround indicates potential issues with the redisio cookbook that may not exist with native Ansible Redis management