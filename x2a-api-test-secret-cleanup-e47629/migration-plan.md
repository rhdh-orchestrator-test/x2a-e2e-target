# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 2-3 weeks, with moderate complexity due to the security configurations and multiple service integrations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificates
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall)

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

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef configuration file defining the run list and node attributes
- `solo.rb`: Chef configuration file defining paths and log settings
- `Vagrantfile`: Defines a Fedora 42 VM for local development with port forwarding and resource allocation
- `vagrant-provision.sh`: Shell script that installs Chef and runs the cookbooks in the Vagrant environment

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development or on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role or direct package management
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` role or direct Redis installation and configuration

### Security Considerations

- **Firewall Configuration**: UFW firewall rules need to be migrated to Ansible's `ufw` module
- **Fail2ban Setup**: Configuration needs to be migrated to Ansible templates
- **SSH Hardening**: SSH configuration (disabling root login, password authentication) needs to be migrated
- **SSL Certificate Management**: Self-signed certificate generation needs to be handled with Ansible's `openssl_*` modules
- **Vault/secrets management**:
  - Redis password in the cache cookbook (hardcoded as 'redis_secure_password_123')
  - PostgreSQL database credentials in the fastapi-tutorial cookbook (hardcoded as 'fastapi_password')
  - Total credentials detected: 2 hardcoded passwords

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple virtual hosts based on attributes will need careful translation to Ansible templates and variables
- **SSL Certificate Management**: Self-signed certificate generation and management will need to be handled with Ansible's OpenSSL modules
- **Service Orchestration**: The order of service deployment and configuration needs to be maintained (e.g., PostgreSQL before FastAPI application)
- **Python Environment Management**: The Python virtual environment setup and dependency installation will need to be translated to Ansible's Python modules

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Create base Nginx role with templates for configuration
   - Implement security hardening (fail2ban, UFW)
   - Set up SSL certificate generation

2. **cache** (low complexity, independent service)
   - Set up Memcached configuration
   - Configure Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Set up PostgreSQL database and user
   - Deploy FastAPI application from Git
   - Configure Python environment and dependencies
   - Create and enable systemd service

### Assumptions

1. The target environment will continue to be Fedora-based systems (specifically Fedora 42 as indicated in the Vagrantfile)
2. The self-signed certificates are for development purposes only and not production
3. The hardcoded passwords in the Redis and PostgreSQL configurations will be replaced with Ansible Vault variables
4. The current directory structure with separate modules will be maintained in the Ansible roles
5. The Vagrant development environment will be preserved but updated to use Ansible provisioning instead of Chef
6. No changes to the actual application code or deployment architecture are required
7. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
8. The current security configurations (fail2ban, UFW, SSH hardening) are to be maintained in the Ansible implementation