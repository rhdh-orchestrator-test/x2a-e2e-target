# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, configuration templates, and security settings. The estimated timeline for migration is 3-4 weeks, with moderate complexity due to the interdependencies between services and security configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, fail2ban integration, UFW firewall configuration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external cookbook dependencies
- `solo.json`: Chef configuration file containing the run list and node attributes
- `solo.rb`: Chef configuration file specifying cookbook paths and log settings
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration file for the development environment using Fedora 42

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or dedicated tasks for Redis installation and configuration

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should maintain this capability while allowing for future integration with Let's Encrypt or other certificate authorities.
- **Firewall Configuration**: UFW rules need to be migrated to appropriate Ansible firewall modules (ufw or firewalld depending on target OS).
- **fail2ban Integration**: Configuration needs to be migrated to Ansible tasks.
- **Security Headers**: Nginx security headers configuration needs to be preserved in templates.
- **SSH Hardening**: SSH configuration hardening (disabling root login, password authentication) needs to be migrated.
- **Vault/secrets management**:
  - Redis password in cache cookbook (plaintext in recipe)
  - PostgreSQL credentials in fastapi-tutorial cookbook (plaintext in recipe)
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Configuration**: The dynamic generation of multiple Nginx sites based on node attributes will need careful translation to Ansible variables and templates.
- **SSL Certificate Generation**: The self-signed certificate generation logic needs to be replicated in Ansible.
- **Service Orchestration**: The current setup has interdependent services (Nginx, Redis, Memcached, PostgreSQL, FastAPI application) that need to be started in the correct order.
- **Python Environment Management**: The Python virtual environment setup and dependency installation needs to be handled appropriately in Ansible.

### Migration Order

1. **cache cookbook** (Priority 1, low complexity)
   - Simple Redis and Memcached configuration
   - Few dependencies
   - Good starting point for the migration

2. **nginx-multisite cookbook** (Priority 2, moderate complexity)
   - Core infrastructure component
   - Multiple templates and configurations
   - Security configurations that other components depend on

3. **fastapi-tutorial cookbook** (Priority 3, moderate complexity)
   - Application deployment
   - Depends on PostgreSQL
   - Requires service configuration

### Assumptions

1. The target environment will continue to be Fedora-based systems, with potential expansion to Ubuntu and CentOS as indicated in the cookbook metadata.
2. Self-signed certificates are acceptable for the migrated solution, but the implementation should allow for easy replacement with proper certificates.
3. The current security configurations (fail2ban, UFW, SSH hardening) are required in the migrated solution.
4. The Vagrant development environment should be preserved or replaced with an equivalent Ansible-based development workflow.
5. The current plaintext secrets in the recipes will be migrated to Ansible Vault or another secure storage mechanism.
6. The FastAPI application source code will continue to be pulled from the same Git repository.
7. The current directory structure and naming conventions for deployed applications will be maintained.
8. The PostgreSQL database configuration (users, databases, permissions) should be preserved.
9. The systemd service configurations should be maintained with the same parameters.
10. The Redis configuration workarounds in the cache cookbook may not be necessary in an Ansible-based solution and should be evaluated during migration.