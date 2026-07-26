# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated complexity is moderate, with an estimated timeline of 2-3 weeks for a complete migration.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef configuration data with run list and node attributes
- `solo.rb`: Chef Solo configuration file defining cookbook paths and log settings
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration for development/testing environment using Fedora 42

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development/testing

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role or direct package management
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` role or direct Redis installation and configuration

### Security Considerations

- **SSL Certificate Management**: The current setup generates self-signed certificates. Migration should maintain this capability or integrate with Let's Encrypt for production environments.
- **Firewall Configuration**: UFW firewall rules need to be migrated to equivalent Ansible UFW module tasks.
- **Fail2ban Configuration**: Fail2ban setup needs to be migrated to Ansible tasks.
- **SSH Hardening**: SSH security configurations (disable root login, password authentication) need to be preserved.
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - No Chef Vault or encrypted data bags are used in the current implementation

### Technical Challenges

- **Custom Resource Migration**: The `lineinfile` custom resource in nginx-multisite needs to be replaced with Ansible's native `lineinfile` module.
- **Template Conversion**: Multiple ERB templates need to be converted to Jinja2 format for Ansible.
- **Idempotency**: Ensuring all shell commands and file operations remain idempotent in Ansible.
- **Configuration Hierarchy**: Preserving the attribute precedence and override patterns from Chef in Ansible's variable system.

### Migration Order

1. **nginx-multisite** (Priority 1): Core infrastructure component that other services depend on
   - Break into smaller roles: `nginx-base`, `nginx-ssl`, `nginx-security`, `nginx-sites`
   - Convert templates from ERB to Jinja2
   - Replace custom resources with Ansible modules

2. **cache** (Priority 2): Supporting services with external dependencies
   - Create separate roles for Memcached and Redis
   - Implement secure password management for Redis

3. **fastapi-tutorial** (Priority 3): Application deployment
   - Create roles for Python environment, PostgreSQL, and application deployment
   - Implement secure database credential management

### Assumptions

1. The target environment will continue to be Fedora-based systems (specifically Fedora 42 as indicated in the Vagrantfile).
2. Self-signed certificates are acceptable for the migrated solution, but production deployment may require integration with Let's Encrypt.
3. The current hardcoded credentials will need to be replaced with Ansible Vault or another secrets management solution.
4. The Vagrant development environment will be preserved but updated to use Ansible provisioning instead of Chef.
5. The current directory structure with separate cookbooks will be replaced with Ansible roles with similar separation of concerns.
6. The current security configurations (fail2ban, UFW, SSH hardening) are required in the migrated solution.
7. The FastAPI application deployment will continue to use a Python virtual environment and systemd service.