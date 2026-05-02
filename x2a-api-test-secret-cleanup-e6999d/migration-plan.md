# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks, handling external dependencies, and ensuring proper security configurations are maintained.

**Scope**: 3 Chef cookbooks with external dependencies
**Complexity**: Medium
**Estimated Timeline**: 3-4 weeks

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, fail2ban integration, UFW firewall configuration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef configuration file containing the run list and node attributes
- `solo.rb`: Chef configuration file specifying cookbook paths and log settings
- `Vagrantfile`: Defines the development VM configuration using Fedora 42
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)
- **PostgreSQL**: Replace with Ansible PostgreSQL role (e.g., geerlingguy.postgresql)

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for development
  - Migration should maintain the same security parameters (TLS 1.2/1.3, strong ciphers)
  - Consider integrating with Ansible's crypto modules for certificate generation

- **Firewall Configuration**:
  - UFW firewall rules need to be migrated to appropriate Ansible UFW module
  - Default deny policy with specific allows for SSH, HTTP, HTTPS

- **Fail2ban Integration**:
  - Fail2ban configuration needs to be migrated to Ansible
  - Maintain jail configurations for SSH and web services

- **SSH Hardening**:
  - Root login disabled
  - Password authentication disabled
  - These configurations need to be maintained in Ansible

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL password is hardcoded in the recipe (`fastapi_password`)
  - These should be migrated to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - The Chef cookbook dynamically generates site configurations based on node attributes
  - Ansible will need to use templates and loops to achieve the same functionality
  - Security headers and SSL configurations must be preserved

- **Service Orchestration**:
  - The current setup has interdependent services (Nginx, Redis, Memcached, PostgreSQL, FastAPI)
  - Ansible will need to handle service dependencies and proper restart notifications

- **Python Application Deployment**:
  - Virtual environment setup and package installation
  - Environment file configuration with database connection details
  - Systemd service management

### Migration Order

1. **cache cookbook** (Low complexity, foundational services)
   - Implement Memcached configuration
   - Implement Redis configuration with authentication

2. **fastapi-tutorial cookbook** (Medium complexity)
   - PostgreSQL database setup
   - Python application deployment
   - Environment configuration
   - Systemd service setup

3. **nginx-multisite cookbook** (High complexity)
   - Base Nginx configuration
   - SSL certificate generation
   - Virtual host configuration
   - Security hardening (headers, fail2ban, firewall)

### Assumptions

1. The target environment will continue to be Fedora-based systems, with potential support for Ubuntu and CentOS
2. Self-signed certificates are acceptable for development, but production may require integration with Let's Encrypt or other certificate providers
3. The security configurations (firewall, fail2ban, SSH hardening) are required in the migrated solution
4. The current Redis and PostgreSQL passwords are development passwords and will be replaced with secure passwords in Ansible Vault
5. The FastAPI application source will continue to be pulled from the same Git repository
6. The Nginx configuration will maintain the same security headers and SSL parameters
7. The current directory structure in the target system (/opt/fastapi-tutorial, /var/www/sites) will be maintained