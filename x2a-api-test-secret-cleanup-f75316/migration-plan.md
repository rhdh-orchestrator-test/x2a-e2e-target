# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to Ansible roles and playbooks. The estimated complexity is moderate, with security configurations and multi-site SSL setup requiring careful attention.

**Timeline Estimate:**
- Planning and preparation: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and validation: 1-2 weeks
- Documentation and knowledge transfer: 1 week
- Total: 5-7 weeks

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and fail2ban/ufw configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, firewall configuration

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef run list and node attributes configuration
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Provisioning script for Vagrant environment
- `Vagrantfile`: Vagrant configuration for development environment using Fedora 42

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development/testing

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or collection (e.g., `geerlingguy.nginx`)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., `geerlingguy.memcached`)
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role (e.g., `geerlingguy.redis` or `DavidWittman.redis`)

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated in the Chef cookbook
  - Migration approach: Use Ansible's `openssl_*` modules or `community.crypto` collection

- **Firewall Configuration**: 
  - UFW is configured in the security recipe
  - Migration approach: Use Ansible's `ufw` module

- **Fail2ban Configuration**: 
  - Fail2ban is installed and configured
  - Migration approach: Use Ansible's `template` module for configuration files

- **SSH Hardening**: 
  - Root login and password authentication are disabled
  - Migration approach: Use Ansible's `lineinfile` module or dedicated SSH role

- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook
  - PostgreSQL password is hardcoded in the FastAPI cookbook
  - Migration approach: Use Ansible Vault for storing sensitive credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current setup dynamically generates Nginx site configurations for multiple domains
  - Mitigation: Use Ansible templates with loops to generate site configurations

- **SSL Certificate Generation**: 
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's `openssl_certificate` module with proper idempotency checks

- **Service Dependencies**: 
  - Description: The FastAPI application depends on PostgreSQL being configured first
  - Mitigation: Use Ansible handlers and proper task ordering

- **Redis Configuration Patching**: 
  - Description: The cache cookbook includes a hack to fix Redis configuration
  - Mitigation: Create a proper Redis configuration template in Ansible

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Create base Nginx role
   - Implement SSL certificate generation
   - Configure virtual hosts
   - Implement security hardening

2. **cache** (low complexity, standalone services)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, application deployment)
   - Implement PostgreSQL database setup
   - Configure Python environment
   - Deploy application code
   - Set up systemd service

### Assumptions

1. The target environment will continue to be Fedora 42 as specified in the Vagrantfile
2. Self-signed certificates are acceptable for the migrated solution
3. The same security hardening measures should be applied in the Ansible solution
4. The FastAPI application repository URL will remain accessible
5. The current Redis and Memcached configurations are sufficient for the application needs
6. No additional monitoring or logging solutions need to be implemented beyond what's in the current Chef setup
7. The Nginx sites configuration in solo.json overrides the default attributes in the cookbook
8. The current setup is for development/testing purposes, not production
9. No CI/CD integration is required for the Ansible migration
10. The current directory structure in the target system should be preserved