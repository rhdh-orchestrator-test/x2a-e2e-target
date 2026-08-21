# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- Well-structured Chef cookbooks with clear separation of concerns
- Standard infrastructure components (Nginx, Redis, Memcached, PostgreSQL)
- Self-contained development environment using Vagrant
- Some security configurations that need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4)
- `solo.json`: Contains Chef run list and configuration data for Nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Defines the development VM using Fedora 42 with port forwarding and networking

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) based on cookbook metadata, but the Vagrant environment uses Fedora 42
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or local development

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks with custom configuration

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for development
  - Migration should maintain proper permissions (640) and ownership (root:ssl-cert)
  - Consider using Ansible's openssl_* modules or community.crypto collection

- **Firewall Configuration**: 
  - UFW firewall rules need to be migrated to Ansible's ufw module
  - Default deny policy with specific allows for SSH, HTTP, and HTTPS

- **Fail2ban Integration**:
  - Migrate fail2ban configuration to Ansible's template module
  - Ensure service is enabled and started

- **SSH Hardening**:
  - Disable root login and password authentication
  - Use Ansible's lineinfile or template module for sshd_config

- **Vault/secrets management**:
  - Redis password ("redis_secure_password_123") in cache/recipes/default.rb
  - PostgreSQL user password ("fastapi_password") in fastapi-tutorial/recipes/default.rb
  - These should be migrated to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - The Chef cookbook dynamically creates Nginx site configurations based on node attributes
  - Ansible will need to use loops with template module to achieve the same functionality

- **SSL Certificate Generation**:
  - Chef uses inline shell commands for certificate generation
  - Ansible should use the openssl_* modules for better idempotence

- **PostgreSQL User and Database Creation**:
  - Chef uses shell commands via execute resource
  - Ansible should use the postgresql_* modules for better idempotence and error handling

- **Redis Configuration Hack**:
  - The Chef cookbook includes a ruby_block to modify Redis configuration
  - Ansible will need to use lineinfile or template with proper regex handling

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Then add SSL and security features
   - Finally implement the multi-site configuration

2. **cache** (Priority 2)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper service management

3. **fastapi-tutorial** (Priority 3)
   - Set up PostgreSQL database
   - Configure Python environment and application deployment
   - Create systemd service

### Assumptions

1. The target environment will continue to use Vagrant for development/testing
2. The same operating system support (Ubuntu 18.04+/CentOS 7+) is required
3. Self-signed certificates are acceptable for development (production would likely use Let's Encrypt or other CA)
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current security configurations are appropriate for the target environment
6. No additional monitoring or logging requirements beyond what's in the current Chef setup
7. Redis and Memcached configurations don't require clustering or high availability
8. The PostgreSQL database will remain local to the application server