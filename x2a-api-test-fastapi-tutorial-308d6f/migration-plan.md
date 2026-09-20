# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and a multi-site nginx reverse proxy with SSL termination. The migration involves converting Chef cookbooks to Ansible playbooks and roles, addressing external dependencies, and implementing security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication, logging, and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication, custom log directory creation, configuration file patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv creation, PostgreSQL database and user provisioning, systemd service management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening, and fail2ban integration
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx, memcached, redisio)
- `solo.json`: Chef Solo run list and node attributes configuration with site-specific settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning (likely for testing)
- `vagrant-provision.sh`: Shell script for Vagrant environment setup

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached or custom Ansible tasks for memcached installation and configuration
- **redisio (~> 7.2.4)**: Replace with community.general.redis or ansible.builtin.package with custom configuration templates

### Security Considerations

- **Hardcoded Credentials**: Multiple instances requiring Ansible Vault migration:
  - Redis password: `redis_secure_password_123` in cache cookbook
  - PostgreSQL credentials: `fastapi:fastapi_password` in fastapi-tutorial cookbook
  - Database connection strings with embedded passwords in environment files
- **SSL Certificate Management**: Self-signed certificate generation needs migration to ansible.builtin.openssl_* modules
- **SSH Hardening**: Root login disable and password authentication disable configurations
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH access
- **Fail2ban Integration**: Jail configuration templates for intrusion prevention

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook contains complex ruby_block logic for Redis configuration file manipulation that needs conversion to Ansible lineinfile or replace modules
- **Service Dependencies**: Complex service ordering between PostgreSQL, nginx, and application services requires careful Ansible handler and dependency management
- **Multi-site SSL**: Dynamic SSL certificate generation for multiple sites needs conversion to Ansible loops with openssl modules
- **Git Repository Management**: FastAPI application deployment via git clone needs migration to ansible.builtin.git module with proper change detection

### Migration Order

1. **cache** (moderate complexity, standalone caching services)
2. **nginx-multisite** (high complexity due to SSL and security configurations, but foundational)
3. **fastapi-tutorial** (highest complexity due to application deployment, database setup, and service management dependencies)

### Assumptions

- Target environments will maintain the same OS support matrix (Ubuntu 18.04+, CentOS 7+)
- Self-signed certificates are acceptable for the target environment (production may require Let's Encrypt or CA-signed certificates)
- PostgreSQL and Redis will continue to run on the same hosts as the applications
- The FastAPI tutorial application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and stable
- Current Chef Solo deployment model will be replaced with Ansible playbook execution
- Vagrant development environment will be maintained for testing migrated Ansible configurations
- Network topology and firewall requirements remain unchanged (ports 22, 80, 443)
- Service user accounts (www-data, redis, postgres) will be managed consistently across platforms