# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, configuration templates, and security settings.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- Security configurations are comprehensive and will require careful migration
- External dependencies on community cookbooks will need Ansible equivalents

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW, sysctl security settings

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `Vagrantfile`: Defines a Fedora 42 VM for development/testing with port forwarding and networking
- `solo.json`: Chef configuration file with run list and node attributes
- `solo.rb`: Chef configuration file with paths and log settings
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be designed for local development with potential for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or DavidWittman.redis

### Security Considerations

- **Firewall Configuration**: The UFW firewall configuration in nginx-multisite::security.rb needs to be migrated to Ansible's ufw module
- **fail2ban Setup**: The fail2ban configuration needs to be migrated using Ansible's template module
- **SSH Hardening**: SSH security settings (disable root login, password authentication) need to be migrated using Ansible's lineinfile or template module
- **SSL Certificate Management**: Self-signed certificate generation needs to be migrated using Ansible's openssl_* modules
- **Vault/secrets management**:
  - Redis password in cache/recipes/default.rb (hardcoded as 'redis_secure_password_123')
  - PostgreSQL database credentials in fastapi-tutorial/recipes/default.rb (hardcoded as 'fastapi_password')
  - These should be migrated to Ansible Vault for secure storage

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of Nginx site configurations based on node attributes will need to be carefully migrated to Ansible's template system
- **SSL Certificate Generation**: The self-signed certificate generation logic will need to be converted to use Ansible's openssl_certificate module
- **PostgreSQL User/Database Creation**: The PostgreSQL setup using shell commands should be replaced with Ansible's postgresql_* modules for better idempotency
- **Redis Configuration Hack**: The ruby_block that modifies Redis configuration will need a cleaner implementation in Ansible

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Then add SSL and security features
   - Finally implement multi-site configuration

2. **cache** (Priority 2)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper integration with Nginx

3. **fastapi-tutorial** (Priority 3)
   - Set up PostgreSQL database
   - Deploy Python application with virtual environment
   - Configure systemd service
   - Integrate with Nginx and caching services

### Assumptions

1. The target environment will continue to be Fedora-based systems
2. The self-signed certificates are for development only and may be replaced with proper certificates in production
3. The current security configurations (fail2ban, UFW, SSH hardening) are appropriate for the target environment
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current directory structure in /opt/ and /var/ can be maintained in the target environment
6. The current Redis and Memcached configurations are sufficient for the application's needs
7. The current PostgreSQL user/database setup meets the application's requirements
8. The Nginx sites configuration (test.cluster.local, ci.cluster.local, status.cluster.local) will remain the same