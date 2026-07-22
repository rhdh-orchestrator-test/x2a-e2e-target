# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with FastAPI application backend and caching services (Redis and Memcached). The migration scope includes 3 Chef cookbooks with moderate complexity. Based on the repository analysis, we estimate a 2-3 week timeline for complete migration, with the most complex components being the Nginx multi-site SSL configuration and security hardening.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and proper SSL certificate management
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall), sysctl security settings

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

- `Berksfile`: Manages cookbook dependencies - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Contains node configuration data - will be migrated to Ansible group_vars and host_vars
- `solo.rb`: Chef configuration file - will be replaced by Ansible configuration
- `Vagrantfile`: Defines development VM - will need updates for Ansible provisioning
- `vagrant-provision.sh`: Provisions the Vagrant VM with Chef - will be replaced with Ansible provisioning

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ based on cookbook metadata
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or memcached module
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or redis module
- **PostgreSQL**: Replace with Ansible postgresql role or postgresql_* modules

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW with specific rules for SSH, HTTP, and HTTPS. Migration should use Ansible's ufw module to maintain identical rules.
- **Fail2Ban Setup**: The cookbook configures fail2ban for brute force protection. Use Ansible's fail2ban module or a dedicated role.
- **SSH Hardening**: The cookbook disables root login and password authentication. Use Ansible's ssh_config module to maintain these settings.
- **SSL Certificate Management**: Self-signed certificates are generated for each site. Use Ansible's openssl_* modules to generate certificates.
- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123" (hardcoded)
  - PostgreSQL password in fastapi-tutorial cookbook: "fastapi_password" (hardcoded)
  - Both should be migrated to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The current setup dynamically creates Nginx site configurations based on node attributes. Ansible templates will need to replicate this dynamic behavior.
- **SSL Certificate Generation**: Self-signed certificates are generated for each site. Ansible will need to handle certificate generation and proper file permissions.
- **System Tuning**: The Chef cookbook applies sysctl security settings. Ansible will need to use the sysctl module to apply the same settings.
- **Service Orchestration**: The current setup manages multiple interdependent services (Nginx, PostgreSQL, Redis, Memcached, FastAPI application). Ansible will need to maintain the correct order of operations.

### Migration Order

1. **cache cookbook** (low complexity, fewer dependencies)
   - Memcached and Redis configuration
   - Move hardcoded Redis password to Ansible Vault

2. **fastapi-tutorial cookbook** (moderate complexity)
   - Python environment setup
   - PostgreSQL database configuration
   - Application deployment and service setup
   - Move database credentials to Ansible Vault

3. **nginx-multisite cookbook** (high complexity)
   - Base Nginx configuration
   - Security hardening (fail2ban, ufw, sysctl)
   - SSL certificate generation
   - Virtual host configuration

### Assumptions

1. The current Chef setup is functional and represents the desired end state.
2. The target environment will continue to be Fedora 42 or compatible Linux distributions.
3. Self-signed certificates are acceptable for the migrated solution (no integration with Let's Encrypt or other CA).
4. The FastAPI application source will continue to be pulled from the same Git repository.
5. The Vagrant development environment should be preserved with equivalent functionality.
6. No additional monitoring or logging requirements beyond what's in the current Chef configuration.
7. The security hardening approach (fail2ban, ufw, sysctl settings) should be maintained.
8. Redis and PostgreSQL passwords are currently hardcoded and should be secured in Ansible Vault.