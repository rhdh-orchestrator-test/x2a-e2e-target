# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration scope is moderate, involving three primary cookbooks with external dependencies. Based on the analysis, we estimate a 2-3 week timeline for complete migration, with the most complex components being the multi-site Nginx configuration and the FastAPI application deployment.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site-specific configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL setup, security hardening (fail2ban, ufw)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Manages cookbook dependencies, including external dependencies from Chef Supermarket (nginx, memcached, redisio). Migration will require mapping these to Ansible Galaxy roles or collections.
- `solo.json`: Contains node configuration including the run list and site-specific configurations. This will be migrated to Ansible inventory variables.
- `solo.rb`: Chef configuration file that sets paths and log levels. Will be replaced by Ansible configuration.
- `Vagrantfile`: Defines the development VM environment. Can be adapted for Ansible testing with minimal changes.
- `vagrant-provision.sh`: Bootstraps Chef in the Vagrant environment. Will need to be replaced with Ansible provisioning script.

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ mentioned in cookbook metadata
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible community.nginx collection or geerlingguy.nginx role
- **memcached (~> 6.0)**: Replace with geerlingguy.memcached role
- **redisio (~> 7.2.4)**: Replace with geerlingguy.redis role or community.redis collection

### Security Considerations

- **SSL Configuration**: The nginx-multisite cookbook manages SSL certificates and private keys. Migration must preserve paths and permissions.
  - Migration approach: Use ansible.posix.file module for directory permissions and ansible-vault for sensitive certificate data
  
- **Redis Authentication**: Redis is configured with password authentication.
  - Migration approach: Use ansible-vault to store the Redis password and reference it in templates

- **Security Hardening**: The configuration includes fail2ban, ufw firewall, and SSH hardening.
  - Migration approach: Use community.general.ufw and community.general.fail2ban modules

- **Vault/secrets management**:
  - Hardcoded credentials found in fastapi-tutorial recipe (PostgreSQL password: 'fastapi_password')
  - Hardcoded credentials found in cache recipe (Redis password: 'redis_secure_password_123')
  - These should be migrated to ansible-vault encrypted variables

### Technical Challenges

- **Multi-site Nginx Configuration**: The nginx-multisite cookbook dynamically creates virtual hosts based on node attributes.
  - Mitigation: Use Ansible templates with loops over host variables to generate similar configuration

- **PostgreSQL User/Database Creation**: The fastapi-tutorial cookbook uses inline shell commands for database setup.
  - Mitigation: Replace with community.postgresql collection modules for idempotent database management

- **Service Management**: Multiple services need to be configured and managed (Nginx, Redis, Memcached, FastAPI application).
  - Mitigation: Use ansible.builtin.systemd module with handlers for service restarts

- **Python Environment Management**: The FastAPI application requires a virtual environment with specific dependencies.
  - Mitigation: Use ansible.builtin.pip module with virtualenv parameter

### Migration Order

1. **cache cookbook** (Low complexity, foundational service)
   - Implement Redis and Memcached configurations
   - Secure Redis with proper password management

2. **nginx-multisite cookbook** (Medium complexity, core infrastructure)
   - Implement base Nginx configuration
   - Configure SSL certificates
   - Set up virtual hosts

3. **fastapi-tutorial cookbook** (High complexity, application layer)
   - Set up PostgreSQL database
   - Deploy application code
   - Configure systemd service

### Assumptions

1. The current Chef setup is functional and represents the desired end state
2. SSL certificates are self-signed for development (based on Vagrant configuration)
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git is accessible and contains the expected code
4. The target environment will continue to be Fedora-based systems
5. No CI/CD pipeline integration is required as part of the migration
6. The current security configurations (fail2ban, ufw, SSH hardening) are sufficient and should be maintained
7. Redis and Memcached configurations don't require clustering or advanced features
8. The PostgreSQL database is local to the application server