# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to Ansible roles and playbooks. The estimated complexity is medium, with security configurations and multiple service integrations requiring careful attention.

**Timeline Estimate:**
- Planning and preparation: 1 week
- Core infrastructure migration: 2 weeks
- Testing and validation: 1 week
- Documentation and knowledge transfer: 1 week
- **Total**: 5 weeks

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
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

- `Berksfile`: Dependency management file listing cookbook dependencies (nginx, memcached, redisio)
- `solo.json`: Chef configuration file with run list and node attributes
- `solo.rb`: Chef configuration file for Chef Solo
- `Vagrantfile`: Defines a Fedora 42 VM for development/testing
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks
- **PostgreSQL**: Replace with Ansible postgresql_* modules or community.postgresql collection

### Security Considerations

- **SSL/TLS Configuration**: 
  - Self-signed certificate generation needs to be migrated to Ansible's openssl_* modules
  - Certificate and key paths need to be maintained (/etc/ssl/certs and /etc/ssl/private)
  - TLS protocol and cipher configurations need to be preserved

- **Firewall Configuration**:
  - UFW rules need to be migrated to Ansible's ufw module
  - Default deny policy with specific allow rules for SSH, HTTP, HTTPS

- **Fail2ban Integration**:
  - Configuration needs to be migrated to Ansible's template module
  - Service management needs to be handled

- **SSH Hardening**:
  - Root login disable configuration
  - Password authentication disable configuration

- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL user/password in fastapi-tutorial cookbook: "fastapi"/"fastapi_password"
  - Database connection string in .env file

### Technical Challenges

- **Multi-site Configuration**: The dynamic generation of Nginx site configurations based on node attributes will need careful translation to Ansible variables and templates.

- **Service Interdependencies**: The FastAPI application depends on PostgreSQL, and the web server configuration depends on the application being available. These dependencies need to be properly sequenced in Ansible.

- **SSL Certificate Management**: Self-signed certificate generation and management will need to be handled carefully to ensure proper permissions and ownership.

- **Idempotency**: Ensuring that database creation and user setup tasks are idempotent, similar to the current Chef implementation.

- **Configuration Customization**: The current implementation uses Chef attributes extensively for configuration. This needs to be translated to Ansible variables with appropriate defaults.

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Add virtual host configuration
   - Add security hardening (fail2ban, firewall, headers)

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on database)
   - Set up PostgreSQL database and user
   - Deploy application code from Git
   - Configure Python environment and dependencies
   - Set up systemd service

### Assumptions

1. The target environment will continue to be Fedora 42 or a compatible Linux distribution.
2. The same directory structure for web content will be maintained (/var/www/[site]).
3. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or other CA).
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The current security configurations (TLS settings, headers, firewall rules) are appropriate for the target environment.
6. The Redis and PostgreSQL passwords in the current configuration are development passwords that will be replaced with Ansible Vault secured values.
7. The Vagrant development environment will be replaced with an equivalent Ansible-based setup.
8. The current multi-site configuration approach will be maintained rather than using a more dynamic approach.