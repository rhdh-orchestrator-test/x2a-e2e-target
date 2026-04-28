# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks, handling external dependencies, and ensuring proper security configurations are maintained.

**Scope**: 3 Chef cookbooks with dependencies on external cookbooks
**Complexity**: Medium (standard web stack with some security hardening)
**Timeline Estimate**: 3-4 weeks (1 week per cookbook + 1 week for testing and documentation)

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, fail2ban integration, UFW firewall configuration

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

- `Berksfile`: Dependency management file listing cookbook dependencies (nginx, memcached, redisio)
- `solo.json`: Chef configuration file with run list and node attributes
- `solo.rb`: Chef configuration file for Chef Solo
- `vagrant-provision.sh`: Provisioning script for Vagrant environment
- `Vagrantfile`: Vagrant configuration for development environment using Fedora 42

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development/testing

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated in the nginx-multisite cookbook
  - Migration should use Ansible's openssl_* modules for certificate generation
  - Consider integrating with Ansible Vault for private key storage

- **Firewall Configuration**: 
  - UFW configuration in security.rb should be migrated to Ansible's ufw module
  - Maintain the same allowed ports (SSH, HTTP, HTTPS)

- **System Hardening**:
  - sysctl security configurations should be migrated using Ansible's sysctl module
  - SSH hardening (disable root login, password authentication) should be maintained

- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL credentials in fastapi-tutorial cookbook: User "fastapi" with password "fastapi_password"
  - Consider using Ansible Vault to secure these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - The dynamic generation of multiple virtual hosts based on node attributes will need careful translation to Ansible templates
  - Solution: Use Ansible's with_items/loop constructs with templates

- **SSL Certificate Generation**: 
  - Self-signed certificate generation logic needs to be preserved
  - Solution: Use Ansible's openssl_certificate module with similar parameters

- **Service Dependencies**: 
  - The FastAPI application depends on PostgreSQL being configured first
  - Solution: Use Ansible's meta: dependencies or explicit ordering with tags/handlers

- **Idempotent Database Creation**: 
  - The current Chef recipe uses "|| true" to make PostgreSQL user/database creation idempotent
  - Solution: Use Ansible's postgresql_* modules which are inherently idempotent

### Migration Order

1. **nginx-multisite cookbook** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security configurations that should be established first

2. **cache cookbook** (Priority 2)
   - Supporting services that the application may depend on
   - Relatively simple configuration with external dependencies

3. **fastapi-tutorial cookbook** (Priority 3)
   - Application deployment that depends on the infrastructure being in place
   - More complex with database setup, Python environment, and service configuration

### Assumptions

1. The target environment will continue to be Fedora-based systems (Fedora 42 as specified in Vagrantfile)
2. Self-signed certificates are acceptable for the migrated solution (production would likely require proper certificates)
3. The security requirements (fail2ban, UFW, SSH hardening) will remain the same
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current passwords in the Chef recipes are development passwords and will be replaced with proper secrets management
6. The Vagrant development environment will be maintained but converted to use Ansible provisioner instead of Chef
7. No custom Chef resources are being used that would require special handling (all standard Chef resources)