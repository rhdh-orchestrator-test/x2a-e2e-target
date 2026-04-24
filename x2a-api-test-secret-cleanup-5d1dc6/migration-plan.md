# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup with three main cookbooks: nginx-multisite, cache, and fastapi-tutorial. The migration to Ansible will involve converting these cookbooks to Ansible roles and playbooks, preserving the functionality while adapting to Ansible's declarative approach.

**Scope**: 3 Chef cookbooks with dependencies on external cookbooks
**Complexity**: Medium (standard web server, caching, and application deployment patterns)
**Timeline Estimate**: 2-3 weeks (1 week per cookbook with testing)

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, depends on external cookbooks

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks, lists both local and external cookbook dependencies
- `solo.json`: Chef configuration file defining the run list and node attributes
- `solo.rb`: Chef configuration file defining paths and log settings
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Defines the Vagrant VM configuration (Fedora 42) with port forwarding and networking

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting local development/testing environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or direct package installation
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached` or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or direct package installation

### Security Considerations

- **SSL Certificate Management**: 
  - Migration approach: Use Ansible's `openssl_*` modules to generate self-signed certificates
  - Consider integration with `community.crypto` collection for certificate management

- **Firewall Configuration (UFW)**:
  - Migration approach: Use Ansible's `ufw` module to configure firewall rules

- **Fail2ban Configuration**:
  - Migration approach: Use Ansible to install and configure fail2ban with templates

- **SSH Hardening**:
  - Migration approach: Use Ansible's `lineinfile` module to modify SSH configuration or consider `dev-sec.ssh-hardening` role

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the FastAPI recipe (`fastapi:fastapi_password`)
  - Consider using Ansible Vault to secure these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation uses Chef templates and attributes to configure multiple Nginx sites
  - Mitigation: Create Ansible templates with similar structure, use Ansible's `with_items` to iterate through site configurations

- **Redis Configuration Hack**: 
  - Description: The cache cookbook includes a Ruby block to modify Redis configuration file directly
  - Mitigation: Use Ansible's template module with proper configuration options instead of post-processing the file

- **PostgreSQL User/Database Creation**:
  - Description: Current implementation uses direct shell commands via `execute` resource
  - Mitigation: Use Ansible's `postgresql_*` modules for more idempotent database management

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Relatively straightforward to implement in Ansible

2. **cache** (Priority 2)
   - Dependent services that should be configured before the application
   - Moderate complexity due to Redis configuration requirements

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on the infrastructure being in place
   - More complex due to Python environment setup and PostgreSQL integration

### Assumptions

1. The target environment will continue to be Fedora-based systems, with potential support for Ubuntu and CentOS
2. The self-signed SSL certificates approach is acceptable for the migrated solution
3. The current security configurations (fail2ban, UFW, SSH hardening) are required in the Ansible version
4. The FastAPI application source will continue to be pulled from the same Git repository
5. The current Redis and PostgreSQL passwords are for development only and will be replaced with proper secrets management
6. The Vagrant development environment will be maintained, but Chef will be replaced with Ansible for provisioning
7. No additional monitoring or logging requirements beyond what's currently implemented