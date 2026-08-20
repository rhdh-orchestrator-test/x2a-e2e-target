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
    - Key Features: Multi-site configuration, SSL certificate management, security hardening (fail2ban, ufw)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including external cookbooks from Chef Supermarket (nginx, memcached, redisio). Migration will require mapping these to Ansible Galaxy roles or collections.
- `solo.json`: Contains the run list and configuration data for Chef Solo. This will be migrated to Ansible inventory variables and group_vars.
- `solo.rb`: Chef Solo configuration file. Will be replaced by Ansible configuration.
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef. Will need to be updated to use Ansible provisioner.
- `Vagrantfile`: Defines the development VM. Will need updates to use Ansible provisioner instead of Chef.

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible community.nginx collection or geerlingguy.nginx role
- **memcached (~> 6.0)**: Replace with geerlingguy.memcached role
- **redisio (~> 7.2.4)**: Replace with geerlingguy.redis role or community.redis collection

### Security Considerations

- **SSL Certificate Management**: The nginx-multisite cookbook manages SSL certificates. Migration should preserve certificate paths and configurations.
  - Migration approach: Use Ansible's crypto modules for certificate management
  
- **Redis Authentication**: Redis is configured with password authentication.
  - Migration approach: Ensure Redis password is stored in Ansible Vault

- **Security Hardening**: The configuration includes fail2ban, ufw firewall, and SSH hardening.
  - Migration approach: Use dedicated Ansible security roles (e.g., dev-sec.ssh-hardening, dev-sec.nginx-hardening)

- **Vault/secrets management**:
  - Redis password hardcoded in the cache cookbook recipe
  - PostgreSQL credentials hardcoded in the FastAPI application recipe
  - Migration approach: Move all credentials to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The nginx-multisite cookbook manages multiple virtual hosts with SSL. 
  - Mitigation: Use Ansible templates to generate site configurations with similar structure

- **Redis Configuration Hack**: The cache cookbook includes a ruby_block to modify Redis configuration files after they're created.
  - Mitigation: Create custom Redis configuration template in Ansible to avoid post-configuration modifications

- **FastAPI Application Deployment**: The current setup clones a Git repository and sets up a Python environment.
  - Mitigation: Use Ansible's git module and pip module to replicate this functionality

### Migration Order

1. **cache cookbook** (low complexity, standalone functionality)
   - Implement Memcached and Redis configurations
   - Move Redis password to Ansible Vault

2. **nginx-multisite cookbook** (moderate complexity)
   - Implement Nginx installation and configuration
   - Configure SSL certificates
   - Set up security features (fail2ban, ufw)
   - Configure virtual hosts

3. **fastapi-tutorial cookbook** (high complexity, application deployment)
   - Set up PostgreSQL database
   - Deploy FastAPI application from Git
   - Configure Python virtual environment
   - Set up systemd service

### Assumptions

1. The current Chef setup is functional and represents the desired state for the Ansible migration
2. SSL certificates are self-signed for development (based on Vagrant setup)
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git is accessible and contains the expected code
4. The migration will maintain the same target OS support (Ubuntu 18.04+, CentOS 7+, Fedora)
5. The Vagrant development environment should be preserved with similar functionality
6. No CI/CD pipeline integration is required as part of the migration (none was present in the original)
7. The Redis configuration hack is necessary due to compatibility issues with the redisio cookbook
8. No monitoring or logging solutions are currently implemented that need migration