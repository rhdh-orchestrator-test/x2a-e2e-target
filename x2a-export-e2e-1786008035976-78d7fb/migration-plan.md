# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, configuration templates, and security settings. Based on the complexity and scope, this migration is estimated to be a medium-sized project requiring approximately 3-4 weeks for a complete transition.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site virtual hosts, SSL certificate generation, security hardening with fail2ban and UFW, sysctl security configurations

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef node configuration with run list and attribute overrides
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Defines development VM with Fedora 42, network configuration, and provisioning
- `vagrant-provision.sh`: Shell script for Chef installation and execution in Vagrant environment

### Target Details

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ based on cookbook metadata
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or community.general.memcached module
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or community.general.redis module

### Security Considerations

- **Firewall Configuration**: UFW rules need to be migrated to appropriate firewall modules (firewalld for Fedora)
- **fail2ban Setup**: Configuration needs to be migrated to Ansible fail2ban role
- **SSH Hardening**: SSH configuration hardening (disable root login, password authentication)
- **Vault/secrets management**:
  - Redis password in cache cookbook: `redis_secure_password_123`
  - PostgreSQL credentials in fastapi-tutorial cookbook: `fastapi:fastapi_password`
  - Self-signed SSL certificates generated in nginx-multisite cookbook
  - Environment variables in .env file for FastAPI application

### Technical Challenges

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Consider using Ansible's crypto modules or certbot for Let's Encrypt integration
- **Multi-site Configuration**: The dynamic generation of site configurations based on node attributes needs to be carefully migrated to Ansible's template system
- **Service Dependencies**: Ensuring proper ordering of service installations and configurations, particularly for the FastAPI application which depends on PostgreSQL
- **Security Hardening**: Comprehensive security configurations need to be maintained across the migration

### Migration Order

1. **nginx-multisite cookbook** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security configurations that should be established first

2. **cache cookbook** (Priority 2)
   - Relatively simple configuration with external dependencies
   - Required by the application but less complex than the application itself

3. **fastapi-tutorial cookbook** (Priority 3)
   - Most complex component with multiple dependencies
   - Depends on both nginx and potentially cache services

### Assumptions

1. The current Chef setup is functional and represents the desired end state
2. The target environment will continue to be Fedora-based systems
3. Self-signed certificates are acceptable for the migrated solution (or will be replaced with proper certificates)
4. The same directory structure and file paths will be maintained in the Ansible version
5. Vagrant will continue to be used for development/testing
6. No changes to the application code or database schema are required
7. Hard-coded credentials in the current implementation will be replaced with Ansible Vault or another secure solution
8. The migration will maintain the same level of security hardening present in the Chef implementation