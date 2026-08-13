# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration scope involves converting 3 Chef cookbooks to Ansible roles, handling external dependencies, and preserving the current deployment workflow that uses Vagrant for development/testing.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- **Total**: 5-6 weeks

**Complexity Assessment**: Medium
- Small number of cookbooks (3)
- Standard technology stack (Nginx, Redis, Memcached, PostgreSQL, Python)
- Some security considerations (SSL, authentication)
- Vagrant integration for testing

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts/subdomains
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate management, security hardening

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database provisioning, systemd service configuration

### Infrastructure Files

- `Berksfile`: Manages Chef cookbook dependencies. Will be replaced with Ansible Galaxy requirements.yml
- `solo.json`: Contains Chef node attributes and run list. Will be replaced with Ansible group_vars and inventory
- `solo.rb`: Chef Solo configuration. Will be replaced with ansible.cfg
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef. Will be replaced with Ansible provisioner in Vagrantfile
- `Vagrantfile`: Defines the development/test VM. Will be updated to use Ansible provisioner instead of Chef

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be focused on local development/testing

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` role or direct package installation and configuration

### Security Considerations

- **SSL Certificate Management**: 
  - Current implementation uses self-signed certificates for multiple domains
  - Migration approach: Use Ansible's `community.crypto.openssl_*` modules for certificate generation
  - Store certificates in `/etc/ssl/certs` and private keys in `/etc/ssl/private` as per current configuration

- **Redis Authentication**:
  - Current implementation sets a hardcoded Redis password in the recipe
  - Migration approach: Use Ansible Vault to store the Redis password securely

- **PostgreSQL Authentication**:
  - Current implementation has hardcoded database credentials in the recipe
  - Migration approach: Use Ansible Vault for database credentials

- **Security Hardening**:
  - Current implementation includes fail2ban, ufw, and SSH hardening
  - Migration approach: Use Ansible's `security` role or dedicated modules for each security component

- **Vault/secrets management**:
  - Credentials detected:
    - Redis password (hardcoded in cache/recipes/default.rb)
    - PostgreSQL user and password (hardcoded in fastapi-tutorial/recipes/default.rb)
    - FastAPI environment variables (hardcoded in fastapi-tutorial/recipes/default.rb)
  - Migration approach: Move all credentials to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Preserving the dynamic nature of the multi-site configuration
  - Mitigation: Use Ansible templates with loops to generate site configurations from variables

- **Service Dependencies**:
  - Challenge: Ensuring proper ordering of service deployment (PostgreSQL before FastAPI, etc.)
  - Mitigation: Use Ansible's `handlers` and `notify` mechanism to manage service dependencies

- **Vagrant Integration**:
  - Challenge: Replacing Chef provisioning with Ansible in the Vagrant workflow
  - Mitigation: Update Vagrantfile to use the Ansible provisioner instead of shell provisioning with Chef

### Migration Order

1. **cache** role (low complexity, standalone services)
   - Implement Redis configuration with Ansible Vault for password
   - Implement Memcached configuration

2. **nginx-multisite** role (medium complexity)
   - Implement base Nginx installation
   - Implement SSL certificate management
   - Implement multi-site configuration with templates
   - Implement security hardening

3. **fastapi-tutorial** role (high complexity, has dependencies)
   - Implement PostgreSQL database setup with Ansible Vault for credentials
   - Implement Python environment setup
   - Implement application deployment from Git
   - Implement systemd service configuration

### Assumptions

1. The current Chef setup is functional and represents the desired end state
2. The target environment will continue to be Fedora 42 or compatible Linux distributions
3. Vagrant with libvirt will continue to be used for development/testing
4. Self-signed certificates are acceptable for the migrated solution
5. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git is accessible and will remain available
6. The current security measures (fail2ban, ufw, SSH hardening) are sufficient and should be maintained
7. No additional monitoring or logging requirements beyond what's in the current Chef configuration
8. The migration will be a direct conversion of functionality rather than a redesign of the architecture