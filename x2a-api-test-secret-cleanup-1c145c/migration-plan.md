# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks, handling external dependencies, and ensuring proper security configurations are maintained. Based on the complexity and scope, this migration is estimated to require 3-4 weeks with 1-2 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and proper SSL configuration
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
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration file for local development environment using Fedora 42

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or local development

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct configuration

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for development
  - Migration should maintain or improve certificate security
  - Consider using Ansible crypto modules for certificate generation

- **Firewall Configuration**: 
  - UFW firewall rules need to be migrated to Ansible ufw module
  - Maintain existing allowed services (SSH, HTTP, HTTPS)

- **Fail2ban Integration**:
  - Convert fail2ban configuration to Ansible tasks
  - Maintain jail configurations

- **SSH Hardening**:
  - Maintain root login restrictions
  - Maintain password authentication restrictions

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL password is hardcoded in the recipe (`fastapi_password`)
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - The Chef cookbook uses templates to generate site configurations dynamically
  - Ansible will need to replicate this dynamic template generation based on variables

- **Service Dependencies**: 
  - FastAPI application depends on PostgreSQL
  - Ensure proper ordering of service installation and configuration in Ansible

- **SSL Certificate Generation**:
  - Chef generates self-signed certificates with OpenSSL
  - Ansible will need to replicate this or improve with Let's Encrypt integration

### Migration Order

1. **nginx-multisite cookbook** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security configurations that should be established first

2. **cache cookbook** (Priority 2)
   - Relatively simple configuration with external dependencies
   - Services that may be used by the application

3. **fastapi-tutorial cookbook** (Priority 3)
   - Application deployment that depends on other infrastructure
   - Contains database configuration and application-specific settings

### Assumptions

1. The target environment will continue to be Fedora-based systems
2. Self-signed certificates are acceptable for development environments
3. The same security practices should be maintained in the Ansible implementation
4. The FastAPI application repository will remain available at the specified URL
5. The current network configuration and port mappings should be preserved
6. Redis and PostgreSQL passwords in the current implementation are for development only and will be replaced with secure passwords in production
7. The current directory structure in the target system should be maintained