# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server setup with FastAPI application backend and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
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

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and SSL certificate management
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, SSH hardening)

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database setup
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks - lists both local and external dependencies
- `solo.json`: Chef Solo run list and node attributes configuration
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration for development/testing environment

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible `nginx` role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible `geerlingguy.memcached` role or custom Ansible tasks
- **redisio (~> 7.2.4)**: Replace with Ansible `geerlingguy.redis` role or custom Ansible tasks

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration should maintain the same level of security or improve it
  - Consider using Ansible's `openssl_*` modules or `community.crypto` collection

- **Firewall Configuration**: 
  - UFW firewall rules need to be migrated to Ansible `ufw` module
  - Default deny policy with specific allows for SSH, HTTP, HTTPS

- **SSH Hardening**:
  - Root login disabled
  - Password authentication disabled
  - Use Ansible's `lineinfile` or templates to configure SSH

- **Fail2ban Configuration**:
  - Custom fail2ban configuration needs to be migrated
  - Use Ansible templates to create fail2ban jail configuration

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the FastAPI recipe (`fastapi:fastapi_password`)
  - These should be migrated to Ansible Vault or another secrets management solution

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - The Chef cookbook dynamically creates Nginx site configurations based on node attributes
  - Ansible will need to use loops with templates to achieve the same functionality

- **SSL Certificate Generation**:
  - Self-signed certificates are generated with custom attributes
  - Ansible's `openssl_certificate` module will need to be configured to match the current behavior

- **Service Dependencies**:
  - FastAPI service depends on PostgreSQL
  - Proper ordering of tasks and handlers will be needed in Ansible

- **Dynamic Configuration**:
  - Chef attributes are used to configure sites and security settings
  - Ansible variables and templates will need to be structured to maintain flexibility

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add SSL certificate management
   - Add security hardening (fail2ban, ufw)
   - Add multi-site configuration

2. **cache** (Priority 2)
   - Standalone services that other components may depend on
   - Migrate Memcached configuration
   - Migrate Redis configuration with authentication

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on other infrastructure
   - Migrate PostgreSQL setup
   - Migrate Python environment and application deployment
   - Migrate systemd service configuration

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions (Ubuntu 18.04+, CentOS 7+).
2. The same directory structure for web content and SSL certificates will be maintained.
3. Self-signed certificates are acceptable for the migrated solution (not using Let's Encrypt or other CA).
4. The Vagrant development environment will be maintained but converted to use Ansible provisioner.
5. No changes to the application code or database schema are required.
6. The current security settings (fail2ban, ufw, SSH hardening) are appropriate and should be maintained.
7. The Redis and PostgreSQL passwords in the current code are development passwords and will be replaced with proper secrets management.