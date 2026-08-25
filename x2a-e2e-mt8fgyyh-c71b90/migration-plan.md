# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration scope is moderate, involving three primary cookbooks with external dependencies. Based on the complexity and number of components, we estimate a 2-3 week timeline for a complete migration to Ansible, with testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL setup, security hardening (fail2ban, firewall)

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

- `Berksfile`: Chef dependency management file listing cookbook dependencies and versions
- `solo.json`: Chef configuration data including run list and node attributes
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `vagrant-provision.sh`: Bash script for provisioning Chef in a Vagrant VM
- `Vagrantfile`: Vagrant configuration for local development/testing environment

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ mentioned in cookbook metadata
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)

### Security Considerations

- **SSL Certificate Management**: The nginx-multisite cookbook manages SSL certificates in `/etc/ssl/certs` and `/etc/ssl/private`. Migration should preserve this structure or implement a more robust solution like Let's Encrypt with Ansible.
- **Redis Authentication**: Redis is configured with password authentication (`requirepass: 'redis_secure_password_123'`). This should be migrated to Ansible Vault for secure storage.
- **PostgreSQL Credentials**: The FastAPI application uses PostgreSQL with hardcoded credentials (`fastapi:fastapi_password`). These should be migrated to Ansible Vault.
- **Security Hardening**: The nginx-multisite cookbook implements security measures including:
  - fail2ban configuration
  - UFW firewall rules
  - SSH hardening (root login disabled, password authentication disabled)
  - These should be preserved in the Ansible migration.
- **Vault/secrets management**: 
  - 2 hardcoded credentials detected in cache cookbook (Redis password)
  - 2 hardcoded credentials detected in fastapi-tutorial cookbook (PostgreSQL username/password)
  - Environment variables with sensitive data in .env file for FastAPI application

### Technical Challenges

- **Multi-site Nginx Configuration**: The current setup dynamically generates Nginx site configurations based on node attributes. This pattern needs to be replicated in Ansible using templates and variables.
- **Service Orchestration**: The current setup has interdependent services (Nginx, Redis, Memcached, PostgreSQL, FastAPI application). The Ansible playbook must maintain proper service ordering and dependencies.
- **Python Environment Management**: The FastAPI application uses a Python virtual environment. Ansible must replicate this setup correctly.
- **SSL Certificate Handling**: The migration must ensure proper handling of SSL certificates, potentially integrating with Ansible's certificate management capabilities.

### Migration Order

1. **cache cookbook** (low complexity, foundational services)
   - Implement Redis and Memcached roles
   - Migrate configuration settings
   - Secure passwords with Ansible Vault

2. **nginx-multisite cookbook** (moderate complexity)
   - Implement Nginx installation and configuration
   - Migrate SSL certificate management
   - Implement security hardening features
   - Set up multi-site configuration

3. **fastapi-tutorial cookbook** (higher complexity)
   - Implement PostgreSQL database setup
   - Configure Python environment and application deployment
   - Set up systemd service
   - Integrate with Nginx configuration

### Assumptions

1. The current Chef setup is functional and represents the desired end state
2. SSL certificates are self-signed for development (based on Vagrant setup)
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git is accessible and contains the required code
4. The target environment will continue to be Fedora-based, though the cookbooks support Ubuntu and CentOS
5. No CI/CD pipeline integration is required as part of the migration
6. The current security configurations (fail2ban, UFW, SSH hardening) are sufficient and should be maintained
7. The Vagrant development environment should be preserved or replaced with an equivalent Ansible-based setup