# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Scope**: 3 Chef cookbooks with external dependencies
**Complexity**: Medium
**Estimated Timeline**: 2-3 weeks for complete migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **cache**:
    - Description: Configures caching services (memcached and redis) with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration
    - Default Recipe: cookbooks/cache/recipes/default.rb

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management
    - Default Recipe: cookbooks/fastapi-tutorial/recipes/default.rb

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)
    - Default Recipe: cookbooks/nginx-multisite/recipes/default.rb

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (nginx, memcached, redisio)
- `solo.json`: Defines the Chef run list and configuration attributes
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Defines the development VM (Fedora 42)
- `vagrant-provision.sh`: Script to provision the VM with Chef

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` role or direct package installation

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration approach: Use Ansible's `openssl_*` modules or `community.crypto` collection

- **Firewall Configuration**: 
  - UFW is configured with default deny and specific allow rules
  - Migration approach: Use Ansible's `ufw` module

- **SSH Hardening**:
  - Root login disabled
  - Password authentication disabled
  - Migration approach: Use Ansible's `lineinfile` module or `ansible.posix.sshd` module

- **System Hardening**:
  - Sysctl security parameters
  - Migration approach: Use Ansible's `sysctl` module

- **Fail2ban Configuration**:
  - Custom jail configuration
  - Migration approach: Use Ansible's `template` module or `fail2ban` role

- **Vault/secrets management**:
  - Hardcoded credentials detected:
    - PostgreSQL password in fastapi-tutorial/recipes/default.rb
    - Redis password in cache/recipes/default.rb
  - Migration approach: Use Ansible Vault for all credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Maintaining the dynamic generation of site configurations
  - Mitigation: Use Ansible's template module with loops over site dictionary variables

- **SSL Certificate Generation**:
  - Challenge: Ensuring certificates are only generated when needed
  - Mitigation: Use Ansible's `stat` module to check for existing certificates and `changed_when` conditions

- **Service Dependencies**:
  - Challenge: Ensuring proper service startup order (e.g., PostgreSQL before FastAPI)
  - Mitigation: Use Ansible's `meta: flush_handlers` and proper task ordering

- **Idempotent Execution**:
  - Challenge: Ensuring commands like database creation run only when needed
  - Mitigation: Use Ansible's `changed_when`, `failed_when`, and proper conditionals

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Relatively self-contained with clear configuration templates

2. **cache** (Priority 2)
   - Depends on external roles (memcached, redis)
   - Moderate complexity with configuration customization

3. **fastapi-tutorial** (Priority 3)
   - Depends on PostgreSQL and potentially Nginx for serving
   - Most complex with application deployment, database setup, and service configuration

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt)
3. The same directory structure for document roots and SSL certificates will be maintained
4. The FastAPI application repository will remain available at the specified URL
5. PostgreSQL and Redis passwords in the Chef recipes are development credentials and will be replaced with secure values in Ansible Vault
6. The Vagrant development environment will be maintained but converted to use Ansible provisioner instead of Chef