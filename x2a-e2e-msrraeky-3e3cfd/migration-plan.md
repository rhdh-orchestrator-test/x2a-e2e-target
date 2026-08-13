# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration scope is moderate, consisting of three primary cookbooks with external dependencies. Based on the complexity and size, a complete migration to Ansible is estimated to take 2-3 weeks with 1-2 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and SSL certificate management
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup, security hardening (fail2ban, ufw)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database provisioning, systemd service configuration

### Infrastructure Files

- `Berksfile`: Manages cookbook dependencies, including local and external cookbooks. Migration will require mapping these dependencies to Ansible Galaxy roles or collections.
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

- **nginx (~> 12.0)**: Replace with Ansible `nginx` role from Galaxy or use the `ansible.builtin.package` module with templates
- **memcached (~> 6.0)**: Replace with Ansible `geerlingguy.memcached` role or direct configuration
- **redisio (~> 7.2.4)**: Replace with Ansible `geerlingguy.redis` role or direct configuration

### Security Considerations

- **SSL Certificate Management**: The nginx-multisite cookbook manages SSL certificates. Migration should preserve certificate paths and permissions.
  - Migration approach: Use Ansible `copy` or `template` modules for certificate files, with appropriate permissions.

- **Redis Authentication**: Redis is configured with password authentication.
  - Migration approach: Ensure Redis password is stored securely in Ansible Vault.

- **Security Hardening**: The configuration includes fail2ban, ufw firewall, and SSH hardening.
  - Migration approach: Use Ansible security roles like `dev-sec.ssh-hardening` and `dev-sec.nginx-hardening`.

- **Vault/secrets management**:
  - Hardcoded Redis password in cache/recipes/default.rb: `redis_secure_password_123`
  - FastAPI database password in fastapi-tutorial/recipes/default.rb: `fastapi_password`
  - Migration approach: Move all credentials to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The nginx-multisite cookbook manages multiple virtual hosts with SSL. 
  - Mitigation: Use Ansible templates to generate site configurations, similar to the Chef approach.

- **PostgreSQL User and Database Creation**: The FastAPI cookbook creates PostgreSQL users and databases.
  - Mitigation: Use Ansible's `postgresql_*` modules from the `community.postgresql` collection.

- **Service Management**: The FastAPI application is deployed as a systemd service.
  - Mitigation: Use Ansible's `systemd` module to manage the service.

### Migration Order

1. **cache cookbook** (Low complexity): Simple Redis and Memcached configuration
2. **nginx-multisite cookbook** (Medium complexity): Nginx configuration with multiple sites and SSL
3. **fastapi-tutorial cookbook** (High complexity): Application deployment with database dependencies

### Assumptions

1. The current Chef setup is functional and represents the desired end state.
2. No major architectural changes are planned during the migration.
3. The target environment will continue to be Fedora/CentOS/Ubuntu based.
4. Vagrant will continue to be used for development environments.
5. The FastAPI application source code will remain at the same GitHub repository.
6. SSL certificates are self-signed for development purposes.
7. The migration will maintain the same security practices (fail2ban, ufw, SSH hardening).
8. Redis and Memcached configurations will remain similar.