# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration scope is moderate, consisting of three primary cookbooks with external dependencies. Based on the complexity and size of the codebase, an estimated timeline for migration would be 2-3 weeks with 1-2 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
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

- `Berksfile`: Manages cookbook dependencies, including local and external cookbooks from Chef Supermarket. Migration will require mapping these dependencies to Ansible Galaxy roles or collections.
- `solo.json`: Contains the run list and configuration data for Chef Solo. This will be migrated to Ansible inventory variables and group_vars.
- `solo.rb`: Chef Solo configuration file. Will be replaced by Ansible configuration.
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef. Will need to be updated to use Ansible provisioning.
- `Vagrantfile`: Defines the development VM configuration. Will need minor updates to use Ansible provisioner instead of Chef.

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ as indicated in cookbook metadata
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible community.nginx collection or geerlingguy.nginx role
- **memcached (~> 6.0)**: Replace with geerlingguy.memcached role
- **redisio (~> 7.2.4)**: Replace with geerlingguy.redis role or community.redis collection

### Security Considerations

- **SSL Configuration**: The nginx-multisite cookbook manages SSL certificates and private keys. Migration must ensure secure handling of these sensitive files.
- **Redis Authentication**: Redis is configured with password authentication (`requirepass` parameter). This credential should be stored in Ansible Vault.
- **PostgreSQL Credentials**: The FastAPI application uses PostgreSQL with hardcoded credentials. These should be migrated to Ansible Vault.
- **Security Hardening**: The nginx-multisite cookbook includes security configurations that must be preserved in the Ansible roles.
- **Vault/secrets management**:
  - Redis password in cache cookbook: 1 credential
  - PostgreSQL username/password in fastapi-tutorial cookbook: 2 credentials
  - SSL certificates and private keys referenced in nginx-multisite cookbook: Multiple files

### Technical Challenges

- **Multi-site Nginx Configuration**: The current setup dynamically generates Nginx site configurations based on node attributes. This pattern will need to be replicated using Ansible templates and variables.
- **Service Orchestration**: The current setup manages service dependencies (e.g., FastAPI depends on PostgreSQL). Ansible handlers and proper task ordering will be needed to maintain these dependencies.
- **Custom Ruby Logic**: The cache cookbook contains a ruby_block for modifying Redis configuration. This will need to be replaced with Ansible's lineinfile module or templates.
- **Python Environment Management**: The FastAPI application uses a Python virtual environment. This will need to be managed using Ansible's pip module with the virtualenv parameter.

### Migration Order

1. **nginx-multisite cookbook** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation and configuration
   - Implement SSL certificate management
   - Configure virtual hosts for multiple sites
   - Implement security hardening

2. **cache cookbook** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper service management

3. **fastapi-tutorial cookbook** (high complexity, application deployment)
   - Configure PostgreSQL database
   - Set up Python environment and dependencies
   - Deploy application code
   - Configure systemd service

### Assumptions

1. The current Chef setup is functional and represents the desired end state.
2. SSL certificates are self-signed for development purposes, as indicated in the Vagrant provisioning script.
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git is accessible and contains the expected code.
4. The target environment will continue to be Fedora-based, though the cookbooks support Ubuntu and CentOS as well.
5. The migration will maintain the same network configuration and port mappings as defined in the Vagrantfile.
6. No CI/CD pipeline integration is required as part of the migration, as none is present in the current setup.
7. The current setup appears to be for development/testing purposes rather than production, given the use of Vagrant and self-signed certificates.