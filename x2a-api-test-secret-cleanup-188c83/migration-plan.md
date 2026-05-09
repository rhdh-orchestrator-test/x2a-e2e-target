# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- External dependencies on community cookbooks need to be replaced with Ansible Galaxy roles
- Security configurations need careful migration
- Credential management needs improvement during migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and custom configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), custom resource for line-in-file operations

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, dependency on community cookbooks

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file listing both local cookbooks and external dependencies from Chef Supermarket. Migration will require identifying Ansible Galaxy equivalents.
- `solo.json`: Chef configuration file containing the run list and node attributes. Will be replaced by Ansible inventory and variable files.
- `solo.rb`: Chef configuration file specifying paths and log settings. Will be replaced by Ansible configuration.
- `Vagrantfile`: Defines the development VM using Fedora 42. Can be adapted for Ansible testing with minimal changes.
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef. Will need to be replaced with Ansible provisioning.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` module or community.general collection
- **memcached (~> 6.0)**: Replace with Ansible's `memcached` module or geerlingguy.memcached role
- **redisio (~> 7.2.4)**: Replace with geerlingguy.redis role or custom Ansible role

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should:
  - Maintain the same certificate generation capability
  - Consider integrating with Ansible's `openssl_*` modules
  - Add option for Let's Encrypt integration using Ansible's `acme_certificate` module

- **Firewall Configuration**: Current implementation uses UFW:
  - Replace with Ansible's `ufw` module or `firewalld` module depending on target OS
  - Maintain the same allowed ports (SSH, HTTP, HTTPS)

- **Fail2ban Configuration**: 
  - Use Ansible's `template` module to create fail2ban configuration
  - Maintain the same jail settings

- **SSH Hardening**:
  - Use Ansible's `lineinfile` module to replace the current SSH configuration hardening
  - Maintain settings for disabling root login and password authentication

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the FastAPI recipe (`fastapi:fastapi_password`)
  - Migration should use Ansible Vault for all credentials

### Technical Challenges

- **Custom Resource Migration**: The `lineinfile` custom resource in the nginx-multisite cookbook needs to be replaced with Ansible's native `lineinfile` module.

- **Redis Configuration Hack**: The cache cookbook contains a Ruby block to fix Redis configuration. This will need careful migration to ensure the same configuration adjustments are made in Ansible.

- **Multi-site Configuration**: The dynamic generation of Nginx site configurations based on node attributes will need to be replicated using Ansible's templating system.

- **PostgreSQL User and Database Creation**: The current implementation uses inline shell commands. This should be replaced with Ansible's `postgresql_*` modules for better idempotency.

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component
   - Other components depend on it
   - Contains security configurations that should be established first

2. **cache** (Priority 2)
   - Depends on external cookbooks that need Ansible equivalents
   - Contains sensitive data (Redis password) that should be migrated to Ansible Vault

3. **fastapi-tutorial** (Priority 3)
   - Application-specific configuration
   - Depends on PostgreSQL which needs to be properly configured
   - Contains sensitive data (database credentials) that should be migrated to Ansible Vault

### Assumptions

1. The target environment will continue to be Fedora 42 or similar Linux distributions.
2. Self-signed certificates are acceptable for the migrated solution (production environments might require proper certificates).
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
4. The current security settings (fail2ban, ufw, SSH hardening) are appropriate for the target environment.
5. The Redis and Memcached configurations don't require advanced tuning beyond what's in the current recipes.
6. The PostgreSQL database schema is managed by the FastAPI application, not by the infrastructure code.
7. The Vagrant development environment will continue to be used for testing.