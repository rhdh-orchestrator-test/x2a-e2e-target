# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

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

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (nginx, memcached, redisio)
- `solo.json`: Chef Solo run list and node attributes configuration
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Bash script for provisioning Chef in Vagrant VM
- `Vagrantfile`: Vagrant configuration for development environment

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development/testing

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible `nginx` role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible `geerlingguy.memcached` role or custom role
- **redisio (~> 7.2.4)**: Replace with Ansible `geerlingguy.redis` role or custom role

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration should maintain the same level of security or improve it
  - Consider using Ansible's `openssl_*` modules or `community.crypto` collection

- **Firewall Configuration**:
  - UFW is configured with default deny policy and specific allow rules
  - Replace with Ansible `ufw` module or `firewalld` module depending on target OS

- **SSH Hardening**:
  - Root login disabled
  - Password authentication disabled
  - Use Ansible's `lineinfile` or templates to configure SSH

- **Fail2ban Configuration**:
  - Custom jail configuration
  - Use Ansible to install and configure fail2ban

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the FastAPI recipe
  - Recommend using Ansible Vault for all credentials in the migrated solution

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - The Chef cookbook dynamically creates site configurations based on node attributes
  - Ansible solution will need to use loops with templates to achieve the same functionality

- **SSL Certificate Generation**:
  - Self-signed certificates are generated with OpenSSL commands
  - Ansible has built-in modules for this which will simplify the migration

- **Service Dependencies**:
  - FastAPI service depends on PostgreSQL
  - Ensure proper ordering in Ansible playbooks using handlers and dependencies

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add SSL and security features
   - Finally add multi-site configuration

2. **cache** (Priority 2)
   - Relatively simple configuration with external dependencies
   - Memcached and Redis are standard services with good Ansible support

3. **fastapi-tutorial** (Priority 3)
   - Application-specific configuration
   - Depends on PostgreSQL and potentially Nginx for serving

### Assumptions

1. The target environment will continue to be Fedora or a similar Linux distribution
2. The same security requirements will apply in the new environment
3. Self-signed certificates are acceptable for development (production would likely use Let's Encrypt or similar)
4. The FastAPI application repository will remain available at the same URL
5. The multi-site configuration pattern will be maintained
6. Redis and Memcached will continue to be the caching solutions
7. PostgreSQL will continue to be the database for the FastAPI application