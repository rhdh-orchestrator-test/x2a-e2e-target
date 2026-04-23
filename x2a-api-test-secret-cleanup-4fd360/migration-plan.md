# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Scope**: 3 Chef cookbooks with external dependencies
**Complexity**: Medium (standard web infrastructure with some security hardening)
**Timeline Estimate**: 2-3 weeks for complete migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and fail2ban/ufw firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, firewall configuration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file listing cookbook dependencies (nginx, memcached, redisio)
- `solo.json`: Chef configuration file defining the run list and node attributes
- `solo.rb`: Chef configuration file defining paths and log settings
- `Vagrantfile`: Defines a Fedora 42 VM for local development with port forwarding
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile) with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation and configuration
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package installation and configuration

### Security Considerations

- **SSL Certificate Management**: Self-signed certificates are generated for development; migration should maintain this capability or integrate with Let's Encrypt
- **Firewall Configuration**: UFW firewall rules need to be migrated to equivalent Ansible firewall module tasks
- **Fail2ban Configuration**: Fail2ban setup needs to be migrated to Ansible tasks
- **SSH Hardening**: SSH configuration hardening (disable root login, password authentication) needs to be preserved
- **Security Headers**: Nginx security headers configuration needs to be maintained
- **Vault/secrets management**:
  - Redis password in cache cookbook (hardcoded as 'redis_secure_password_123')
  - PostgreSQL database credentials in fastapi-tutorial cookbook (hardcoded as 'fastapi_password')
  - No Chef Vault or encrypted data bags detected

### Technical Challenges

- **Multi-site Configuration**: The dynamic generation of multiple Nginx site configurations will need careful translation to Ansible templates
- **Service Coordination**: The interdependencies between services (Nginx, Redis, Memcached, PostgreSQL, FastAPI) will need proper ordering in Ansible
- **SSL Certificate Generation**: The self-signed certificate generation logic will need to be replicated in Ansible
- **Firewall Configuration**: Ensuring idempotent firewall configuration in Ansible

### Migration Order

1. **cache** (Priority 1): Relatively simple cookbook with standard Redis and Memcached configuration
2. **nginx-multisite** (Priority 2): Core infrastructure component with moderate complexity
3. **fastapi-tutorial** (Priority 3): Application deployment with database dependencies

### Assumptions

1. The target environment will continue to be Fedora/CentOS/Ubuntu based systems
2. Self-signed certificates are acceptable for development (no production CA integration required)
3. The same security hardening measures should be maintained in the Ansible implementation
4. The current directory structure in the target environment (/opt/server/*, /etc/ssl/*) should be preserved
5. The FastAPI application source will continue to be pulled from the same Git repository
6. Redis and PostgreSQL passwords are development credentials and can be migrated as-is (though should be moved to Ansible Vault in production)
7. No custom Chef resources are used that would require special handling in Ansible