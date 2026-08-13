# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- External dependencies on community cookbooks need to be replaced with Ansible Galaxy roles
- Security configurations and SSL certificate management require careful migration
- Hardcoded credentials need to be replaced with Ansible Vault

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificates
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4)
- `solo.json`: Contains node attributes and run list for Chef Solo, including Nginx site configurations and security settings
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `Vagrantfile`: Defines a Fedora 42 VM with port forwarding for development and testing
- `vagrant-provision.sh`: Shell script that installs Chef and runs the cookbooks in the Vagrant environment

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with the Vagrantfile using Fedora 42
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role from Galaxy or direct package installation
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` or `DavidWittman.redis` role

### Security Considerations

- **SSL Certificate Management**: 
  - The current implementation generates self-signed certificates
  - Migration approach: Use Ansible's `openssl_*` modules to generate certificates or integrate with Let's Encrypt using `geerlingguy.certbot`

- **Firewall Configuration**: 
  - Current implementation uses UFW
  - Migration approach: Use Ansible's `ufw` module or `firewalld` module depending on target OS

- **SSH Hardening**: 
  - Current implementation disables root login and password authentication
  - Migration approach: Use Ansible's `lineinfile` module or `ansible.posix.sshd` role

- **System Hardening**: 
  - Current implementation sets sysctl parameters
  - Migration approach: Use Ansible's `sysctl` module

- **Fail2ban Configuration**: 
  - Current implementation installs and configures fail2ban
  - Migration approach: Use Ansible's `fail2ban` module or a dedicated role like `geerlingguy.security`

- **Vault/secrets management**:
  - Redis password in `cookbooks/cache/recipes/default.rb`: "redis_secure_password_123"
  - PostgreSQL password in `cookbooks/fastapi-tutorial/recipes/default.rb`: "fastapi_password"
  - Migration approach: Move all credentials to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Replicating the dynamic site configuration from Chef attributes
  - Mitigation: Use Ansible's template module with Jinja2 templates and variable structures similar to the Chef attributes

- **SSL Certificate Generation**: 
  - Challenge: Ensuring certificates are only generated when needed
  - Mitigation: Use Ansible's `stat` module to check for existing certificates and `openssl_*` modules with `creates` parameter

- **Service Orchestration**: 
  - Challenge: Ensuring proper service restart only when configuration changes
  - Mitigation: Use Ansible handlers and notify mechanism similar to Chef's notifications

- **PostgreSQL User and Database Creation**: 
  - Challenge: Idempotent database setup
  - Mitigation: Use Ansible's `postgresql_*` modules with appropriate when conditions

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Implement security hardening
   - Configure virtual hosts

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Set up PostgreSQL database
   - Deploy FastAPI application
   - Configure systemd service

### Assumptions

1. The target environment will continue to use the same operating systems (Ubuntu/CentOS)
2. Self-signed certificates are acceptable for development, but production may require proper CA-signed certificates
3. The same security hardening measures are required in the Ansible implementation
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current Redis and Memcached configurations meet performance requirements and don't need optimization
6. The Vagrant development environment should be preserved with similar functionality
7. No CI/CD pipeline integration is required as part of the migration