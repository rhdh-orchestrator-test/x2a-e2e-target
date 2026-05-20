# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup with three primary cookbooks: nginx-multisite, cache, and fastapi-tutorial. The infrastructure appears to be designed for a development or testing environment using Vagrant with Fedora 42. The migration to Ansible is estimated to be of moderate complexity with an approximate timeline of 2-3 weeks for a small team (2-3 members).

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificates
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall)

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

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints.
- `Vagrantfile`: Defines the development VM using Fedora 42 with port forwarding and resource allocation.
- `solo.json`: Chef Solo configuration file defining the run list and node attributes for Nginx sites and security settings.
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and logging settings.
- `vagrant-provision.sh`: Bash script that installs Chef and Berkshelf, then runs Chef Solo in the Vagrant VM.

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ mentioned in cookbook metadata
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development/testing

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package module
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package module with custom configuration

### Security Considerations

- **Firewall Configuration**: UFW firewall rules need to be migrated to appropriate Ansible firewalld or ufw modules
- **fail2ban**: Configuration needs to be migrated to Ansible fail2ban role or template module
- **SSH Hardening**: SSH configuration (disable root login, password authentication) needs to be migrated to Ansible ssh_config module
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - These should be migrated to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple Nginx sites with SSL certificates will require careful templating in Ansible
- **Self-signed Certificate Generation**: The OpenSSL commands for generating self-signed certificates need to be migrated to Ansible's openssl_* modules
- **Redis Configuration Hack**: The Chef cookbook includes a Ruby block to modify Redis configuration files after they're created, which will need a custom approach in Ansible
- **PostgreSQL User/Database Creation**: The current implementation uses direct psql commands which should be replaced with Ansible's postgresql_* modules

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Implement security hardening (fail2ban, firewall)
   - Configure virtual hosts

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, application deployment)
   - Set up PostgreSQL database and user
   - Deploy Python application from Git
   - Configure virtual environment and dependencies
   - Create systemd service

### Assumptions

1. The target environment will continue to be Fedora-based (the Vagrantfile specifies Fedora 42)
2. Self-signed certificates are acceptable (production would likely use Let's Encrypt or other CA)
3. The current security settings (fail2ban, UFW, SSH hardening) should be maintained
4. The Redis and PostgreSQL passwords in the code are development credentials and will be replaced with secure values in Ansible Vault
5. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
6. The current port mappings and network configuration will be maintained
7. No high availability or clustering is required based on the current configuration