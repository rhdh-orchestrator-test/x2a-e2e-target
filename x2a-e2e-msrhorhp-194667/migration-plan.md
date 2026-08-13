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
- The repository has a clear structure with well-defined cookbooks
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
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef configuration data with run list and node attributes
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration for development environment using Fedora 42

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be a local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package module
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package module

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW firewall rules that need to be migrated to Ansible's ufw module
- **Fail2ban Setup**: Fail2ban configuration needs to be migrated to Ansible
- **SSH Hardening**: SSH security configurations (disabling root login, password authentication) need to be preserved
- **SSL Certificate Management**: Self-signed certificate generation needs to be migrated to Ansible's openssl_* modules
- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL database credentials in fastapi-tutorial cookbook: "fastapi:fastapi_password"
  - These should be moved to Ansible Vault or another secrets management solution

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple Nginx sites based on node attributes needs to be carefully migrated to Ansible's template system
- **SSL Certificate Generation**: The self-signed certificate generation logic needs to be preserved in Ansible
- **Service Dependencies**: Ensuring proper ordering of service installations and configurations (e.g., PostgreSQL before FastAPI application)
- **Python Environment Management**: Converting the Python virtual environment setup to Ansible's python_virtualenv module

### Migration Order

1. **nginx-multisite cookbook** (Priority 1)
   - This forms the foundation of the web infrastructure
   - Start with basic Nginx installation and configuration
   - Then add SSL and security components
   - Finally, add multi-site configuration

2. **cache cookbook** (Priority 2)
   - Relatively simple cookbook with Redis and Memcached configuration
   - Depends on external cookbooks that need to be replaced with Ansible roles

3. **fastapi-tutorial cookbook** (Priority 3)
   - Depends on PostgreSQL and Python environment setup
   - Involves application deployment and service configuration

### Assumptions

1. The target environment will continue to be Fedora-based systems
2. The same directory structure for web content will be maintained
3. Self-signed certificates are acceptable for the migrated solution (not using Let's Encrypt or other CA)
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate for the target environment
6. No changes to the application architecture are required during migration
7. The Vagrant development environment will be preserved or replaced with an equivalent