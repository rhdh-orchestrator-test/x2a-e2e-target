# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, configuration templates, and security settings. Based on the complexity and scope, this migration is estimated to require 3-4 weeks with 1-2 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, fail2ban integration, UFW firewall management, security hardening

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file listing cookbook dependencies (nginx, memcached, redisio). Will be replaced by Ansible Galaxy requirements.yml.
- `solo.json`: Chef run list and node attributes configuration. Will be replaced by Ansible inventory variables.
- `solo.rb`: Chef configuration file. Will be replaced by Ansible configuration.
- `Vagrantfile`: VM configuration for development/testing. Can be adapted for Ansible Vagrant provisioner.
- `vagrant-provision.sh`: Shell script for Chef provisioning in Vagrant. Will be replaced by Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ based on cookbook metadata
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or system module
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or community.general.redis module

### Security Considerations

- **Firewall Management**: UFW configuration in nginx-multisite::security recipe needs to be migrated to Ansible's ufw module
- **Fail2ban Configuration**: Convert fail2ban template and service management to Ansible fail2ban role
- **SSH Hardening**: SSH security settings (disable root login, password authentication) should be migrated to Ansible ssh_config module
- **Sysctl Security Settings**: System security parameters need to be migrated to Ansible sysctl module
- **Vault/secrets management**:
  - Redis password in cache cookbook (hardcoded as 'redis_secure_password_123')
  - PostgreSQL database credentials in fastapi-tutorial cookbook (hardcoded as 'fastapi_password')
  - SSL certificate private keys managed in nginx-multisite cookbook
  - Total credentials detected: 3 (Redis password, PostgreSQL user password, SSL private keys)

### Technical Challenges

- **SSL Certificate Generation**: The self-signed certificate generation in nginx-multisite::ssl.rb needs to be converted to Ansible's openssl_* modules
- **Multi-site Configuration**: The dynamic site configuration in nginx-multisite::sites.rb will need careful conversion to Ansible templates and loops
- **Redis Configuration Hack**: The ruby_block "fix_redis_config" in cache/recipes/default.rb will need a custom Ansible solution (lineinfile or template module)
- **PostgreSQL User/DB Creation**: The database setup in fastapi-tutorial cookbook uses direct psql commands that should be replaced with Ansible's postgresql_* modules

### Migration Order

1. **cache cookbook** (Low complexity, foundational service)
   - Implement Memcached and Redis configuration
   - Address Redis configuration hack

2. **nginx-multisite cookbook** (Medium complexity, depends on SSL certificates)
   - Implement basic Nginx installation and configuration
   - Implement security features (fail2ban, firewall)
   - Implement SSL certificate generation
   - Implement virtual host configuration

3. **fastapi-tutorial cookbook** (High complexity, application deployment)
   - Implement PostgreSQL installation and configuration
   - Implement Python environment setup
   - Implement application deployment from Git
   - Implement systemd service configuration

### Assumptions

1. The target environment will continue to be Fedora-based (with support for Ubuntu/CentOS as indicated in metadata)
2. Self-signed certificates are acceptable for development (production would likely use Let's Encrypt or provided certificates)
3. The current security settings (fail2ban, UFW, SSH hardening) are appropriate for the target environment
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current Redis and PostgreSQL passwords are development passwords that will be replaced with Ansible Vault secrets
6. The current directory structure (/opt/server/*, /opt/fastapi-tutorial) should be maintained in the Ansible version
7. The Vagrant development environment should be preserved with similar networking configuration