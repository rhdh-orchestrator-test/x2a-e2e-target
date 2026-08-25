# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server setup with FastAPI application backend and caching services (Redis and Memcached). The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- No custom resources or complex Chef-specific patterns
- Standard infrastructure components (web servers, caching, application deployment)

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw)

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef Solo configuration file with run list and node attributes
- `solo.rb`: Chef Solo configuration file with paths and settings
- `vagrant-provision.sh`: Provisioning script for Vagrant that installs Chef and runs the cookbooks
- `Vagrantfile`: Vagrant configuration for development environment using Fedora 42

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in Vagrant development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or community.general.memcached module
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or community.general.redis module

### Security Considerations

- **SSL/TLS Management**: 
  - Self-signed certificates are generated for each site
  - Migration should maintain proper permissions (640) and ownership (root:ssl-cert)
  - Consider using Ansible's crypto modules for certificate generation

- **Firewall Configuration**:
  - UFW is configured with default deny and specific allow rules
  - Migrate to Ansible's ufw module or firewalld for Fedora/RHEL systems

- **SSH Hardening**:
  - Root login disabled
  - Password authentication disabled
  - Migrate to Ansible's openssh_config module

- **Fail2ban Configuration**:
  - Custom jail configuration
  - Migrate to Ansible's fail2ban module

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL credentials hardcoded in FastAPI recipe (`fastapi:fastapi_password`)
  - Both should be migrated to Ansible Vault

### Technical Challenges

- **Multi-site Configuration**: The nginx-multisite cookbook dynamically creates site configurations based on node attributes. This pattern needs to be replicated in Ansible using loops and templates.

- **Service Dependencies**: The FastAPI application depends on PostgreSQL, and the web server depends on the application being available. These dependencies need to be properly managed in the Ansible playbook.

- **SSL Certificate Generation**: Self-signed certificates are generated for each site. This needs to be handled carefully in Ansible to ensure idempotence and proper permissions.

- **System Tuning**: Security-related sysctl settings need to be migrated to Ansible's sysctl module.

### Migration Order

1. **cache role** (Priority 1, low complexity)
   - Simple configuration of Redis and Memcached
   - Good starting point with minimal dependencies

2. **nginx-multisite role** (Priority 2, medium complexity)
   - Core infrastructure component
   - Multiple templates and configurations to migrate
   - Security hardening components

3. **fastapi-tutorial role** (Priority 3, medium complexity)
   - Application deployment with database dependencies
   - Requires proper handling of Python virtual environments and Git repository

### Assumptions

1. The target environment will continue to support the same operating systems (Ubuntu 18.04+ or CentOS 7.0+)
2. The Vagrant development environment will be maintained for testing
3. The same directory structure for web content will be maintained
4. Self-signed certificates are acceptable for development (not production)
5. The FastAPI application source code will remain available at the specified Git repository
6. PostgreSQL will be installed locally rather than using an external database service
7. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate for the target environment
8. Redis and Memcached will continue to be used as caching solutions