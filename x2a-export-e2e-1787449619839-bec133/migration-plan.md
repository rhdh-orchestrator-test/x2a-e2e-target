# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration scope is moderate, consisting of three primary cookbooks with external dependencies. Based on the complexity and size, a migration timeline of 2-3 weeks is estimated with a team of 2 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and SSL certificate management
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup, security hardening

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database provisioning, systemd service configuration

### Infrastructure Files

- `Berksfile`: Manages cookbook dependencies, including local and external cookbooks from Chef Supermarket. Migration will require mapping these dependencies to Ansible Galaxy roles or collections.
- `solo.json`: Contains the run list and configuration data for Chef Solo. This will be migrated to Ansible inventory variables and group_vars.
- `solo.rb`: Chef Solo configuration file. Will be replaced by Ansible configuration.
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef. Will need to be updated to use Ansible provisioner.
- `Vagrantfile`: Defines the development VM using Fedora 42. Will need updates to use Ansible provisioner instead of Chef.

### Target Details

Based on the source configuration files:

- **Operating System**: Supports Ubuntu 18.04+ and CentOS 7+, with Fedora 42 used in the Vagrant development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible community.nginx collection or geerlingguy.nginx role
- **memcached (~> 6.0)**: Replace with geerlingguy.memcached role
- **redisio (~> 7.2.4)**: Replace with geerlingguy.redis role or community.redis collection

### Security Considerations

- **SSL/TLS Configuration**: The nginx-multisite cookbook manages SSL certificates and private keys. Migration should ensure secure handling of certificates using Ansible Vault.
- **Redis Authentication**: Redis is configured with password authentication (`requirepass` parameter). This password should be stored in Ansible Vault.
- **Security Hardening**: The nginx-multisite cookbook includes security hardening (fail2ban, ufw, SSH hardening). These configurations should be migrated to appropriate Ansible roles.
- **Vault/secrets management**: 
  - Redis password in cache cookbook (plaintext in recipe)
  - FastAPI PostgreSQL credentials in fastapi-tutorial cookbook (plaintext in recipe)
  - Total credentials detected: 2 database passwords in plaintext

### Technical Challenges

- **Multi-site Nginx Configuration**: The nginx-multisite cookbook manages multiple virtual hosts with SSL. This will require careful migration to ensure all sites are properly configured in Ansible.
- **Redis Configuration Customization**: The cache cookbook includes a custom Ruby block to modify Redis configuration. This will need to be reimplemented using Ansible templates or lineinfile modules.
- **FastAPI Application Deployment**: The fastapi-tutorial cookbook clones a Git repository and sets up a Python virtual environment. This workflow will need to be recreated using Ansible's git, pip, and template modules.

### Migration Order

1. **cache cookbook** (low complexity, standalone service)
   - Implement Memcached and Redis configuration using community roles
   - Secure Redis password using Ansible Vault

2. **nginx-multisite cookbook** (moderate complexity)
   - Implement Nginx installation and configuration
   - Configure SSL certificates and virtual hosts
   - Implement security hardening features

3. **fastapi-tutorial cookbook** (high complexity)
   - Set up PostgreSQL database
   - Deploy FastAPI application
   - Configure systemd service

### Assumptions

1. The current Chef setup is functional and represents the desired end state
2. No major architectural changes are required during migration
3. SSL certificates are self-signed for development (based on Vagrant setup)
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git is accessible and will remain available
5. The migration will maintain support for both Ubuntu and CentOS/RHEL systems
6. The Vagrant development environment will continue to be used for testing
7. No CI/CD pipeline integration is currently implemented
8. No monitoring or logging solutions are currently configured beyond basic system services