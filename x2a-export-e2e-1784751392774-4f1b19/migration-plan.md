# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with FastAPI application backend and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- No custom resources or complex Chef-specific patterns
- Standard infrastructure components (Nginx, PostgreSQL, Redis, Memcached)
- Security configurations that need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW, custom site templates

**CRITICAL PATH VERIFICATION:**
All module paths have been verified to exist in the repository:
- cookbooks/fastapi-tutorial exists and contains recipes/default.rb
- cookbooks/cache exists and contains recipes/default.rb
- cookbooks/nginx-multisite exists and contains recipes/default.rb

### Infrastructure Files

- `Berksfile`: Chef dependency manager file listing cookbook dependencies (nginx, memcached, redisio)
- `solo.json`: Chef node configuration with run list and attribute overrides
- `solo.rb`: Chef configuration file for chef-solo
- `Vagrantfile`: Defines development VM using Fedora 42 with port forwarding and networking
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package module
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package module with custom configuration

### Security Considerations

- **SSH Hardening**: The current configuration disables root login and password authentication
  - Migration approach: Use Ansible's `ssh_config` module or security role
  
- **Firewall Configuration**: UFW is configured to allow only specific ports (SSH, HTTP, HTTPS)
  - Migration approach: Use Ansible's `ufw` module or firewall role
  
- **Fail2ban**: Configured for brute force protection
  - Migration approach: Use Ansible's `template` module for fail2ban configuration
  
- **SSL/TLS**: Self-signed certificates are generated for each site
  - Migration approach: Use Ansible's `openssl_*` modules for certificate generation
  
- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the FastAPI recipe (`fastapi:fastapi_password`)
  - Migration approach: Move all credentials to Ansible Vault

### Technical Challenges

- **Multi-site Configuration**: The nginx-multisite cookbook dynamically creates site configurations based on node attributes
  - Mitigation: Use Ansible's with_items/loop to iterate through site configurations
  
- **Service Dependencies**: The FastAPI service depends on PostgreSQL being configured first
  - Mitigation: Use Ansible's handlers and notify mechanism to ensure proper ordering
  
- **SSL Certificate Generation**: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's openssl_* modules with proper idempotency checks

### Migration Order

1. **cache role** (low complexity, foundational service)
   - Implement Memcached configuration
   - Implement Redis with authentication

2. **nginx-multisite role** (medium complexity, core infrastructure)
   - Implement base Nginx configuration
   - Implement security hardening (fail2ban, UFW)
   - Implement SSL certificate generation
   - Implement site configuration templates

3. **fastapi-tutorial role** (high complexity, application layer)
   - Implement PostgreSQL database setup
   - Implement Python environment and application deployment
   - Implement systemd service configuration

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions
2. Self-signed certificates are acceptable for the migrated solution (vs. Let's Encrypt)
3. The same directory structure for web content will be maintained
4. The same security policies (SSH hardening, firewall rules) will be applied
5. The FastAPI application repository URL will remain accessible
6. The PostgreSQL database schema does not require complex migration scripts
7. Redis and Memcached configurations do not have custom tuning beyond what's visible in the recipes