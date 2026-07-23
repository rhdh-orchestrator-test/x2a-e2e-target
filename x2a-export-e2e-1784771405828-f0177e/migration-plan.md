# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 2-3 weeks, with moderate complexity due to the security configurations and SSL certificate management.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database creation, systemd service configuration, Git repository deployment

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, fail2ban integration, UFW firewall setup

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4)
- `solo.json`: Chef configuration file containing the run list and attribute overrides for nginx sites and security settings
- `solo.rb`: Chef configuration file for Chef Solo
- `Vagrantfile`: Defines the development VM using Vagrant with Fedora 42
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development/testing

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should maintain this functionality using Ansible's openssl_* modules.
- **Firewall Configuration**: UFW firewall rules need to be migrated using Ansible's ufw module.
- **fail2ban Integration**: Configuration needs to be migrated using Ansible's template module.
- **SSH Hardening**: SSH security configurations (disabling root login, password authentication) need to be migrated.
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Configuration**: The dynamic generation of Nginx site configurations based on attributes will need careful translation to Ansible variables and templates.
- **Service Dependencies**: Ensuring proper ordering of service installations and configurations, particularly for the FastAPI application which depends on PostgreSQL.
- **SSL Certificate Generation**: Ensuring proper permissions and security for SSL certificate generation and storage.
- **Idempotency**: Ensuring that database creation and user setup tasks are idempotent, similar to the current Chef implementation.

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation
   - Add SSL certificate generation
   - Add security configurations (fail2ban, firewall)
   - Add multi-site configuration

2. **cache** (low complexity, standalone service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Implement PostgreSQL installation and configuration
   - Implement Python environment setup
   - Implement application deployment
   - Implement systemd service configuration

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distribution.
2. Self-signed certificates are acceptable for the migrated solution (not using Let's Encrypt or other CA).
3. The current security configurations (fail2ban, UFW, SSH hardening) are required in the migrated solution.
4. The current directory structure for web content (/var/www/[site]) will be maintained.
5. The PostgreSQL database configuration (database name, user, password) can remain the same.
6. Redis will continue to require password authentication.
7. The FastAPI application will be deployed from the same Git repository.
8. The Vagrant development environment will be maintained but updated to use Ansible provisioning instead of Chef.