# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backend. The migration scope encompasses 3 Chef cookbooks with external dependencies on community cookbooks. Based on the complexity and size of the codebase, this migration is estimated to be of medium complexity and could be completed in approximately 2-3 weeks with 1-2 dedicated engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and SSL certificate management
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup, security hardening

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
- `solo.json`: Contains node configuration data including the run list and attribute overrides. This will be migrated to Ansible inventory variables and group_vars.
- `solo.rb`: Chef Solo configuration file. Will be replaced by Ansible configuration.
- `Vagrantfile`: Defines the development VM environment. Can be adapted to use Ansible provisioner instead of Chef.
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef. Will need to be updated for Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ based on cookbook metadata
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible `nginx` role from Galaxy or use the `ansible.builtin.package` module with templates
- **memcached (~> 6.0)**: Replace with Ansible `geerlingguy.memcached` role or custom tasks
- **redisio (~> 7.2.4)**: Replace with Ansible `geerlingguy.redis` role or custom Redis configuration tasks

### Security Considerations

- **SSL Certificate Management**: The nginx-multisite cookbook manages SSL certificates. Migration should preserve the same certificate paths and permissions.
  - Migration approach: Use Ansible's `ansible.builtin.copy` or `ansible.builtin.template` modules to manage certificates, or consider integrating with `community.crypto` collection for certificate generation.

- **Redis Authentication**: Redis is configured with password authentication.
  - Migration approach: Ensure Redis password is stored securely in Ansible Vault and applied using templates.

- **Security Hardening**: The nginx-multisite cookbook includes security hardening via the security.rb recipe.
  - Migration approach: Implement equivalent security measures using Ansible tasks or the `dev-sec.nginx-hardening` role.

- **Vault/secrets management**:
  - Hardcoded Redis password in cache/recipes/default.rb
  - PostgreSQL database credentials in fastapi-tutorial/recipes/default.rb
  - All credentials should be migrated to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The nginx-multisite cookbook manages multiple virtual hosts with SSL. 
  - Mitigation: Use Ansible templates to generate site configurations, potentially using with_items to iterate through site definitions.

- **PostgreSQL Database Setup**: The FastAPI application requires specific PostgreSQL configuration.
  - Mitigation: Use the `community.postgresql` collection to manage database users and permissions.

- **Service Orchestration**: The current setup manages service dependencies (e.g., FastAPI depends on PostgreSQL).
  - Mitigation: Use Ansible handlers and the `notify` directive to ensure proper service restart ordering.

- **Python Environment Management**: The FastAPI application uses a Python virtual environment.
  - Mitigation: Use Ansible's `ansible.builtin.pip` module with the `virtualenv` parameter to manage Python dependencies.

### Migration Order

1. **nginx-multisite cookbook** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation and configuration
   - Implement SSL certificate management
   - Configure virtual hosts
   - Apply security hardening

2. **cache cookbook** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial cookbook** (high complexity, depends on PostgreSQL)
   - Set up PostgreSQL database
   - Deploy FastAPI application
   - Configure systemd service

### Assumptions

1. The target environment will continue to use Fedora 42 as the primary OS.
2. The development workflow will continue to use Vagrant for local testing.
3. SSL certificates are managed manually or generated on the fly (no integration with Let's Encrypt or other automated certificate management).
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain accessible.
5. The current security configurations (fail2ban, ufw, SSH hardening) should be preserved in the Ansible implementation.
6. Redis and Memcached configurations don't require significant customization beyond what's currently implemented.
7. The migration will not introduce new features or architectural changes to the existing infrastructure.