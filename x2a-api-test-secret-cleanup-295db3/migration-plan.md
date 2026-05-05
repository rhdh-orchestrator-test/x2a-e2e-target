# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- **Total**: 5-6 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- External dependencies on community cookbooks will need Ansible equivalents
- Security configurations are present and will need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site-specific configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall), sysctl security settings

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

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef configuration file containing the run list and node attributes
- `solo.rb`: Chef configuration file specifying cookbook paths and logging settings
- `Vagrantfile`: Defines a Vagrant VM for development/testing with Fedora 42
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or DavidWittman.redis

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW firewall rules that need to be migrated to Ansible's `ufw` module
- **fail2ban Setup**: Fail2ban configuration needs to be migrated using Ansible's package and template modules
- **SSH Hardening**: SSH security settings (disabling root login, password authentication) need to be migrated
- **SSL Certificate Management**: Self-signed certificate generation needs to be migrated to Ansible's `openssl_*` modules
- **Vault/secrets management**:
  - Redis password in cache cookbook (hardcoded as 'redis_secure_password_123')
  - PostgreSQL database credentials in fastapi-tutorial cookbook (hardcoded as 'fastapi_password')
  - These should be migrated to Ansible Vault or another secrets management solution

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple virtual hosts based on node attributes will need to be replicated in Ansible using templates and variables
- **SSL Certificate Generation**: The self-signed certificate generation logic will need to be migrated to Ansible's `openssl_certificate` module
- **PostgreSQL User/Database Creation**: The current implementation uses direct shell commands, which should be replaced with Ansible's PostgreSQL modules
- **Service Management**: Ensuring proper service dependencies and restart handlers are maintained in Ansible

### Migration Order

1. **nginx-multisite** (Priority 1)
   - This is the foundation for the web infrastructure
   - Other components depend on it being properly configured

2. **cache** (Priority 2)
   - Moderate complexity with external dependencies
   - Requires proper handling of Redis authentication

3. **fastapi-tutorial** (Priority 3)
   - Depends on PostgreSQL being properly configured
   - Involves application deployment and service configuration

### Assumptions

1. The target environment will continue to be Fedora-based systems (specifically Fedora 42 as indicated in the Vagrantfile)
2. The same directory structure for web content and configuration files will be maintained
3. Self-signed certificates are acceptable for development/testing (production would likely use Let's Encrypt or other CA)
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current security settings (fail2ban, UFW, SSH hardening) are appropriate for the target environment
6. Redis and PostgreSQL passwords are currently hardcoded and will need to be moved to a secure storage solution
7. The Vagrant development environment will be maintained but converted to use Ansible provisioning