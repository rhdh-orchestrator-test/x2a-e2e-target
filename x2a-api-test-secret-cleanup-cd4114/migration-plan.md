# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Scope**: 3 Chef cookbooks with external dependencies
**Complexity**: Medium (standard web stack with some security configurations)
**Timeline Estimate**: 2-3 weeks for complete migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificates
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall)

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef Solo configuration with run list and node attributes
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration for local development using Fedora 42

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in Vagrant
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role or direct package installation

### Security Considerations

- **SSL Certificate Management**: Self-signed certificates are generated for each site; migrate to Ansible crypto modules
- **Firewall Configuration**: UFW firewall rules need to be migrated to Ansible ufw module
- **Fail2ban Setup**: Fail2ban configuration needs to be migrated to Ansible
- **SSH Hardening**: SSH security settings (disable root login, password authentication) need to be migrated
- **Vault/secrets management**: 
  - Redis password hardcoded in attributes (`redis_secure_password_123`)
  - PostgreSQL credentials hardcoded in recipe (`fastapi:fastapi_password`)
  - Total credentials detected: 2 (should be moved to Ansible Vault)

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple virtual hosts with SSL needs careful translation to Ansible templates
- **Redis Configuration Hack**: The cookbook includes a Ruby block to modify Redis configuration files after installation, which will need a different approach in Ansible
- **Service Dependencies**: Ensuring proper service ordering and dependencies in Ansible (e.g., FastAPI depends on PostgreSQL)

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Create Ansible role for Nginx installation and configuration
   - Create templates for virtual hosts and SSL configuration
   - Implement security hardening (fail2ban, ufw)

2. **cache** (low complexity, standalone service)
   - Create Ansible roles for Memcached and Redis
   - Implement Redis authentication using Ansible Vault for password storage

3. **fastapi-tutorial** (high complexity, application deployment)
   - Create Ansible role for Python application deployment
   - Implement PostgreSQL database setup
   - Configure systemd service

### Assumptions

1. The target environment will continue to be either Ubuntu (>= 18.04) or CentOS (>= 7.0)
2. The Vagrant development environment will be maintained but converted to use Ansible provisioner
3. Self-signed certificates are acceptable for development (not production)
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current security configurations are appropriate for the target environment
6. No changes to the application architecture are required during migration
7. The current Redis configuration hack is necessary due to compatibility issues that may need investigation
8. The current directory structure in the target environment (/opt/fastapi-tutorial, /var/www/sites) will be maintained