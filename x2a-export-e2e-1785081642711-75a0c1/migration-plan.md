# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated complexity is medium, with an estimated timeline of 2-3 weeks for a complete migration, including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies.
- `solo.json`: Chef Solo configuration file defining the run list and node attributes.
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and logging settings.
- `Vagrantfile`: Defines a Vagrant VM for development and testing with Fedora 42.
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development/testing

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible community.nginx collection or direct package installation
- **memcached (~> 6.0)**: Replace with Ansible community.general.memcached module
- **redisio (~> 7.2.4)**: Replace with Ansible community.redis collection or direct package installation

### Security Considerations

- **SSL Certificate Management**: Self-signed certificates are generated for development. Migration should maintain this capability while providing a path for production certificates.
- **Firewall Configuration**: UFW firewall rules need to be migrated to equivalent Ansible UFW module tasks.
- **fail2ban Configuration**: Fail2ban setup needs to be migrated to Ansible tasks.
- **SSH Hardening**: SSH security configurations (disabling root login, password authentication) need to be preserved.
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi`/`fastapi_password`)
  - No Chef Vault or encrypted data bags are used, simplifying migration

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple virtual hosts based on attributes will need careful translation to Ansible templates and variables.
- **Service Orchestration**: The current setup has interdependent services (Nginx, PostgreSQL, FastAPI application). Proper ordering and handlers will be needed in Ansible.
- **SSL Certificate Generation**: The self-signed certificate generation logic needs to be replicated in Ansible.
- **Configuration File Templating**: Multiple configuration templates will need to be converted from ERB to Jinja2 format.

### Migration Order

1. **cache role** (Priority 1, low complexity): Simple Redis and Memcached configuration with minimal dependencies.
2. **nginx-multisite role** (Priority 2, medium complexity): Core infrastructure component with security configurations.
3. **fastapi-tutorial role** (Priority 3, higher complexity): Application deployment with database dependencies.

### Assumptions

1. The target environment will continue to be Fedora-based systems (specifically Fedora 42 as indicated in the Vagrantfile).
2. Self-signed certificates are acceptable for the migrated solution (production deployment would require additional considerations).
3. The current security hardening approach (fail2ban, UFW, SSH configuration) is appropriate for the target environment.
4. The PostgreSQL database will continue to be deployed on the same host as the application.
5. The current Redis password and PostgreSQL credentials are development values that can be migrated as-is initially, but should be moved to Ansible Vault in the production version.
6. The Vagrant development environment will be maintained but converted to use Ansible provisioning instead of Chef.