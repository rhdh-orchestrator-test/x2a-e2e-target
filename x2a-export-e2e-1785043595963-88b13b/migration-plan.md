# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration scope is moderate, involving three Chef cookbooks with external dependencies. Based on the complexity and number of components, the estimated timeline for migration is 2-3 weeks with 1-2 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL setup, security hardening (fail2ban, ufw, SSH restrictions)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment, Git repository deployment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (both local and external from Chef Supermarket). Migration will require mapping these dependencies to Ansible Galaxy roles or collections.
- `solo.json`: Contains the Chef run list and configuration data that will need to be migrated to Ansible inventory variables.
- `solo.rb`: Chef configuration file that defines paths and log settings.
- `Vagrantfile`: Defines the development/test environment using Vagrant with a Fedora 42 VM. Can be adapted for Ansible testing.
- `vagrant-provision.sh`: Shell script that installs Chef and runs the cookbooks in the Vagrant environment.

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) based on cookbook metadata, with Fedora 42 used in the Vagrant development environment.
- **Virtual Machine Technology**: Vagrant with libvirt provider based on the Vagrantfile.
- **Cloud Platform**: Not specified in the repository. The configuration appears to be designed for on-premises or generic VM deployment.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or the `ansible.posix.nginx` collection
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role or custom tasks
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` role or the `community.general.redis` module

### Security Considerations

- **SSL Certificate Management**: The nginx-multisite cookbook manages SSL certificates in `/etc/ssl/certs` and `/etc/ssl/private`. Migration should use Ansible's `openssl_*` modules or `community.crypto` collection.
- **Firewall Configuration**: The security recipe configures UFW. Use Ansible's `ufw` module for migration.
- **SSH Hardening**: SSH configuration disables root login and password authentication. Use Ansible's `template` module with appropriate SSH configuration.
- **fail2ban Integration**: Security configuration includes fail2ban. Use Ansible's `community.general.fail2ban` module.
- **Vault/secrets management**: 
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - These should be migrated to Ansible Vault or an external secrets management solution

### Technical Challenges

- **Multi-site Nginx Configuration**: The nginx-multisite cookbook dynamically creates virtual hosts based on the configuration in solo.json. This will require careful template design in Ansible.
- **Redis Configuration Hacks**: The cache cookbook includes a Ruby block to modify Redis configuration files after they're created. This will need special handling in Ansible.
- **FastAPI Application Deployment**: The deployment process involves Git, Python virtual environments, and systemd service configuration. This will require multiple Ansible modules working together.
- **PostgreSQL User and Database Creation**: The current implementation uses direct psql commands. Migration should use Ansible's PostgreSQL modules for idempotent operation.

### Migration Order

1. **cache cookbook** (moderate complexity, fewer dependencies)
   - Implement Memcached configuration
   - Implement Redis configuration with authentication

2. **nginx-multisite cookbook** (moderate complexity)
   - Implement base Nginx installation and configuration
   - Implement security hardening (fail2ban, ufw, SSH)
   - Implement SSL certificate management
   - Implement virtual host configuration

3. **fastapi-tutorial cookbook** (highest complexity)
   - Implement PostgreSQL installation and configuration
   - Implement Python environment setup
   - Implement application deployment from Git
   - Implement systemd service configuration

### Assumptions

1. The current Chef setup is functional and represents the desired end state.
2. SSL certificates are self-signed for development (based on vagrant-provision.sh output).
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git is accessible and contains the expected code.
4. The migration will maintain the same operating system support (Ubuntu 18.04+ and CentOS 7+).
5. The Vagrant development environment will continue to be used for testing the Ansible playbooks.
6. No CI/CD pipeline integration is required as part of the migration (none was present in the original Chef setup).
7. The hardcoded credentials in the cookbooks are for development only and will be replaced with more secure solutions in the Ansible implementation.