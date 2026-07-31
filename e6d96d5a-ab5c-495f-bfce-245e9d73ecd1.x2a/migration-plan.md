# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup focused on web services with multiple sites, caching layers, and a FastAPI application. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 2-3 weeks, with moderate complexity due to the multi-site configuration and security requirements.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw)

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

- `Berksfile`: Dependency management file listing both local cookbooks and external dependencies from Chef Supermarket. Migration will require mapping these dependencies to Ansible Galaxy roles or custom implementations.
- `solo.json`: Contains the run list and configuration data for Chef Solo. This will be converted to Ansible inventory variables and group_vars.
- `solo.rb`: Chef Solo configuration file. Will be replaced by Ansible configuration.
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef. Will need to be updated to use Ansible.
- `Vagrantfile`: Defines the development VM. Will need minor updates to use Ansible provisioner instead of Chef.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` module or community.general collection
- **memcached (~> 6.0)**: Replace with Ansible's `memcached` module or community.general collection
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role from Galaxy or custom implementation using Ansible's `redis` modules

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should maintain this capability while allowing for future integration with Let's Encrypt or other certificate providers.
- **Firewall Configuration**: UFW firewall rules need to be migrated to equivalent Ansible UFW module tasks.
- **Fail2ban Configuration**: Fail2ban setup needs to be migrated to Ansible tasks.
- **SSH Hardening**: SSH configuration hardening (disabling root login, password authentication) should be preserved.
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi`/`fastapi_password`)
  - These should be moved to Ansible Vault or another secrets management solution

### Technical Challenges

- **Multi-site Configuration**: The dynamic generation of multiple Nginx site configurations based on node attributes will need to be replicated using Ansible's templating system.
- **SSL Certificate Generation**: Self-signed certificate generation logic needs to be preserved while making it compatible with Ansible's idempotent execution model.
- **Service Dependencies**: Ensuring proper ordering of service installation, configuration, and startup in Ansible's declarative model.
- **Redis Configuration Hack**: The current implementation includes a Ruby block to modify Redis configuration files after they're created. This will need a clean implementation in Ansible.

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation
   - Add SSL certificate generation
   - Implement security hardening
   - Configure multi-site setup

2. **cache** (low complexity, standalone service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Set up Python environment
   - Configure PostgreSQL
   - Deploy application
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions.
2. Self-signed certificates are acceptable for development; production would likely use different certificate sources.
3. The current security configurations are appropriate for the target environment.
4. The FastAPI application source will continue to be available at the specified GitHub repository.
5. The Redis configuration "hack" is necessary due to compatibility issues with the current Redis version.
6. The current directory structure in `/var/www` for website content will be maintained.
7. The PostgreSQL database structure required by the FastAPI application is created by the application itself.