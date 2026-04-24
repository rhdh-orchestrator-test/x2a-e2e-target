# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, configuration templates, and security settings. Based on the complexity and scope, this migration is estimated to require 2-3 weeks of effort with a team of 2 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall), sysctl security settings

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

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local cookbooks and external dependencies from Chef Supermarket (nginx, memcached, redisio).
- `solo.json`: Chef configuration file defining the run list and node attributes, including Nginx site configurations and security settings.
- `solo.rb`: Chef configuration file specifying cookbook paths and logging settings.
- `Vagrantfile`: Defines a Vagrant VM configuration using Fedora 42 for local development and testing.
- `vagrant-provision.sh`: Shell script that installs Chef and runs the cookbooks in the Vagrant environment.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Ansible Galaxy or create a custom role
- **memcached (~> 6.0)**: Replace with Ansible memcached role or module
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or modules
- **PostgreSQL**: Use Ansible postgresql_* modules or community.postgresql collection

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW firewall rules that need to be migrated to Ansible's ufw module
- **fail2ban Configuration**: Migrate fail2ban configuration to Ansible's fail2ban_jail module
- **SSH Hardening**: Migrate SSH security settings (disable root login, password authentication) to Ansible's lineinfile or template module
- **SSL Certificate Management**: Replace self-signed certificate generation with Ansible's openssl_* modules
- **Vault/secrets management**:
  - Redis password in cache cookbook (hardcoded as 'redis_secure_password_123')
  - PostgreSQL database credentials in fastapi-tutorial cookbook (hardcoded as 'fastapi_password')
  - No Chef Vault or encrypted data bags detected, but credentials should be moved to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple Nginx sites based on node attributes will need to be replicated using Ansible's templating and looping capabilities
- **SSL Certificate Generation**: Self-signed certificate generation logic needs to be migrated to Ansible's openssl_* modules
- **Service Dependencies**: Ensuring proper ordering of service deployments (e.g., PostgreSQL before FastAPI application)
- **Idempotent Execution**: Ensuring database creation commands are idempotent in Ansible (current Chef implementation uses "|| true" to ignore errors)

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation and configuration
   - Add security hardening (fail2ban, UFW, sysctl)
   - Implement SSL certificate generation
   - Configure virtual hosts

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Set up PostgreSQL database
   - Deploy Python application from Git
   - Configure virtual environment and dependencies
   - Create systemd service

### Assumptions

1. The target environment will continue to be Fedora 42 or a compatible Linux distribution.
2. Self-signed certificates are acceptable for development; production would likely require proper certificates.
3. The current hardcoded credentials will be replaced with Ansible Vault variables.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The current security settings (fail2ban, UFW, SSH hardening) are appropriate for the target environment.
6. The Nginx configuration will maintain the same virtual host structure with SSL enabled.
7. The Redis configuration workarounds (ruby_block "fix_redis_config") may not be necessary with a direct Ansible implementation.
8. The PostgreSQL database structure required by the FastAPI application is created by the application itself after database initialization.