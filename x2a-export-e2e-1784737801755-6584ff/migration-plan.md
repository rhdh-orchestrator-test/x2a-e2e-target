# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 2-3 weeks, with moderate complexity due to the security configurations and SSL certificate management.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw)

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef configuration data with node attributes for Nginx sites, SSL, and security settings
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration for development environment using Fedora 42

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>=18.04) and CentOS (>=7.0) based on cookbook metadata, with Fedora 42 used in Vagrant development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or community.general.memcached module
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or community.general.redis module

### Security Considerations

- **Firewall Configuration**: The current setup uses UFW for firewall management, which should be migrated to appropriate Ansible firewall modules (ufw or firewalld depending on target OS)
- **Fail2ban Setup**: Current configuration includes fail2ban for brute force protection, which should be migrated to an Ansible fail2ban role
- **SSH Hardening**: SSH configuration disables root login and password authentication, which should be preserved in Ansible using the openssh_* modules
- **SSL Certificate Management**: Self-signed certificates are generated for each site, which should be migrated to Ansible's openssl_* modules
- **Vault/secrets management**: 
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL credentials in fastapi-tutorial cookbook: username "fastapi" with password "fastapi_password"
  - These should be migrated to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The current setup dynamically creates Nginx site configurations based on node attributes. This pattern needs to be replicated in Ansible using templates and variables.
- **SSL Certificate Generation**: Self-signed certificates are generated for each site. This logic needs to be preserved in Ansible using the openssl_* modules.
- **Service Orchestration**: The current setup manages multiple interdependent services (Nginx, PostgreSQL, Redis, Memcached, FastAPI application). The Ansible playbooks need to maintain these dependencies and restart services appropriately.
- **Security Hardening**: The comprehensive security configurations (sysctl settings, firewall rules, fail2ban) need to be carefully migrated to maintain the same security posture.

### Migration Order

1. **cache** (low complexity): Simple configuration of Memcached and Redis services
2. **nginx-multisite** (moderate complexity): Nginx configuration with SSL and security features
3. **fastapi-tutorial** (moderate complexity): Application deployment with database dependencies

### Assumptions

1. The target environment will continue to use the same operating systems (Ubuntu/CentOS/Fedora)
2. The self-signed SSL certificates approach is acceptable for the migrated solution
3. The current security configurations are appropriate for the target environment
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current Redis and PostgreSQL password configurations are for development only and will be replaced with more secure credentials in production
6. The Vagrant development environment will be maintained for testing the Ansible playbooks