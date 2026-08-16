# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration scope includes 3 Chef cookbooks with moderate complexity. Based on the repository analysis, we estimate a 2-3 week timeline for complete migration, with the most complex components being the Nginx multi-site configuration and security hardening.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening (fail2ban, UFW), and self-signed SSL certificates
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef run list and configuration data for the cookbooks
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Defines the development VM using Fedora 42, with port forwarding and network configuration
- `vagrant-provision.sh`: Shell script to provision the VM with Chef Solo

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_config module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package module
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package module with custom configuration

### Security Considerations

- **SSH Hardening**: Migration must preserve SSH security settings (root login disabled, password authentication disabled)
- **Firewall Configuration**: UFW rules need to be migrated to equivalent firewall module in Ansible
- **fail2ban Setup**: Configuration needs to be migrated to Ansible fail2ban role
- **SSL Certificates**: Self-signed certificate generation needs to be handled in Ansible
- **Vault/secrets management**: 
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL credentials in fastapi-tutorial cookbook: username "fastapi" with password "fastapi_password"
  - Total credentials detected: 2 hardcoded passwords that should be moved to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple virtual hosts with SSL will require careful templating in Ansible
- **Self-signed Certificate Generation**: Ensuring idempotent certificate generation in Ansible
- **Security Hardening**: Ensuring all security measures are properly implemented in Ansible equivalents
- **Database Configuration**: PostgreSQL user and database creation with proper permissions

### Migration Order

1. **cache cookbook** (low complexity, standalone functionality)
2. **nginx-multisite cookbook** (moderate complexity, core infrastructure)
3. **fastapi-tutorial cookbook** (moderate complexity, depends on database)

### Assumptions

1. The target environment will continue to be Fedora-based systems, with potential for Ubuntu/CentOS as indicated in cookbook metadata
2. The Vagrant development environment will be maintained but converted to use Ansible provisioner
3. Self-signed certificates are acceptable for the migrated solution (no Let's Encrypt or commercial certificates required)
4. The current security posture (fail2ban, UFW, SSH hardening) must be maintained in the Ansible solution
5. The FastAPI application will continue to be deployed from the same GitHub repository
6. The PostgreSQL database will remain local to the application server
7. Redis and Memcached configurations will maintain the same security settings
8. No high availability or clustering requirements are present in the current configuration