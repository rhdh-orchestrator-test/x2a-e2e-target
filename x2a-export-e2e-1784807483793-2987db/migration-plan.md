# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with FastAPI application backend and caching services (Redis and Memcached). The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- No custom resources or complex Chef-specific patterns
- Standard infrastructure components (Nginx, Redis, Memcached, PostgreSQL)
- Security configurations that need careful migration

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

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies.
- `solo.json`: Configuration data for Chef Solo run, contains site configurations and security settings.
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings.
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef.
- `Vagrantfile`: Vagrant configuration for development environment using Fedora 42.

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>=18.04) and CentOS (>=7.0), with Fedora 42 used in the Vagrant development environment.
- **Virtual Machine Technology**: Vagrant with libvirt provider (based on Vagrantfile configuration).
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks

### Security Considerations

- **SSL/TLS Management**: 
  - Self-signed certificates are generated for each site
  - Migration should maintain proper file permissions (640 for private keys)
  - Consider integrating with Ansible's crypto modules or certbot for Let's Encrypt

- **Firewall Configuration**:
  - UFW firewall rules need to be migrated to Ansible's ufw module
  - Default deny policy with specific allows for SSH, HTTP, HTTPS

- **SSH Hardening**:
  - Root login disabled
  - Password authentication disabled
  - Migrate to Ansible's openssh_* modules

- **Fail2ban Configuration**:
  - Custom jail.local template needs migration
  - Ensure service is enabled and running

- **Vault/secrets management**:
  - Redis password in plaintext in recipe (redis_secure_password_123)
  - PostgreSQL password in plaintext in recipe (fastapi_password)
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - The Chef cookbook dynamically creates site configurations based on node attributes
  - Ansible implementation will need to use loops with templates to achieve the same functionality

- **SSL Certificate Generation**:
  - Current implementation uses inline shell commands for OpenSSL
  - Ansible has dedicated modules (openssl_* family) that should be used instead

- **System Tuning**:
  - Security-related sysctl settings need to be migrated
  - Consider using Ansible's sysctl module instead of templates

- **PostgreSQL Database Setup**:
  - Current implementation uses inline SQL commands
  - Ansible has postgresql_* modules that should be used instead

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Then add SSL and security components
   - Finally implement multi-site configuration

2. **cache** (Priority 2)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper service management

3. **fastapi-tutorial** (Priority 3)
   - Set up Python environment and dependencies
   - Configure PostgreSQL database
   - Deploy application code and systemd service

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based systems.
2. The Vagrant development environment will be maintained for testing.
3. Self-signed certificates are acceptable for development, but production may require proper certificates.
4. The current security configurations are appropriate and should be maintained in the Ansible implementation.
5. No changes to the application architecture are planned during migration.
6. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
7. The current Redis and Memcached configurations meet performance requirements and don't need optimization.