# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration scope is moderate, consisting of three primary cookbooks with external dependencies. Based on the complexity and size, an estimated timeline of 2-3 weeks would be reasonable for a complete migration to Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and SSL certificate management
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL setup, security hardening

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

- `Berksfile`: Manages Chef cookbook dependencies, including local and external cookbooks. Migration will require mapping these dependencies to Ansible Galaxy roles or collections.
- `solo.json`: Contains Chef node attributes and run list. This will be migrated to Ansible inventory variables and playbook structure.
- `solo.rb`: Chef Solo configuration file. Will be replaced by Ansible configuration.
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef. Will need to be updated to use Ansible provisioning.
- `Vagrantfile`: Defines the development VM configuration. Will need minor updates to use Ansible provisioner instead of Chef.

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible community.nginx collection or geerlingguy.nginx role
- **memcached (~> 6.0)**: Replace with geerlingguy.memcached role
- **redisio (~> 7.2.4)**: Replace with geerlingguy.redis role or community.redis collection

### Security Considerations

- **SSL Certificate Management**: The nginx-multisite cookbook manages SSL certificates. Migration should preserve the certificate paths and configurations.
  - Migration approach: Use Ansible's crypto modules for certificate management
  
- **Redis Authentication**: Redis is configured with password authentication.
  - Migration approach: Ensure Redis password is stored securely in Ansible Vault

- **Security Hardening**: The nginx-multisite cookbook includes security hardening via the security.rb recipe.
  - Migration approach: Implement equivalent security measures using Ansible hardening roles

- **Vault/secrets management**:
  - Hardcoded Redis password in cache/recipes/default.rb: "redis_secure_password_123"
  - Hardcoded PostgreSQL password in fastapi-tutorial/recipes/default.rb: "fastapi_password"
  - Database connection string in .env file with embedded credentials
  - Total credentials detected: 3 (all hardcoded in recipes)

### Technical Challenges

- **Multi-site Nginx Configuration**: The nginx-multisite cookbook manages multiple virtual hosts with SSL. This will require careful migration to ensure all sites are properly configured.
  - Mitigation: Use Ansible templates to generate Nginx site configurations, similar to the Chef approach

- **Redis Configuration Customization**: The cache cookbook includes a ruby_block to modify Redis configuration files after they're created.
  - Mitigation: Use Ansible's lineinfile or template modules to achieve the same configuration modifications

- **FastAPI Application Deployment**: The fastapi-tutorial cookbook clones a Git repository and sets up a Python environment.
  - Mitigation: Use Ansible's git, pip, and template modules to replicate this functionality

### Migration Order

1. **cache cookbook** (low risk, standalone service)
   - Implement Memcached and Redis configuration
   - Ensure Redis authentication is properly configured

2. **nginx-multisite cookbook** (moderate complexity)
   - Implement base Nginx installation
   - Configure SSL certificates
   - Set up virtual hosts
   - Implement security hardening

3. **fastapi-tutorial cookbook** (high complexity, dependencies)
   - Set up PostgreSQL database
   - Deploy FastAPI application
   - Configure systemd service

### Assumptions

1. The current Chef setup is functional and represents the desired end state
2. No changes to the application architecture are required during migration
3. The same VM/server configuration will be maintained
4. SSL certificates are self-signed for development (based on Vagrant setup)
5. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git is accessible and contains the expected code
6. The Redis configuration hack in the cache cookbook is necessary due to compatibility issues with the redisio cookbook
7. No custom Chef resources or libraries are being used that would require special handling
8. The migration will maintain the same security posture as the current implementation
9. No CI/CD pipeline integration is required as part of the migration