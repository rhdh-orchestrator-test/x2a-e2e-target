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
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment, Git repository deployment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies.
- `solo.json`: Chef configuration file containing the run list and node attributes.
- `solo.rb`: Chef configuration file specifying cookbook paths and log settings.
- `Vagrantfile`: Defines a Fedora 42 VM with port forwarding for development/testing.
- `vagrant-provision.sh`: Shell script that installs Chef and runs the cookbooks in the Vagrant environment.

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used for development in Vagrant
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct configuration

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration approach: Use Ansible's openssl_* modules or community.crypto collection

- **Firewall Configuration**: 
  - UFW is configured to allow only SSH, HTTP, and HTTPS
  - Migration approach: Use Ansible's ufw module or firewalld module depending on target OS

- **SSH Hardening**: 
  - Root login disabled
  - Password authentication disabled
  - Migration approach: Use Ansible's lineinfile module or ssh_config module

- **System Hardening**: 
  - Sysctl security parameters
  - Migration approach: Use Ansible's sysctl module

- **Fail2ban Configuration**: 
  - Configured to protect services
  - Migration approach: Use Ansible's template module or community.general.fail2ban module

- **Vault/secrets management**:
  - Redis password hardcoded in recipe (redis_secure_password_123)
  - PostgreSQL password hardcoded in recipe (fastapi_password)
  - Database connection string with credentials in .env file
  - Count: 3 hardcoded credentials identified

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation dynamically generates site configurations based on node attributes
  - Mitigation: Use Ansible loops with templates to achieve similar functionality

- **SSL Certificate Generation**: 
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's openssl_* modules to generate certificates or integrate with Let's Encrypt

- **Redis Configuration Hack**: 
  - Description: The current implementation includes a ruby_block to modify Redis configuration
  - Mitigation: Create proper Redis configuration template in Ansible

- **PostgreSQL User and Database Creation**: 
  - Description: Uses shell commands to create database and user
  - Mitigation: Use Ansible's postgresql_* modules for cleaner implementation

### Migration Order

1. **cache cookbook** (Priority 1 - low complexity)
   - Simple configuration of Memcached and Redis
   - Few dependencies
   - Good starting point to establish patterns

2. **nginx-multisite cookbook** (Priority 2 - medium complexity)
   - Core infrastructure component
   - Security configurations
   - Multiple templates and configurations

3. **fastapi-tutorial cookbook** (Priority 3 - higher complexity)
   - Application deployment
   - Database configuration
   - Service management

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based systems
2. Self-signed certificates are acceptable for the migrated solution (vs. Let's Encrypt integration)
3. The same security hardening requirements will apply in the new environment
4. The FastAPI application repository will remain available at the same URL
5. The Vagrant development environment will be replaced with an Ansible-compatible alternative
6. No specific CI/CD integration requirements are specified for the Ansible migration
7. The current Redis and PostgreSQL passwords are development values that should be replaced with Ansible Vault in production
8. The current directory structure in the target environment (/opt/server/*, /var/www/*) should be maintained