# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with FastAPI application backend and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- Total: 5-6 weeks

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
- `solo.json`: Configuration data for Chef Solo, contains site configurations and security settings.
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings.
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef.
- `Vagrantfile`: Vagrant configuration for development environment using Fedora 42.

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (18.04+) and CentOS (7.0+), with Fedora 42 used in the Vagrant development environment.
- **Virtual Machine Technology**: Vagrant with libvirt provider (based on Vagrantfile configuration).
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.nginx collection
- **memcached (~> 6.0)**: Replace with Ansible memcached role or community.general.memcached module
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or community.redis collection

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration approach: Use Ansible's openssl_* modules or community.crypto collection

- **Firewall Configuration**: 
  - UFW is configured with default deny and specific allow rules
  - Migration approach: Use Ansible's ufw module or firewalld module depending on target OS

- **Fail2ban Configuration**: 
  - Fail2ban is installed and configured for SSH protection
  - Migration approach: Use Ansible's community.general.fail2ban module

- **SSH Hardening**: 
  - Root login disabled and password authentication disabled
  - Migration approach: Use Ansible's openssh_config module or security role

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (redis_secure_password_123)
  - PostgreSQL password is hardcoded in the recipe (fastapi_password)
  - Migration approach: Use Ansible Vault for storing sensitive credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Chef iterates through node attributes to create multiple virtual hosts
  - Migration strategy: Use Ansible loops with templates to achieve the same functionality

- **SSL Certificate Generation**: 
  - Self-signed certificates are generated with OpenSSL commands
  - Migration strategy: Use Ansible's openssl_* modules for certificate generation

- **Service Dependencies**: 
  - FastAPI service depends on PostgreSQL
  - Migration strategy: Use Ansible handlers and meta dependencies to ensure proper ordering

### Migration Order

1. **cache cookbook** (low complexity, standalone)
   - Implement Memcached and Redis roles
   - Secure Redis password with Ansible Vault

2. **nginx-multisite cookbook** (medium complexity)
   - Implement Nginx installation and configuration
   - Implement SSL certificate generation
   - Implement security hardening (fail2ban, ufw)
   - Implement virtual host configuration

3. **fastapi-tutorial cookbook** (medium complexity, has dependencies)
   - Implement PostgreSQL database setup
   - Implement Python application deployment
   - Implement systemd service configuration

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based systems.
2. The Vagrant development environment will be maintained for testing.
3. Self-signed certificates are acceptable for development; production may require proper certificates.
4. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate for the target environment.
5. The FastAPI application source will continue to be pulled from the same Git repository.
6. The current Redis and PostgreSQL passwords are development passwords and will be replaced with proper secrets management.
7. The current directory structure and file organization will be maintained in the Ansible roles.