# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration scope is moderate, consisting of three primary cookbooks with external dependencies. Based on the complexity and size, a complete migration to Ansible is estimated to take 2-3 weeks with 1-2 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, including security hardening
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

- `Berksfile`: Defines cookbook dependencies from Chef Supermarket and local paths. Migration will require mapping these dependencies to Ansible Galaxy roles or collections.
- `solo.json`: Contains the run list and configuration data for Chef Solo. This will be migrated to Ansible inventory variables and group_vars.
- `solo.rb`: Chef Solo configuration file. Will be replaced by Ansible configuration.
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef. Will need to be updated to use Ansible.
- `Vagrantfile`: Defines the development VM configuration. Will need minor updates to use Ansible provisioner instead of Chef.

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or the `ansible.posix.nginx` collection
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` role or DavidWittman.redis

### Security Considerations

- **SSL Certificate Management**: The nginx-multisite cookbook manages SSL certificates. Migration should use Ansible's `community.crypto` collection for certificate management.
- **Security Hardening**: The security recipe in nginx-multisite configures fail2ban, ufw, and SSH hardening. Use Ansible's `dev-sec.ssh-hardening` and `dev-sec.nginx-hardening` roles.
- **Redis Authentication**: The cache cookbook sets a Redis password. Ensure this is securely managed in Ansible Vault.
- **Vault/secrets management**:
  - Redis password hardcoded in the cache cookbook's default.rb
  - PostgreSQL credentials hardcoded in the fastapi-tutorial cookbook's default.rb
  - Total credentials detected: 2 (Redis password, PostgreSQL user/password)

### Technical Challenges

- **Multi-site Nginx Configuration**: The nginx-multisite cookbook manages multiple virtual hosts with SSL. This will require careful templating in Ansible to maintain the same flexibility.
- **Redis Configuration Hack**: The cache cookbook contains a Ruby block to modify Redis configuration files after they're created. This will need a custom Ansible approach, possibly using lineinfile or template modules.
- **FastAPI Application Deployment**: The fastapi-tutorial cookbook clones a Git repository and sets up a Python environment. This will require multiple Ansible modules working together (git, pip, template, systemd).

### Migration Order

1. **cache cookbook** (low complexity, standalone services)
2. **nginx-multisite cookbook** (moderate complexity, core infrastructure)
3. **fastapi-tutorial cookbook** (higher complexity, application deployment)

### Assumptions

1. The current Chef setup is functional and represents the desired end state.
2. The Vagrant development environment should be preserved with minimal changes.
3. No CI/CD pipeline integration is required as part of the migration.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git is accessible and will remain available.
5. The SSL certificates referenced in the configuration are self-signed for development purposes.
6. The security configurations (fail2ban, ufw, SSH hardening) should be maintained in the Ansible version.
7. The Redis configuration hack is necessary due to compatibility issues with the current Redis version.
8. The PostgreSQL database should be created with the same credentials and configuration.