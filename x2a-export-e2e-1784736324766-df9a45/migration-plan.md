# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services (Redis and Memcached) and a FastAPI application. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and files to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- No custom resources or complex Chef-specific patterns are used
- Standard package installation and configuration patterns are used throughout

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), custom site templates

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4)
- `solo.json`: Contains node attributes and run list for Chef Solo
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Shell script for provisioning Chef in Vagrant VM
- `Vagrantfile`: Vagrant configuration for development environment using Fedora 42

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or local development

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks
- **PostgreSQL**: Replace with Ansible postgresql_* modules or community.postgresql collection

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated in the nginx-multisite cookbook
  - Migration approach: Use Ansible's openssl_* modules or community.crypto collection

- **Firewall Configuration**: 
  - UFW is configured in security.rb
  - Migration approach: Use Ansible's ufw module

- **Fail2ban Configuration**: 
  - Configured in security.rb with custom jail.local template
  - Migration approach: Use Ansible's template module with equivalent templates

- **SSH Hardening**: 
  - Root login and password authentication can be disabled
  - Migration approach: Use Ansible's lineinfile module or ssh_config module

- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook ("redis_secure_password_123")
  - PostgreSQL password is hardcoded in the fastapi-tutorial cookbook ("fastapi_password")
  - Migration approach: Use Ansible Vault for storing sensitive information

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - The current implementation uses Chef's iteration over node attributes to create multiple sites
  - Mitigation: Use Ansible loops with site-specific variables in host_vars or group_vars

- **Redis Configuration Customization**: 
  - The current implementation uses a ruby_block to modify Redis configuration
  - Mitigation: Use Ansible's lineinfile module or template with proper configuration

- **Service Dependencies**: 
  - The FastAPI service depends on PostgreSQL
  - Mitigation: Use Ansible's meta: flush_handlers and proper ordering with dependencies

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security configurations that should be established first

2. **cache** (Priority 2)
   - Supporting service with moderate complexity
   - Depends on external cookbooks that need to be replaced

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on the infrastructure being in place
   - Involves database setup, application code deployment, and service configuration

### Assumptions

1. The target environment will continue to be Fedora 42 or a compatible Linux distribution
2. Self-signed certificates are acceptable for development/testing (production would likely use Let's Encrypt or other CA)
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
4. The current security configurations are appropriate for the target environment
5. No custom Chef handlers or complex Chef-specific patterns are in use that would require special handling
6. The Vagrant development environment will be maintained for testing
7. No external Chef server is being used (Chef Solo only)