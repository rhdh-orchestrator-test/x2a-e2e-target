# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 3-4 weeks, with complexity rated as moderate due to the presence of multiple services and security configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and fail2ban/ufw firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, firewall configuration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment, Git repository deployment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef configuration file containing the run list and node attributes
- `solo.rb`: Chef configuration file specifying cookbook paths and log settings
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration file for the development environment using Fedora 42

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be a local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or DavidWittman.redis

### Security Considerations

- **SSL Certificate Management**: 
  - Migration approach: Use Ansible's `openssl_*` modules for certificate generation
  - Consider integration with Let's Encrypt using `geerlingguy.certbot` role for production

- **Firewall Configuration**: 
  - Migration approach: Use Ansible's `ufw` module to replace Chef's ufw configuration
  - Ensure all required ports are properly configured (80, 443, 22)

- **Fail2ban Configuration**: 
  - Migration approach: Use Ansible's `template` module to configure fail2ban similar to Chef

- **SSH Hardening**: 
  - Migration approach: Use Ansible's `lineinfile` or `template` module to configure SSH security settings

- **Vault/secrets management**:
  - Redis password in cache cookbook: Use Ansible Vault to store the Redis password
  - PostgreSQL credentials in fastapi-tutorial cookbook: Use Ansible Vault for database credentials
  - Count of credentials detected: 2 (Redis password, PostgreSQL user/password)

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The Chef cookbook dynamically creates multiple virtual hosts based on node attributes
  - Mitigation strategy: Create Ansible templates with Jinja2 loops to generate similar configuration

- **SSL Certificate Generation**: 
  - Description: Self-signed certificates are generated for each site
  - Mitigation strategy: Use Ansible's `openssl_certificate` module with proper idempotency checks

- **PostgreSQL User and Database Creation**: 
  - Description: The Chef cookbook uses shell commands to create database users and permissions
  - Mitigation strategy: Use Ansible's `postgresql_*` modules for more idempotent database management

- **Python Application Deployment**: 
  - Description: The Chef cookbook clones a Git repository and sets up a Python virtual environment
  - Mitigation strategy: Use Ansible's `git` and `pip` modules with proper idempotency checks

### Migration Order

1. **nginx-multisite** (Priority 1)
   - This module provides the web server foundation and should be migrated first
   - Create Ansible roles for nginx installation, SSL configuration, and security hardening

2. **cache** (Priority 2)
   - Migrate the caching services after the web server is properly configured
   - Create separate roles for Memcached and Redis

3. **fastapi-tutorial** (Priority 3)
   - Migrate the application deployment last as it depends on the web server and database
   - Create roles for PostgreSQL and the FastAPI application deployment

### Assumptions

1. The target environment will continue to be Fedora 42 as specified in the Vagrantfile
2. The same directory structure for web content will be maintained
3. Self-signed certificates are acceptable for development (production would require proper certificates)
4. The FastAPI application repository will remain available at the specified URL
5. The security requirements (fail2ban, ufw, SSH hardening) will remain the same
6. Redis and Memcached configurations will maintain the same memory allocations and settings
7. The PostgreSQL database name and credentials can remain the same
8. The systemd service configuration for the FastAPI application will remain similar