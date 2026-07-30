# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx configuration with caching services (Redis and Memcached) and a FastAPI application with PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- No complex custom resources or libraries
- Standard infrastructure components (web server, caching, application deployment)
- Security configurations that need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificates
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4)
- `solo.json`: Contains the run list and configuration data for the Chef run
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Defines a Fedora 42 VM with port forwarding for development/testing
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or local development

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)
- **PostgreSQL**: Replace with Ansible PostgreSQL role (e.g., geerlingguy.postgresql)

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration should maintain the same level of security or improve it
  - Consider using Ansible's openssl_* modules or community.crypto collection

- **Firewall Configuration**: 
  - UFW firewall rules need to be migrated to equivalent Ansible ufw module tasks
  - Default deny policy with specific allows for SSH, HTTP, and HTTPS

- **Fail2ban Integration**: 
  - Fail2ban configuration needs to be migrated to Ansible tasks
  - Template for jail.local needs to be converted

- **SSH Hardening**: 
  - Root login disabled
  - Password authentication disabled
  - These configurations need to be maintained in Ansible

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe as 'redis_secure_password_123'
  - PostgreSQL password is hardcoded as 'fastapi_password'
  - Both should be moved to Ansible Vault during migration
  - Total credentials detected: 2 (Redis and PostgreSQL)

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - The Chef cookbook dynamically creates Nginx site configurations based on node attributes
  - Ansible implementation will need to use loops with templates to achieve the same functionality

- **SSL Certificate Generation**: 
  - Self-signed certificates are generated for each site
  - Ansible will need to use the openssl_* modules to replicate this functionality

- **Service Dependencies**: 
  - The FastAPI application depends on PostgreSQL
  - Ansible handlers and wait_for modules may be needed to ensure proper service startup order

- **Template Conversion**: 
  - Several ERB templates need to be converted to Jinja2 format
  - Syntax differences between ERB and Jinja2 need to be addressed

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx configuration and site setup
   - Then add SSL and security features

2. **cache** (Priority 2)
   - Relatively simple module with standard configurations
   - Depends on external cookbooks that have direct Ansible equivalents

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on other infrastructure
   - More complex with database setup, virtual environment, and service configuration

### Assumptions

1. The target environment will continue to be Fedora 42 or a compatible Linux distribution.
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or other CA).
3. The same security posture should be maintained or improved in the Ansible implementation.
4. The Vagrant development workflow should be preserved with an equivalent Ansible-based provisioning approach.
5. No changes to the application code or architecture are required as part of this migration.
6. The current hardcoded passwords will be replaced with Ansible Vault secured variables.
7. The directory structure in the target environment will remain the same.