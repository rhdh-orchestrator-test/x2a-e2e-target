# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This migration plan outlines the process of converting a Chef-based infrastructure to Ansible. The repository contains three Chef cookbooks managing a multi-site Nginx setup, caching services (Redis and Memcached), and a FastAPI Python application with PostgreSQL. The estimated complexity is medium, with an approximate timeline of 3-4 weeks for complete migration, including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificates
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall)

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

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef Solo configuration file containing the run list and node attributes
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `Vagrantfile`: Defines a Fedora 42 VM for local development and testing
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used for development
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package module
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package module with custom configuration

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each virtual host
  - Migration approach: Use Ansible's openssl_* modules or community.crypto collection

- **Firewall Configuration**: 
  - UFW firewall is configured with specific rules
  - Migration approach: Use Ansible's ufw module or firewalld module depending on target OS

- **Fail2ban Integration**: 
  - Fail2ban is configured for intrusion prevention
  - Migration approach: Use Ansible's template module with fail2ban configuration templates

- **SSH Hardening**: 
  - Root login disabled and password authentication disabled
  - Migration approach: Use Ansible's lineinfile module or ssh_config module

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the FastAPI recipe (`fastapi:fastapi_password`)
  - Migration approach: Use Ansible Vault for storing sensitive credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current setup dynamically creates multiple virtual hosts with SSL
  - Mitigation: Use Ansible's template module with Jinja2 templates to generate site configurations

- **Self-signed Certificate Generation**: 
  - Description: Custom SSL certificates are generated for each site
  - Mitigation: Use Ansible's openssl_certificate module to generate certificates

- **Redis Configuration Patching**: 
  - Description: The current setup uses a Ruby block to modify Redis configuration
  - Mitigation: Create a custom Redis configuration template in Ansible

- **PostgreSQL User and Database Creation**: 
  - Description: PostgreSQL users and databases are created with direct commands
  - Mitigation: Use Ansible's postgresql_* modules from the community.postgresql collection

### Migration Order

1. **cache cookbook** (Priority 1 - Low complexity)
   - Simple package installations and configuration files
   - Few dependencies on other components

2. **nginx-multisite cookbook** (Priority 2 - Medium complexity)
   - Core infrastructure component with security implications
   - Multiple templates and configuration files

3. **fastapi-tutorial cookbook** (Priority 3 - Higher complexity)
   - Application deployment with database dependencies
   - Requires both the web server and database to be configured first

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based systems
2. The Vagrant development environment will be maintained for testing
3. Self-signed certificates are acceptable (no integration with Let's Encrypt or commercial CA)
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current security configurations (fail2ban, UFW, SSH hardening) are required in the migrated solution
6. Redis authentication will continue to be used in the new environment
7. The PostgreSQL database structure will remain unchanged
8. The current directory structure for web content (/var/www/[site]) will be maintained