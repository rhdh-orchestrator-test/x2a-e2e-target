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
- Standard web server configuration patterns
- Moderate number of dependencies
- Security configurations that need careful migration
- Self-signed SSL certificates that need proper handling

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and SSL certificate management
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup, security hardening (fail2ban, ufw firewall)

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Chef dependency manager file listing cookbook dependencies (nginx, memcached, redisio)
- `solo.json`: Chef configuration file with run list and node attributes
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Shell script for provisioning Chef in Vagrant VM
- `Vagrantfile`: Vagrant configuration for development environment using Fedora 42

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or local development

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package module
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package module with custom configuration

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW firewall rules that need to be migrated to Ansible's ufw module
- **Fail2ban Setup**: Fail2ban configuration needs to be migrated using Ansible's template module
- **SSH Hardening**: SSH security configurations (disabling root login, password authentication) need to be migrated
- **SSL/TLS Management**: Self-signed certificate generation needs to be handled with Ansible's openssl_* modules
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL database credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - No Chef Vault or encrypted data bags are used, simplifying migration

### Technical Challenges

- **SSL Certificate Generation**: The current setup generates self-signed certificates. Ansible has built-in modules for this, but the workflow needs careful migration.
- **Multi-site Configuration**: The dynamic generation of Nginx site configurations based on node attributes needs to be replicated in Ansible using loops and templates.
- **Service Dependencies**: Ensuring proper ordering of service installation, configuration, and startup in Ansible.
- **PostgreSQL User/Database Creation**: The current implementation uses direct shell commands via execute resources, which should be replaced with Ansible's postgresql_* modules.

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security configurations that should be established first

2. **cache** (Priority 2)
   - Supporting service with external dependencies (memcached, redis)
   - Moderate complexity with authentication requirements

3. **fastapi-tutorial** (Priority 3)
   - Application-specific configuration that depends on web server
   - Involves database setup and application deployment

### Assumptions

1. The target environment will continue to be Vagrant-based for development/testing
2. Self-signed certificates are acceptable (not using Let's Encrypt or commercial certificates)
3. The same security hardening approach will be maintained
4. No changes to the application architecture are planned during migration
5. PostgreSQL will continue to be used as the database backend
6. The FastAPI application will be deployed from the same GitHub repository
7. Redis and Memcached configurations will remain functionally equivalent
8. No high availability or clustering requirements exist