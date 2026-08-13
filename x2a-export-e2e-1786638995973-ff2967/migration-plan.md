# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible is estimated to be of moderate complexity, with an estimated timeline of 2-3 weeks for a single developer or 1-2 weeks for a small team.

The repository uses Chef Solo with Berkshelf for dependency management. The infrastructure consists of three main cookbooks: nginx-multisite, cache, and fastapi-tutorial. The environment is designed to run on a Vagrant VM with Fedora 42.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificates
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall)

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
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and logging settings
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM, installing Chef and Berkshelf
- `Vagrantfile`: Defines the Vagrant VM configuration (Fedora 42, networking, port forwarding)

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development/testing

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package module
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package module

### Security Considerations

- **Firewall Configuration**: The current setup uses UFW for firewall management. Ansible provides the `ufw` module for Ubuntu or `firewalld` module for Fedora/CentOS.
- **Fail2ban Configuration**: The current setup configures fail2ban for intrusion prevention. Ansible has modules to manage fail2ban.
- **SSH Hardening**: The current setup disables root login and password authentication. Ansible provides the `sshd` module to manage SSH configuration.
- **SSL Certificate Management**: Self-signed certificates are generated for each site. Ansible provides the `openssl_*` modules for certificate management.
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL database credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - These should be migrated to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The current setup dynamically creates Nginx site configurations based on node attributes. Ansible templates will need to replicate this dynamic behavior.
- **SSL Certificate Generation**: Self-signed certificates are generated for each site. Ansible's `openssl_*` modules will need to be used to replicate this functionality.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL. Ansible handlers and meta dependencies will need to be used to ensure proper service ordering.
- **Idempotent Database Setup**: The current setup uses PostgreSQL commands to create users and databases. Ansible's `postgresql_*` modules should be used for idempotent database management.

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Add virtual host configuration
   - Add security hardening (fail2ban, ufw)

2. **cache** (low complexity, independent service)
   - Configure Memcached
   - Configure Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Set up PostgreSQL database and user
   - Deploy FastAPI application from Git
   - Configure Python virtual environment and dependencies
   - Set up systemd service

### Assumptions

1. The target environment will continue to be Fedora-based, though the cookbooks support Ubuntu and CentOS as well.
2. The self-signed certificates are for development/testing purposes only and not for production use.
3. The current setup assumes a single-server deployment model, which will be maintained in the Ansible migration.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git is accessible and will remain available.
5. The Redis configuration hack in the cache cookbook is addressing compatibility issues that may need investigation during migration.
6. The current setup does not include backup or monitoring solutions, which might be considered for addition during migration.
7. The Vagrant configuration suggests this is primarily a development/testing environment rather than production.