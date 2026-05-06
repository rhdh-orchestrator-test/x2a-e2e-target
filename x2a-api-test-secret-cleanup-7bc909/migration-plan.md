# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure for deploying a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, configuration templates, and security settings.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- **Total**: 5-6 weeks

**Complexity Assessment**: Medium
- Well-structured Chef cookbooks with clear separation of concerns
- Standard infrastructure components (Nginx, Redis, Memcached, PostgreSQL)
- Security configurations that need careful migration
- Hardcoded credentials that should be moved to Ansible Vault

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
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file listing cookbook dependencies (nginx, memcached, redisio)
- `solo.json`: Chef Solo configuration with run list and node attributes
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `Vagrantfile`: Defines development VM using Fedora 42, with port forwarding and resource allocation
- `vagrant-provision.sh`: Bash script to provision the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development/testing

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create custom Nginx role
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or DavidWittman.redis

### Security Considerations

- **fail2ban configuration**: Migrate fail2ban jail configuration to Ansible templates
- **UFW firewall rules**: Use Ansible UFW module to configure firewall rules
- **SSH hardening**: Implement SSH configuration using Ansible's lineinfile or template module
- **sysctl security settings**: Use Ansible sysctl module to apply kernel parameter security settings
- **Vault/secrets management**:
  - Redis password in cache cookbook: Move to Ansible Vault
  - PostgreSQL credentials in fastapi-tutorial cookbook: Move to Ansible Vault
  - SSL certificate private keys: Ensure proper permissions and consider using ansible-vault for sensitive operations

### Technical Challenges

- **SSL Certificate Generation**: Chef cookbook generates self-signed certificates; need to implement equivalent functionality in Ansible using the openssl_* modules
- **Multi-site Nginx Configuration**: Need to create a flexible template system in Ansible to handle multiple virtual hosts with conditional SSL
- **Redis Configuration Hack**: The Chef cookbook includes a ruby_block to modify Redis configuration; need to create a clean approach in Ansible
- **Service Dependencies**: Ensure proper ordering of service deployments (e.g., PostgreSQL before FastAPI application)

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx configuration, then add SSL and security features
   - Test virtual host configuration thoroughly

2. **cache** (Priority 2)
   - Implement Memcached and Redis configurations
   - Ensure Redis authentication is properly secured with Ansible Vault
   - Test connectivity and performance

3. **fastapi-tutorial** (Priority 3)
   - Set up PostgreSQL database
   - Deploy Python application with virtual environment
   - Configure systemd service
   - Test application functionality

### Assumptions

1. The target environment will continue to be Fedora-based systems (specifically Fedora 42 as specified in the Vagrantfile)
2. Self-signed certificates are acceptable for the migrated solution (production environments might require Let's Encrypt integration)
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
4. The current security settings (fail2ban, UFW, SSH hardening) are appropriate for the target environment
5. The Redis configuration "hack" in the cache cookbook is necessary due to compatibility issues that may need investigation during migration
6. The hardcoded credentials in the fastapi-tutorial cookbook are for development only and should be replaced with secure values in production
7. The Nginx site configurations (test.cluster.local, ci.cluster.local, status.cluster.local) will remain the same in the migrated solution