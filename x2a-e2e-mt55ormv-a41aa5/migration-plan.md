# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration scope is moderate, consisting of three primary cookbooks with external dependencies. Based on the complexity and size, this migration is estimated to take approximately 2-3 weeks with 1-2 dedicated engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, including security hardening
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate management, security hardening (fail2ban, ufw)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Manages Chef cookbook dependencies, including external cookbooks from Chef Supermarket (nginx, memcached, redisio)
- `solo.json`: Contains Chef run list and configuration data for Nginx sites and security settings
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `Vagrantfile`: Defines a Vagrant VM for development/testing with port forwarding and network configuration
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef Solo

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ mentioned in cookbook metadata
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or custom role
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role from Galaxy

### Security Considerations

- **SSL Certificate Management**: 
  - Migration approach: Use Ansible's `openssl_*` modules for certificate management
  - Current implementation uses self-signed certificates stored in `/etc/ssl/certs` and `/etc/ssl/private`

- **Redis Authentication**:
  - Migration approach: Use Ansible Vault for storing Redis password
  - Current implementation has hardcoded password: 'redis_secure_password_123'

- **PostgreSQL Authentication**:
  - Migration approach: Use Ansible Vault for storing database credentials
  - Current implementation has hardcoded username/password: 'fastapi'/'fastapi_password'

- **Security Hardening**:
  - Migration approach: Use Ansible security roles or dedicated tasks
  - Current implementation configures fail2ban, ufw, and SSH hardening

- **Vault/secrets management**:
  - 3 credentials detected:
    - Redis password (hardcoded in cache/recipes/default.rb)
    - PostgreSQL username and password (hardcoded in fastapi-tutorial/recipes/default.rb)
    - FastAPI environment variables (hardcoded in fastapi-tutorial/recipes/default.rb)

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation dynamically generates multiple virtual host configurations
  - Mitigation: Use Ansible templates with loops to generate similar configurations

- **Service Orchestration**: 
  - Description: The current implementation has interdependent services (PostgreSQL → FastAPI, Nginx → FastAPI)
  - Mitigation: Use Ansible handlers and proper dependency ordering

- **Configuration Customization**:
  - Description: The Redis configuration includes custom modifications via a ruby_block
  - Mitigation: Use Ansible templates with conditional sections or lineinfile module

### Migration Order

1. **cache cookbook** (low risk, standalone services)
   - Implement Memcached configuration
   - Implement Redis configuration with proper secret management

2. **fastapi-tutorial cookbook** (moderate complexity)
   - Implement PostgreSQL database setup
   - Implement Python application deployment
   - Implement systemd service configuration

3. **nginx-multisite cookbook** (high complexity, depends on FastAPI)
   - Implement base Nginx installation
   - Implement SSL certificate management
   - Implement virtual host configuration
   - Implement security hardening

### Assumptions

1. The current Chef implementation is complete and functional
2. Self-signed certificates are acceptable for the migrated solution
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git is accessible and stable
4. The target environment will continue to be Fedora-based systems
5. No CI/CD pipeline integration is required as part of the migration
6. The Vagrant development environment is not critical to preserve (could be replaced with Ansible-based alternative)
7. No monitoring or logging solutions need to be integrated
8. The current security configurations (fail2ban, ufw, SSH hardening) are sufficient