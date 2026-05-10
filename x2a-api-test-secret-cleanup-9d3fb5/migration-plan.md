# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated complexity is moderate, with security configurations and multiple service integrations requiring careful attention.

**Timeline Estimate:**
- Planning & Setup: 1 week
- Core Infrastructure Migration: 2 weeks
- Testing & Validation: 1 week
- Documentation & Knowledge Transfer: 1 week
- **Total**: 5 weeks

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and fail2ban integration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, firewall configuration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password protection, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database provisioning, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file listing cookbook dependencies (both local and external)
- `solo.json`: Chef configuration file defining the run list and node attributes
- `solo.rb`: Chef configuration file defining paths and log settings
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration for development environment using Fedora 42

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in the Vagrant development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks
- **PostgreSQL**: Replace with Ansible postgresql_* modules or community.postgresql collection

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration approach: Use Ansible's openssl_* modules or community.crypto collection

- **Firewall Configuration**: 
  - UFW is configured with specific rules
  - Migration approach: Use Ansible's ufw module or firewalld module depending on target OS

- **Fail2ban Integration**: 
  - Fail2ban is configured for intrusion prevention
  - Migration approach: Use Ansible's template module for fail2ban configuration

- **SSH Hardening**: 
  - Root login disabled and password authentication disabled
  - Migration approach: Use Ansible's lineinfile module or ssh_config module

- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook
  - PostgreSQL password is hardcoded in the fastapi-tutorial cookbook
  - Migration approach: Use Ansible Vault for storing sensitive credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current setup dynamically generates Nginx site configurations for multiple domains
  - Mitigation: Use Ansible templates with loops to generate site configurations, similar to the current Chef approach

- **SSL Certificate Generation**: 
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's openssl_* modules to generate certificates or integrate with Let's Encrypt via certbot

- **Service Orchestration**: 
  - Description: Multiple interdependent services (Nginx, Redis, Memcached, PostgreSQL, FastAPI application)
  - Mitigation: Use Ansible handlers and proper dependency management to ensure services are restarted in the correct order

- **Python Application Deployment**: 
  - Description: Python virtual environment setup and application deployment from Git
  - Mitigation: Use Ansible's git, pip, and template modules to replicate the deployment process

### Migration Order

1. **cache** (Priority 1): 
   - Low complexity, minimal dependencies
   - Provides foundation for other services

2. **nginx-multisite** (Priority 2): 
   - Moderate complexity
   - Core infrastructure component

3. **fastapi-tutorial** (Priority 3): 
   - Higher complexity due to application deployment and database integration
   - Depends on PostgreSQL configuration

### Assumptions

1. The target environment will continue to support the same operating systems (Ubuntu 18.04+ or CentOS 7.0+)
2. The Vagrant development environment will be maintained for testing
3. Self-signed certificates are acceptable for development/testing (production would likely use proper certificates)
4. The current security configurations are appropriate and should be maintained in the Ansible implementation
5. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
6. The current Redis password and PostgreSQL credentials will be migrated to Ansible Vault
7. The current directory structure for web content and application files will be maintained
8. No changes to the application configuration or behavior are required as part of the migration