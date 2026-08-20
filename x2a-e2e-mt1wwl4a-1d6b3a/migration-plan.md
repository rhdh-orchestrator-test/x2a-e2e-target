# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration scope is moderate, consisting of three primary cookbooks with external dependencies. Based on the complexity and size, an estimated timeline of 2-3 weeks would be reasonable for a complete migration to Ansible, including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL setup, security hardening

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

- `Berksfile`: Manages cookbook dependencies, including external cookbooks from Chef Supermarket (nginx, memcached, redisio)
- `solo.json`: Contains the run list and configuration data for Chef Solo, including Nginx site configurations and security settings
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Defines the development VM configuration using Fedora 42

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) as specified in cookbook metadata, with Fedora 42 used in the Vagrant development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role (e.g., geerlingguy.redis)

### Security Considerations

- **SSL Configuration**: Migration must preserve SSL certificate paths and configurations for Nginx sites
  - Current paths: /etc/ssl/certs (certificates) and /etc/ssl/private (private keys)
  - Self-signed certificates are used in development

- **Redis Authentication**: Redis is configured with password authentication
  - Current password is hardcoded in the recipe as 'redis_secure_password_123'
  - Should be migrated to Ansible Vault for secure storage

- **PostgreSQL Credentials**: Database credentials for FastAPI application
  - Username: fastapi
  - Password: fastapi_password
  - Should be migrated to Ansible Vault

- **Security Hardening**: The nginx-multisite cookbook includes security configurations
  - Fail2ban integration
  - UFW firewall configuration
  - SSH hardening (root login disabled, password authentication disabled)

### Technical Challenges

- **Multi-site Nginx Configuration**: The current setup dynamically generates Nginx site configurations from node attributes. Ansible templates will need to replicate this dynamic behavior.
  - Solution: Use Ansible template module with Jinja2 templates to generate site configurations based on variables

- **Service Orchestration**: The current setup has interdependent services (Nginx, Redis, Memcached, PostgreSQL, FastAPI application)
  - Solution: Use Ansible handlers and dependencies to ensure proper service restart ordering

- **Environment Configuration**: The FastAPI application requires environment variables and a .env file
  - Solution: Use Ansible template module to generate the .env file with variables from Ansible Vault

- **PostgreSQL User and Database Setup**: The current setup uses direct PostgreSQL commands
  - Solution: Use Ansible's postgresql_user and postgresql_db modules for cleaner implementation

### Migration Order

1. **cache cookbook** (Low complexity, foundational services)
   - Implement Redis and Memcached roles
   - Configure authentication and basic settings

2. **nginx-multisite cookbook** (Medium complexity, core infrastructure)
   - Implement Nginx installation and configuration
   - Set up SSL certificates
   - Configure virtual hosts
   - Implement security hardening

3. **fastapi-tutorial cookbook** (High complexity, application deployment)
   - Set up PostgreSQL database
   - Deploy FastAPI application from Git
   - Configure Python environment
   - Set up systemd service

### Assumptions

1. The migration will maintain the same target operating systems (Ubuntu 18.04+ and CentOS 7+)
2. Self-signed certificates will continue to be used for development environments
3. The FastAPI application source code will remain at the same Git repository
4. The current directory structure for web content (/var/www/[site]) will be preserved
5. The PostgreSQL database schema does not require migration, only the database and user creation
6. The current security configurations (fail2ban, ufw, SSH hardening) are sufficient and will be migrated as-is
7. The Vagrant development environment will be replaced with an equivalent Ansible-based setup
8. Redis and Memcached configurations will maintain the same port numbers and basic settings