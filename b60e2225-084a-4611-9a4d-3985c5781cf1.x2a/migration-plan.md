# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup focused on deploying a multi-site Nginx configuration with SSL, security hardening, and a FastAPI application with PostgreSQL and caching services (Redis and Memcached). The migration to Ansible is estimated to be of medium complexity, requiring approximately 2-3 weeks for a complete migration with testing. The repository uses Chef Solo with Berkshelf for dependency management and is designed to run in a Vagrant environment.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and SSL certificate generation
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw)

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Configures caching services (Memcached and Redis) with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Manages cookbook dependencies, including external dependencies from Chef Supermarket (nginx, memcached, redisio)
- `solo.json`: Contains node configuration data including site configurations, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Defines the Vagrant VM configuration (Fedora 42, port forwarding, networking)

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) based on cookbook metadata, but the Vagrantfile specifies Fedora 42
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development/testing

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package module
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package module with custom configuration

### Security Considerations

- **SSL Certificate Management**: The current setup generates self-signed certificates. Migration should maintain this capability or integrate with Ansible's crypto modules
- **Security Hardening**: 
  - fail2ban configuration needs to be migrated to Ansible
  - UFW firewall rules need to be migrated to Ansible's ufw module
  - SSH hardening (disable root login, password authentication) needs to be migrated
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: The current setup dynamically generates Nginx site configurations from node attributes. Ansible will need to replicate this dynamic configuration generation.
- **SSL Certificate Generation**: Self-signed certificate generation will need to be replicated in Ansible, potentially using the openssl_* modules.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL, and the Nginx sites depend on the SSL certificates. These dependencies need to be maintained in the Ansible playbook.
- **Redis Configuration Hack**: The cache cookbook includes a Ruby block to modify Redis configuration files after they're created. This will need a custom approach in Ansible.

### Migration Order

1. **nginx-multisite cookbook** (moderate complexity)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Add security hardening (fail2ban, ufw)
   - Add multi-site configuration

2. **cache cookbook** (low complexity)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Address the Redis configuration hack

3. **fastapi-tutorial cookbook** (moderate complexity)
   - Implement Python environment setup
   - Configure PostgreSQL
   - Deploy application from Git
   - Set up systemd service

### Assumptions

1. The target environment will continue to be Vagrant VMs or similar environments
2. Self-signed certificates are acceptable for the migrated solution
3. The same security hardening measures are required in the Ansible version
4. The FastAPI application source code will remain available at the same Git repository
5. The directory structure for document roots and SSL certificates will remain the same
6. The PostgreSQL and Redis passwords can be changed during migration
7. The Fedora 42 OS target will be maintained (though the cookbooks support Ubuntu and CentOS)