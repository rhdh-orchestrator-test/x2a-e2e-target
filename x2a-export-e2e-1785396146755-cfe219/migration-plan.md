# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server setup with FastAPI application backend and caching services (Redis and Memcached). The migration to Ansible is estimated to be of moderate complexity with approximately 2-3 weeks of effort for a small team (2-3 engineers).

The repository uses Chef Solo with Berkshelf for dependency management and is designed to run in a Vagrant environment for development/testing. The configuration includes security hardening, SSL certificate management, and multiple virtual hosts.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw)

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Configures caching services (Memcached and Redis) with security settings
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Manages cookbook dependencies, including external dependencies from Chef Supermarket (nginx, memcached, redisio)
- `solo.json`: Defines the Chef run list and configuration attributes for Nginx sites, SSL, and security settings
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `Vagrantfile`: Defines the development VM configuration using Fedora 42, port forwarding, and resource allocation
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef Solo and Berkshelf

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ mentioned in cookbook metadata
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or local development

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW with specific rules for SSH, HTTP, and HTTPS. Ansible migration should use the `ansible.posix.firewalld` or `community.general.ufw` modules.
- **Fail2ban Setup**: The Chef cookbook configures fail2ban for brute force protection. Ansible migration should use the `community.general.fail2ban` module.
- **SSH Hardening**: The Chef cookbook disables root login and password authentication. Ansible migration should use the `ansible.posix.sshd_config` module.
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - SSL certificates are generated with self-signed certificates for development
  - Consider using Ansible Vault for all credentials in the migration

### Technical Challenges

- **Multi-site Nginx Configuration**: The Chef cookbook dynamically generates Nginx site configurations based on attributes. Ansible migration will need to use templates and loops to achieve similar functionality.
- **SSL Certificate Management**: The Chef cookbook generates self-signed certificates. Ansible migration should use the `community.crypto` collection for certificate management.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL. Ansible migration should use handlers and conditional checks to ensure proper service ordering.
- **Custom Ruby Logic**: The cache cookbook contains a Ruby block to modify Redis configuration files. Ansible migration will need to use the `lineinfile` or `replace` modules to achieve similar functionality.

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Add security hardening (fail2ban, ufw)
   - Add multi-site configuration

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis configuration with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Implement PostgreSQL installation and configuration
   - Implement Python environment setup
   - Implement application deployment from Git
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora-based, though the cookbooks support Ubuntu and CentOS as well.
2. The self-signed certificates are for development only and may be replaced with proper certificates in production.
3. The hardcoded credentials in the cookbooks are for development only and should be replaced with secure credentials management in production.
4. The Vagrant setup is primarily for development/testing and may not be needed in the production Ansible deployment.
5. The FastAPI application source code is available at the specified Git repository.
6. The current setup assumes a single-server deployment model; scaling considerations are not addressed.
7. The current setup does not include monitoring or logging solutions beyond basic system logging.