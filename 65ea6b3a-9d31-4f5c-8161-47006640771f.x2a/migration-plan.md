# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated complexity is medium, with an estimated timeline of 3-4 weeks for a complete migration.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and proper SSL configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, fail2ban integration, UFW firewall configuration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, service management

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external cookbook dependencies
- `solo.json`: Chef configuration file defining the run list and node attributes
- `solo.rb`: Chef configuration file defining paths and log settings
- `Vagrantfile`: Defines the development VM configuration using Fedora 42
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile) with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Ansible role
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or `DavidWittman.redis`

### Security Considerations

- **SSL Certificate Management**: 
  - Current approach uses self-signed certificates generated with OpenSSL
  - Migration approach: Use Ansible's `openssl_*` modules or `community.crypto` collection

- **Firewall Configuration**: 
  - Current approach uses UFW with specific allow rules
  - Migration approach: Use Ansible's `ufw` module or `firewalld` module depending on target OS

- **Fail2ban Integration**:
  - Current approach configures fail2ban with custom jail settings
  - Migration approach: Use Ansible's `template` module to configure fail2ban or use a dedicated role

- **SSH Hardening**:
  - Current approach disables root login and password authentication
  - Migration approach: Use Ansible's `lineinfile` module or `template` module for sshd_config

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe
  - PostgreSQL credentials are hardcoded in the recipe
  - Migration approach: Use Ansible Vault to encrypt sensitive values

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Preserving the dynamic generation of site configurations based on attributes
  - Mitigation: Use Ansible's template module with Jinja2 templates and variable structures similar to the Chef attributes

- **Service Orchestration**: 
  - Challenge: Ensuring proper service restart only when configuration changes
  - Mitigation: Use Ansible handlers to restart services only when needed

- **Database Management**: 
  - Challenge: PostgreSQL user and database creation with proper idempotence
  - Mitigation: Use Ansible's PostgreSQL modules which handle idempotence properly

- **Python Application Deployment**: 
  - Challenge: Managing Python virtual environments and dependencies
  - Mitigation: Use Ansible's `pip` module with virtualenv support

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Moderate complexity with templates and security configurations

2. **cache** (Priority 2)
   - Supporting service with external dependencies
   - Lower complexity as it mainly wraps existing cookbooks

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on infrastructure being in place
   - Higher complexity with database configuration and application deployment

### Assumptions

1. The target environment will continue to be Fedora 42 or similar Linux distributions.
2. Self-signed certificates are acceptable for the migration (not using Let's Encrypt or other CA).
3. The same security hardening requirements will apply in the Ansible version.
4. The FastAPI application source code will remain available at the same Git repository.
5. The current directory structure in the target environment (`/opt/server/test`, etc.) should be preserved.
6. Redis and Memcached configurations don't require advanced tuning beyond what's in the current recipes.
7. The migration will not introduce new features but will maintain feature parity with the current Chef implementation.
8. No CI/CD pipeline integration is required as part of the migration.