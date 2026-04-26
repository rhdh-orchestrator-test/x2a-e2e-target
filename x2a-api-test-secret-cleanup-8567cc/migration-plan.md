# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- **Total**: 5-6 weeks

**Complexity Assessment**: Medium
- Well-structured Chef cookbooks with clear separation of concerns
- Standard infrastructure components (Nginx, Redis, Memcached, PostgreSQL)
- Security configurations that need careful migration
- Hardcoded credentials that should be migrated to Ansible Vault

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and proper SSL configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall), HTTP-to-HTTPS redirection

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

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4)
- `solo.json`: Defines the Chef run list and configuration attributes for Nginx sites and security settings
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Defines the Vagrant VM configuration (Fedora 42) with port forwarding and networking

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development/testing

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or DavidWittman.redis

### Security Considerations

- **SSL Certificate Management**: 
  - Chef cookbook generates self-signed certificates
  - Migration approach: Use Ansible's `openssl_*` modules or community.crypto collection for certificate generation
  - Consider integrating with Let's Encrypt for production environments

- **Firewall Configuration**: 
  - Chef cookbook configures UFW with specific rules
  - Migration approach: Use Ansible's `ufw` module to replicate the same rules

- **fail2ban Configuration**:
  - Chef cookbook installs and configures fail2ban
  - Migration approach: Use Ansible to install fail2ban and template the configuration

- **SSH Hardening**:
  - Chef cookbook disables root login and password authentication
  - Migration approach: Use Ansible's `lineinfile` module or the `ansible-hardening` role

- **Vault/secrets management**:
  - Hardcoded Redis password in cache/recipes/default.rb: "redis_secure_password_123"
  - Hardcoded PostgreSQL password in fastapi-tutorial/recipes/default.rb: "fastapi_password"
  - Migration approach: Move all credentials to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Replicating the dynamic site configuration from Chef to Ansible
  - Mitigation: Create Ansible templates for Nginx site configurations and use loops to iterate through site definitions

- **SSL Certificate Generation**:
  - Challenge: Ensuring proper permissions and security for SSL certificates
  - Mitigation: Use Ansible's file module with appropriate permissions and the openssl_* modules for certificate generation

- **PostgreSQL User and Database Creation**:
  - Challenge: Converting Chef execute resources to idempotent Ansible tasks
  - Mitigation: Use Ansible's postgresql_* modules instead of shell commands for better idempotence

- **Python Application Deployment**:
  - Challenge: Ensuring proper virtual environment setup and dependency installation
  - Mitigation: Use Ansible's pip module with virtualenv parameter for better control

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security configurations that should be established first

2. **cache** (Priority 2)
   - Moderate complexity with Redis and Memcached configuration
   - Depends on proper network configuration from nginx-multisite

3. **fastapi-tutorial** (Priority 3)
   - Most complex component with database, application code, and service configuration
   - Depends on both networking and potentially caching services

### Assumptions

1. The target environment will continue to be Fedora-based systems (specifically Fedora 42 as indicated in the Vagrantfile)
2. The self-signed SSL certificates approach is acceptable for the migrated solution (production environments might require a different approach)
3. The current hardcoded passwords are for development only and will be replaced with more secure values in the Ansible Vault
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current directory structure in the target environment (/opt/server/*, /var/www/*) should be maintained
6. The Nginx configuration with security headers and SSL settings should be preserved exactly as they are now
7. The current VM specifications (2GB RAM, 2 CPUs) are sufficient for the application stack