# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with FastAPI application backend and caching services. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, templates, and configuration files. The estimated complexity is moderate, with an estimated timeline of 2-3 weeks for a complete migration.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and SSL certificate management
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup, security hardening with fail2ban and UFW firewall

- **fastapi-tutorial**:
    - Description: FastAPI Python web application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Node configuration with run list and attribute overrides
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Vagrant configuration for local development/testing environment
- `vagrant-provision.sh`: Provisioning script for Vagrant VM setup

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks

### Security Considerations

- **SSL/TLS Management**: 
  - Self-signed certificates are generated for development
  - Migration should use ansible.builtin.openssl_* modules or community.crypto collection
  - Certificate paths need to be maintained (/etc/ssl/certs and /etc/ssl/private)

- **Firewall Configuration**:
  - UFW firewall is configured with specific rules
  - Replace with ansible.posix.ufw module or ansible.builtin.iptables

- **SSH Hardening**:
  - Root login disabled
  - Password authentication disabled
  - Replace with ansible.posix.ssh_config module or template

- **System Hardening**:
  - fail2ban configuration
  - sysctl security settings
  - Replace with ansible.posix.sysctl and dedicated fail2ban role

- **Vault/secrets management**:
  - Hardcoded credentials found in cache/recipes/default.rb (Redis password: 'redis_secure_password_123')
  - Hardcoded credentials found in fastapi-tutorial/recipes/default.rb (PostgreSQL user/password: 'fastapi'/'fastapi_password')
  - These should be migrated to Ansible Vault or external secret management

### Technical Challenges

- **Multi-site Configuration**: The nginx-multisite cookbook uses a data-driven approach to configure multiple sites. This pattern needs to be replicated in Ansible using loops and templates.

- **Service Dependencies**: The FastAPI application depends on PostgreSQL, and the nginx configuration depends on the SSL certificates. These dependencies need to be properly managed in Ansible with handlers and notify mechanisms.

- **Template Migration**: Several ERB templates need to be converted to Jinja2 format for Ansible, maintaining the same functionality.

- **Idempotency**: Ensuring all custom commands remain idempotent when converted to Ansible tasks, especially the database creation and SSL certificate generation.

### Migration Order

1. **cache cookbook** (Priority 1 - low complexity)
   - Simple package installations and configurations
   - Good starting point with minimal dependencies

2. **nginx-multisite cookbook** (Priority 2 - moderate complexity)
   - Core infrastructure component
   - Contains multiple recipes and templates
   - Security configurations

3. **fastapi-tutorial cookbook** (Priority 3 - moderate complexity)
   - Application deployment
   - Database configuration
   - Depends on functioning web server

### Assumptions

1. The target environment will continue to be Fedora/CentOS/Ubuntu based systems
2. The same directory structure for web content will be maintained
3. Self-signed certificates are acceptable for development (production would use Let's Encrypt or similar)
4. The same security policies should be applied in the Ansible version
5. The FastAPI application source code will remain at the same GitHub repository
6. PostgreSQL and Redis passwords in the current configuration are for development only and will be replaced with secure values in production
7. The Vagrant setup is primarily for development/testing and may not be needed in the final Ansible configuration