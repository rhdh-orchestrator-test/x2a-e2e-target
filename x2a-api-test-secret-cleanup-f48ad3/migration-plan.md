# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, configuration templates, and security settings. Based on the complexity and scope, this migration is estimated to be of medium complexity and should take approximately 3-4 weeks to complete with a team of 2 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and proper SSL configuration
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
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4)
- `solo.json`: Defines the Chef run list and configuration attributes for nginx sites and security settings
- `solo.rb`: Configures Chef Solo paths and logging
- `Vagrantfile`: Defines a Fedora 42 VM with port forwarding for development/testing
- `vagrant-provision.sh`: Bash script to provision the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)
- **PostgreSQL**: Replace with Ansible PostgreSQL role (e.g., geerlingguy.postgresql)

### Security Considerations

- **SSL Certificate Management**: 
  - Migration approach: Use Ansible's openssl_* modules for certificate generation
  - Consider integrating with Ansible Vault for private key storage

- **Firewall Configuration (UFW)**:
  - Migration approach: Use Ansible's ufw module to configure firewall rules

- **fail2ban Integration**:
  - Migration approach: Use Ansible to install and configure fail2ban with templates

- **SSH Hardening**:
  - Migration approach: Use Ansible's lineinfile or template module to configure sshd_config

- **Vault/secrets management**:
  - Redis password in cache cookbook: 1 hardcoded credential
  - PostgreSQL credentials in fastapi-tutorial cookbook: 2 hardcoded credentials
  - Environment variables in .env file: 1 configuration with sensitive data

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation uses Chef templates to generate multiple virtual host configurations
  - Mitigation: Create Ansible templates with similar logic, using with_items to iterate through site configurations

- **SSL Certificate Generation**:
  - Description: Self-signed certificates are generated using openssl commands
  - Mitigation: Use Ansible's openssl_certificate module to generate certificates

- **Redis Configuration Patching**:
  - Description: The Chef cookbook uses a ruby_block to modify Redis configuration
  - Mitigation: Use Ansible's lineinfile module or templates with proper configuration options

- **PostgreSQL User and Database Creation**:
  - Description: Uses shell commands to create database users and permissions
  - Mitigation: Use Ansible's postgresql_* modules for idempotent database management

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Implement security configurations (fail2ban, UFW)
   - Configure virtual hosts

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, application deployment)
   - Implement PostgreSQL database setup
   - Configure Python environment and dependencies
   - Deploy application code
   - Set up systemd service

### Assumptions

1. The target environment will continue to be Fedora-based systems (specifically Fedora 42 as indicated in the Vagrantfile)
2. Self-signed certificates are acceptable for development/testing, but production may require proper certificates
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
4. The current security configurations (fail2ban, UFW, SSH hardening) are appropriate for the target environment
5. Redis and Memcached configurations don't require significant changes from their current settings
6. The PostgreSQL database schema is managed by the FastAPI application and doesn't require additional migration steps
7. The current Nginx site configurations (test.cluster.local, ci.cluster.local, status.cluster.local) will remain the same
8. The current hardcoded credentials will be replaced with Ansible Vault variables