# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with FastAPI application backend and caching services (Redis and Memcached). The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a moderate number of cookbooks with straightforward configurations
- No complex custom resources or libraries
- Clear separation of concerns between cookbooks
- Standard deployment patterns for web servers, application servers, and caching services

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw)

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks, lists both local and external cookbook dependencies
- `solo.json`: Chef node configuration with run list and attribute overrides
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Defines development VM using Fedora 42, with port forwarding and network configuration
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used for development
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package module
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package module

### Security Considerations

- **SSL/TLS Management**: 
  - Self-signed certificates are generated for each site
  - Migration should maintain the same level of security or improve it
  - Consider using Ansible's openssl_* modules or community.crypto collection

- **Firewall Configuration**:
  - UFW is configured to allow only SSH, HTTP, and HTTPS
  - Migrate to Ansible's ufw module or firewalld module depending on target OS

- **SSH Hardening**:
  - Root login disabled
  - Password authentication disabled
  - Migrate to Ansible's openssh_config module

- **System Hardening**:
  - sysctl security settings
  - fail2ban configuration
  - Migrate to Ansible's sysctl module and template module for fail2ban

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the FastAPI recipe
  - Recommend using Ansible Vault for all credentials in the migrated solution

### Technical Challenges

- **Multi-site Configuration**: 
  - The nginx-multisite cookbook dynamically creates site configurations based on node attributes
  - Solution: Use Ansible loops with templates to achieve the same dynamic configuration

- **SSL Certificate Generation**:
  - Self-signed certificates are generated for each site
  - Solution: Use Ansible's openssl_* modules to generate certificates or integrate with Let's Encrypt

- **Service Dependencies**:
  - FastAPI application depends on PostgreSQL
  - Solution: Use Ansible handlers and meta dependencies to ensure proper service ordering

- **Configuration File Modifications**:
  - The cache cookbook uses a ruby_block to modify Redis configuration
  - Solution: Use Ansible's lineinfile or template module with proper templating

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add SSL and security features
   - Finally, add multi-site configuration

2. **cache** (Priority 2)
   - Relatively independent service
   - Simple configuration for Memcached
   - More complex configuration for Redis with authentication

3. **fastapi-tutorial** (Priority 3)
   - Depends on PostgreSQL being configured
   - Requires application deployment from Git
   - Needs systemd service configuration

### Assumptions

1. The target environment will continue to be Vagrant-based for development/testing
2. The same operating systems (Ubuntu/CentOS) will be supported
3. Self-signed certificates are acceptable (no requirement for Let's Encrypt or commercial certificates)
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. No CI/CD pipeline integration is required as part of the migration
6. The current security configurations (fail2ban, ufw, SSH hardening) are sufficient and should be maintained
7. No monitoring or logging solutions are currently implemented and none are required in the migration
8. The current Redis and Memcached configurations are sufficient for the application needs