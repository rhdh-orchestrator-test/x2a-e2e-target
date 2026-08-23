# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration scope is moderate, consisting of three primary cookbooks with external dependencies. Based on the complexity and size, this migration is estimated to take 2-3 weeks with 1-2 engineers.

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

- `Berksfile`: Manages cookbook dependencies - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Contains node configuration and attributes - will be replaced by Ansible group_vars and host_vars
- `solo.rb`: Chef configuration file - will be replaced by ansible.cfg
- `Vagrantfile`: Defines the development VM - can be adapted for Ansible with minimal changes
- `vagrant-provision.sh`: Provisioning script for Vagrant - will be replaced by Ansible playbook calls

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>=18.04) and CentOS (>=7.0), with Fedora 42 used in Vagrant development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)

### Security Considerations

- **SSL Configuration**: The nginx-multisite cookbook manages SSL certificates in `/etc/ssl/certs` and `/etc/ssl/private`. Migration should preserve these paths or update references.
- **Redis Authentication**: Redis is configured with password authentication (`redis_secure_password_123`). This should be migrated to Ansible Vault.
- **PostgreSQL Credentials**: The FastAPI application uses PostgreSQL with hardcoded credentials (`fastapi:fastapi_password`). These should be migrated to Ansible Vault.
- **Fail2ban Configuration**: Security hardening includes fail2ban setup that should be preserved.
- **UFW Firewall**: Security configuration includes UFW firewall that should be migrated.
- **SSH Hardening**: SSH configuration disables root login and password authentication.
- **Vault/secrets management**:
  - Hardcoded Redis password in cache/recipes/default.rb
  - Hardcoded PostgreSQL credentials in fastapi-tutorial/recipes/default.rb
  - Hardcoded FastAPI environment variables in fastapi-tutorial/recipes/default.rb

### Technical Challenges

- **Multi-site Nginx Configuration**: The nginx-multisite cookbook dynamically creates site configurations based on node attributes. This pattern will need to be replicated in Ansible using templates and variables.
- **Redis Configuration Hacks**: The cache cookbook includes a Ruby block to modify Redis configuration files after they're created. This will need a custom approach in Ansible.
- **FastAPI Application Deployment**: The deployment process involves Git cloning, virtual environment setup, and systemd service configuration. This workflow needs to be carefully preserved.
- **SSL Certificate Management**: The current setup appears to use self-signed certificates. Consider integrating with Ansible's crypto modules or certbot for Let's Encrypt.

### Migration Order

1. **nginx-multisite cookbook** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation and configuration
   - Add SSL support
   - Implement multi-site configuration
   - Add security hardening features

2. **cache cookbook** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper service management

3. **fastapi-tutorial cookbook** (high complexity, depends on PostgreSQL)
   - Set up PostgreSQL database
   - Deploy FastAPI application from Git
   - Configure Python environment
   - Set up systemd service

### Assumptions

1. The current Chef setup is functional and represents the desired end state.
2. Self-signed certificates are acceptable for the migrated solution, or certificates will be provided externally.
3. The Vagrant development environment should be preserved with minimal changes.
4. The FastAPI application source code is available at the specified Git repository.
5. The migration will maintain the same directory structure and file paths for application data.
6. The security configurations (fail2ban, UFW, SSH hardening) are required in the migrated solution.
7. The Redis configuration hack is necessary due to compatibility issues that may need investigation.
8. The current setup does not use Chef environments or roles that would need migration.