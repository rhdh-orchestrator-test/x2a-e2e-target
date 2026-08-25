# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with FastAPI application backend and caching services. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Scope**: 3 Chef cookbooks with external dependencies
**Complexity**: Medium
**Estimated Timeline**: 2-3 weeks

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures nginx with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, fail2ban integration, UFW firewall setup, security hardening

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Configures caching services (memcached and redis) with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external dependencies.
- `solo.json`: Chef configuration file containing the run list and node attributes.
- `solo.rb`: Chef configuration file specifying cookbook paths and logging settings.
- `Vagrantfile`: Defines a Vagrant VM for testing the Chef cookbooks on Fedora 42.
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` role or direct package installation and configuration

### Security Considerations

- **SSL Certificate Management**: The Chef cookbook generates self-signed certificates for development. In Ansible, use the `openssl_*` modules or `community.crypto` collection.
- **Firewall Configuration**: The Chef cookbook configures UFW. In Ansible, use the `ufw` module or `ansible.posix.firewall` collection.
- **fail2ban Configuration**: The Chef cookbook configures fail2ban. In Ansible, use the `community.general.fail2ban` module.
- **SSH Hardening**: The Chef cookbook disables root login and password authentication. In Ansible, use the `ansible.posix.ssh` module.
- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123" (hardcoded)
  - PostgreSQL database credentials in fastapi-tutorial cookbook: username "fastapi" with password "fastapi_password" (hardcoded)
  - Total credentials detected: 2 hardcoded passwords

### Technical Challenges

- **Multi-site Nginx Configuration**: The Chef cookbook uses templates and attributes to configure multiple Nginx sites. In Ansible, use templates with variables to achieve the same functionality.
- **SSL Certificate Generation**: The Chef cookbook generates self-signed certificates. In Ansible, use the `openssl_certificate` module.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL. In Ansible, use handlers and the `meta` dependency system to ensure proper ordering.
- **Redis Configuration Hack**: The Chef cookbook includes a ruby_block to modify Redis configuration. In Ansible, use templates or the `lineinfile` module to achieve the same result.

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Create Ansible role for Nginx installation and configuration
   - Create templates for virtual hosts, SSL, and security configurations
   - Implement firewall and fail2ban configurations

2. **cache** (moderate complexity, depends on external modules)
   - Create Ansible role for Memcached and Redis installation
   - Configure Redis with authentication
   - Ensure proper service management

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Create Ansible role for Python environment setup
   - Implement PostgreSQL installation and configuration
   - Configure application deployment and systemd service

### Assumptions

1. The target environment will continue to be Fedora-based systems (the Vagrantfile specifies Fedora 42).
2. The self-signed certificates are acceptable for the migrated solution, or certificates will be provided externally.
3. The hardcoded passwords in the Chef recipes will be replaced with Ansible Vault variables.
4. The directory structure for web content (/var/www/[site]) will remain the same.
5. The FastAPI application source will continue to be pulled from the same Git repository.
6. The Vagrant setup will be maintained for development and testing purposes.
7. The migration will not change the functionality or configuration of the services, only the deployment method.