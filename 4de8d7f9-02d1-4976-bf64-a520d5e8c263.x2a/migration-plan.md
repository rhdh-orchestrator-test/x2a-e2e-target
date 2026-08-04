# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with FastAPI application backend and caching services (Redis and Memcached). The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for migration is 2-3 weeks, with moderate complexity due to the security configurations and SSL certificate management.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies.
- `solo.json`: Chef configuration file containing the run list and node attributes.
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings.
- `Vagrantfile`: Defines the development VM using Fedora 42, with port forwarding and network configuration.
- `vagrant-provision.sh`: Shell script that installs Chef and runs the cookbooks in the Vagrant environment.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or local development

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.nginx collection
- **memcached (~> 6.0)**: Replace with Ansible memcached role or community.general.memcached module
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role or community.general.redis module

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should maintain this capability while allowing for future integration with Let's Encrypt.
- **Firewall Configuration**: UFW firewall rules need to be migrated to equivalent Ansible firewall modules.
- **Fail2ban Configuration**: Fail2ban setup needs to be migrated to Ansible.
- **SSH Hardening**: SSH configuration hardening (disabling root login, password authentication) needs to be preserved.
- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL credentials in fastapi-tutorial cookbook: User "fastapi" with password "fastapi_password"
  - These should be migrated to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple Nginx site configurations based on node attributes will need careful translation to Ansible templates and variables.
- **SSL Certificate Generation**: The self-signed certificate generation logic needs to be preserved in Ansible.
- **Service Dependencies**: Ensuring proper ordering of service installations and configurations (e.g., PostgreSQL before FastAPI application).
- **Redis Configuration Hack**: The current implementation includes a Ruby block to modify Redis configuration files directly. This will need a cleaner implementation in Ansible.

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation
   - Add SSL certificate generation
   - Add security hardening (fail2ban, ufw)
   - Add multi-site configuration

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (moderate complexity, depends on PostgreSQL)
   - Implement PostgreSQL installation and configuration
   - Implement Python environment setup
   - Implement application deployment and service configuration

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions.
2. Self-signed certificates are acceptable for development; production would likely use different certificate sources.
3. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate for the target environment.
4. The FastAPI application source will continue to be available at the specified GitHub repository.
5. The Redis and Memcached configurations do not require advanced clustering or replication features.
6. The PostgreSQL database will remain local to the application server rather than using an external database service.
7. The current directory structure and file organization in the web server document roots will be maintained.