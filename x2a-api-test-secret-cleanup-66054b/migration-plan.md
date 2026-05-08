# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application with PostgreSQL. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. Based on the complexity and dependencies, this migration is estimated to take 2-3 weeks for a skilled Ansible developer.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall), sysctl security settings

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints.
- `Vagrantfile`: Defines a Fedora 42 VM with networking and provisioning configuration for local development.
- `solo.json`: Chef run list and configuration attributes including Nginx site configurations and security settings.
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings.
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM, installing Chef and Berkshelf, and running Chef Solo.

### Target Details

- **Operating System**: Fedora 42 (primary), with support for Ubuntu 18.04+ and CentOS 7+ based on cookbook metadata
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role or direct configuration tasks

### Security Considerations

- **SSL Certificate Management**: The current setup generates self-signed certificates. Migration should maintain this capability while allowing for integration with Let's Encrypt or other certificate providers.
- **Firewall Configuration**: UFW firewall rules need to be migrated to equivalent Ansible UFW module tasks.
- **Fail2ban Configuration**: Fail2ban setup needs to be migrated to Ansible tasks.
- **SSH Hardening**: SSH security configurations (disabling root login, password authentication) need to be preserved.
- **Vault/secrets management**:
  - Redis password in cache cookbook (hardcoded as 'redis_secure_password_123')
  - PostgreSQL database credentials in fastapi-tutorial cookbook (hardcoded as 'fastapi_password')
  - No Chef Vault or encrypted data bags detected, but passwords are hardcoded in recipes

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple Nginx site configurations based on attributes will need careful translation to Ansible templates and variables.
- **SSL Certificate Generation**: Self-signed certificate generation logic needs to be preserved while allowing for future enhancements.
- **Redis Configuration**: The Redis configuration includes a workaround/hack to fix configuration files after deployment, which will need special attention.
- **FastAPI Deployment**: The Python virtual environment setup and application deployment will require careful migration to ensure proper dependency management.

### Migration Order

1. **nginx-multisite** (Priority 1): Core infrastructure component that other services depend on
2. **cache** (Priority 2): Supporting services that the application may depend on
3. **fastapi-tutorial** (Priority 3): Application deployment that depends on the infrastructure

### Assumptions

1. The target environment will continue to be Fedora 42 or similar Linux distributions.
2. Self-signed certificates are acceptable for development/testing purposes.
3. The current security configurations (fail2ban, UFW, SSH hardening) are appropriate for the target environment.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The hardcoded credentials in the recipes are for development purposes and will be replaced with more secure methods in production.
6. The Nginx sites configuration in solo.json overrides the default attributes in the cookbook.
7. No custom resources or libraries are used beyond what's visible in the repository structure.