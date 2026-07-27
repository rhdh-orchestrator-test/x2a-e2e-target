# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, security configurations, and service deployments. The estimated timeline for migration is 2-3 weeks, with moderate complexity due to the security configurations and SSL certificate management.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and fail2ban integration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening, fail2ban integration, UFW firewall configuration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4). Migration will require mapping these to Ansible Galaxy roles or creating equivalent Ansible roles.
- `solo.json`: Contains node configuration including the run list and attribute overrides for nginx sites, SSL paths, and security settings. Will need to be converted to Ansible group_vars or host_vars.
- `solo.rb`: Chef configuration file that sets paths and log levels. Not directly relevant to Ansible migration.
- `Vagrantfile`: Defines the development VM using Fedora 42. Can be adapted to use Ansible provisioner instead of Chef.
- `vagrant-provision.sh`: Shell script that installs Chef and runs the cookbooks. Will need to be replaced with Ansible installation and playbook execution.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development with potential for deployment to any environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or DavidWittman.redis

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should maintain this functionality or improve it with Let's Encrypt integration.
- **Fail2ban Configuration**: The fail2ban configuration needs to be migrated with all existing jail settings.
- **UFW Firewall Rules**: The UFW firewall configuration needs to be migrated with all existing rules.
- **SSH Hardening**: SSH security settings (disable root login, disable password authentication) need to be preserved.
- **Sysctl Security Settings**: System-level security settings need to be migrated.
- **Vault/secrets management**: 
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - No Chef Vault or encrypted data bags are used, but credentials should be moved to Ansible Vault

### Technical Challenges

- **Custom Resource Migration**: The `lineinfile` custom resource in nginx-multisite needs to be replaced with Ansible's `lineinfile` module.
- **Template Conversion**: Multiple ERB templates need to be converted to Jinja2 format for Ansible.
- **Ruby Block Logic**: Ruby blocks in the Chef recipes (particularly in the cache cookbook) need to be converted to Ansible tasks.
- **Service Orchestration**: The order of operations for service installation, configuration, and startup needs to be preserved.

### Migration Order

1. **nginx-multisite** (high value, moderate complexity)
   - Start with basic Nginx installation and configuration
   - Add virtual host configuration
   - Add SSL certificate generation
   - Add security hardening features

2. **cache** (moderate complexity)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (moderate complexity)
   - Set up Python environment
   - Configure PostgreSQL
   - Deploy application from Git
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions.
2. Self-signed certificates are acceptable for development; production would likely use different certificate management.
3. The current security configurations are appropriate for the target environment.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The current Redis and Memcached configurations are sufficient for the application's needs.
6. The current PostgreSQL configuration is sufficient for the FastAPI application.
7. The current Nginx configuration with multiple virtual hosts is required for the application architecture.