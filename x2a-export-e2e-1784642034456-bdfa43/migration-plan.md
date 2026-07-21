# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration scope is moderate, consisting of three primary Chef cookbooks with dependencies on community cookbooks. Based on the complexity and size of the codebase, a migration timeline of 2-3 weeks is estimated, with the most complex component being the Nginx multi-site configuration with SSL.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate management, security hardening

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

**CRITICAL PATH VERIFICATION:**
All module paths have been verified to exist in the repository:
- cookbooks/nginx-multisite/recipes/default.rb exists and includes security, nginx, ssl, and sites recipes
- cookbooks/cache/recipes/default.rb exists and configures memcached and redis
- cookbooks/fastapi-tutorial/recipes/default.rb exists and deploys a FastAPI application

No Puppet modules (manifests/init.pp) or PowerShell modules (.psd1) were found in the repository.

### Infrastructure Files

- `Berksfile`: Manages cookbook dependencies, including community cookbooks like nginx, memcached, and redisio. Will need to be replaced with Ansible Galaxy requirements.
- `solo.json`: Contains node configuration including the run list and attributes for Nginx sites and security settings. Will be migrated to Ansible inventory variables.
- `solo.rb`: Chef configuration file that sets paths and log levels. Not needed in Ansible.
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef. Will need to be replaced with Ansible provisioning.
- `Vagrantfile`: Defines the development VM using Fedora 42. Will need updates to use Ansible provisioner instead of Chef.

### Target Details

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ based on cookbook metadata
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or the `ansible.posix.nginx` collection
- **memcached (~> 6.0)**: Replace with Ansible's `memcached` role or custom tasks
- **redisio (~> 7.2.4)**: Replace with Ansible's `redis` role or the `community.general.redis` module

### Security Considerations

- **SSL Certificate Management**: The nginx-multisite cookbook manages SSL certificates. Migration should preserve the certificate paths and configurations.
  - Migration approach: Use Ansible's `openssl_*` modules for certificate management
  
- **Redis Authentication**: Redis is configured with password authentication.
  - Migration approach: Use Ansible Vault to store the Redis password securely

- **PostgreSQL Credentials**: FastAPI application uses PostgreSQL with hardcoded credentials.
  - Migration approach: Move credentials to Ansible Vault and use template module for .env file

- **Security Hardening**: The nginx-multisite cookbook includes security configurations.
  - Migration approach: Use Ansible's security roles or implement equivalent tasks

- **Vault/secrets management**:
  - Hardcoded Redis password in cache/recipes/default.rb
  - Hardcoded PostgreSQL credentials in fastapi-tutorial/recipes/default.rb
  - Total credentials detected: 2 (Redis password, PostgreSQL user/password)

### Technical Challenges

- **Multi-site Nginx Configuration**: The nginx-multisite cookbook manages multiple virtual hosts with SSL. This will require careful templating in Ansible.
  - Mitigation: Create Jinja2 templates for Nginx configuration with proper variable substitution

- **Redis Configuration Hack**: The cache cookbook includes a Ruby block to modify Redis configuration files after they're created.
  - Mitigation: Use Ansible's lineinfile or template module with proper configuration from the start

- **FastAPI Application Deployment**: The deployment process involves Git, virtual environments, and systemd service configuration.
  - Mitigation: Use Ansible's git, pip, and systemd modules to replicate the deployment process

### Migration Order

1. **cache cookbook** (Low complexity): Simple installation and configuration of Memcached and Redis
2. **fastapi-tutorial cookbook** (Medium complexity): Application deployment with database setup
3. **nginx-multisite cookbook** (High complexity): Complex configuration with multiple sites and SSL

### Assumptions

1. The current Chef setup is functional and represents the desired end state
2. SSL certificates are self-signed for development purposes
3. The Nginx sites configuration in solo.json is complete and represents all required virtual hosts
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git is accessible and contains the expected code
5. The Redis configuration hack is necessary due to compatibility issues with the redisio cookbook
6. No custom Chef resources or libraries are being used that would require special handling
7. The target environment will continue to be Vagrant with libvirt for development
8. No CI/CD pipeline integration is currently in place that would need migration