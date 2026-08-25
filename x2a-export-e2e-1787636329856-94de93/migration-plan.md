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

- `Berksfile`: Dependency management for Chef cookbooks. Lists both local and external cookbook dependencies.
- `solo.json`: Chef node configuration with run list and attribute settings for Nginx sites and security.
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings.
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef.
- `Vagrantfile`: Vagrant configuration for development environment using Fedora 42.

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in the Vagrant development environment.
- **Virtual Machine Technology**: Vagrant with libvirt provider (based on Vagrantfile configuration).
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct configuration

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration should maintain proper permissions (640) and ownership (root:ssl-cert)
  - Consider integrating with Ansible's crypto modules or community.crypto collection

- **Firewall Configuration**:
  - UFW firewall rules need to be migrated to equivalent Ansible ufw module tasks
  - Default deny policy with specific allows for SSH, HTTP, HTTPS

- **SSH Hardening**:
  - Disable root login
  - Disable password authentication
  - Use Ansible's lineinfile or template module to configure sshd_config

- **Fail2Ban Integration**:
  - Fail2ban configuration needs to be migrated to Ansible tasks
  - Custom jail.local template needs to be preserved

- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL credentials in fastapi-tutorial cookbook: "fastapi:fastapi_password"
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - The dynamic generation of site configurations based on node attributes needs to be converted to Ansible's template system
  - Ensure proper SSL certificate paths and permissions are maintained

- **Service Dependencies**:
  - Ensure proper ordering of tasks for services that depend on each other (e.g., PostgreSQL before FastAPI application)
  - Implement handlers for service restarts/reloads equivalent to Chef notifications

- **System Tuning**:
  - Security-related sysctl settings need to be migrated
  - Consider using Ansible's sysctl module instead of templates

- **Python Application Deployment**:
  - Git repository cloning and Python virtual environment setup
  - Environment file creation with database connection string
  - Systemd service configuration

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Implement security hardening (fail2ban, ufw)
   - Configure virtual hosts

2. **cache** (Priority 2)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper service management

3. **fastapi-tutorial** (Priority 3)
   - Set up PostgreSQL database
   - Deploy Python application
   - Configure systemd service

### Assumptions

1. The target environment will continue to support either Ubuntu (>= 18.04) or CentOS (>= 7.0).
2. Self-signed certificates are acceptable for development; production may require integration with Let's Encrypt or other certificate authorities.
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
4. The Vagrant development environment will continue to be used for testing.
5. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate for the target environment.
6. The Redis and PostgreSQL passwords in the code are development credentials and will be replaced with secure values in production.
7. The current directory structure for web content (/var/www/[site]) will be maintained.