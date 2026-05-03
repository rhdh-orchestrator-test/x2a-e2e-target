# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup with three primary cookbooks: nginx-multisite, cache, and fastapi-tutorial. The migration to Ansible will involve converting these cookbooks to Ansible roles while maintaining the same functionality and security practices. Based on the complexity and dependencies, we estimate a medium-complexity migration that should take approximately 3-4 weeks with 1-2 dedicated engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and proper SSL configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, fail2ban integration, UFW firewall configuration

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

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4)
- `solo.json`: Contains the run list and configuration data for nginx sites and security settings
- `solo.rb`: Chef Solo configuration file defining cookbook paths and log settings
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Defines the Vagrant VM configuration (Fedora 42) with port forwarding and networking

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile) with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development/testing

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks
- **PostgreSQL**: Replace with Ansible postgresql_* modules or community.postgresql collection

### Security Considerations

- **SSL Certificate Management**: 
  - Current approach uses self-signed certificates generated with OpenSSL
  - Migration approach: Use ansible.builtin.openssl_* modules or community.crypto collection

- **Firewall Configuration**: 
  - Current approach uses UFW with specific allow rules
  - Migration approach: Use ansible.posix.firewalld or ansible.builtin.ufw modules

- **Fail2ban Integration**: 
  - Current approach configures fail2ban with custom jail settings
  - Migration approach: Use community.general.fail2ban module or custom templates

- **SSH Hardening**: 
  - Current approach disables root login and password authentication
  - Migration approach: Use ansible.posix.sshd module or custom templates

- **Vault/secrets management**:
  - Redis password hardcoded in recipe: "redis_secure_password_123"
  - PostgreSQL credentials hardcoded in recipe: "fastapi:fastapi_password"
  - FastAPI environment variables with database connection string
  - Migration approach: Use Ansible Vault for all credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Maintaining the dynamic generation of multiple site configurations
  - Mitigation: Use Ansible with_items/loop constructs with templates similar to the Chef approach

- **SSL Certificate Generation**: 
  - Challenge: Ensuring proper permissions and security for SSL certificates
  - Mitigation: Use ansible.builtin.file module with appropriate permissions and owner/group settings

- **Service Orchestration**: 
  - Challenge: Ensuring services start in the correct order with proper dependencies
  - Mitigation: Use Ansible handlers and meta dependencies between roles

- **Database Initialization**: 
  - Challenge: Creating PostgreSQL users and databases idempotently
  - Mitigation: Use community.postgresql collection with appropriate when conditions

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Moderate complexity with templates and security configurations

2. **cache** (Priority 2)
   - Simple configuration but depends on external modules
   - Lower complexity than other components

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on both nginx and database
   - Higher complexity with Python environment, Git, and database setup

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions
2. The same security requirements will apply in the Ansible implementation
3. Self-signed certificates are acceptable for development (production would likely use Let's Encrypt or similar)
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current network configuration with port forwarding (80→8080, 443→8443) will be maintained
6. The VM specifications (2GB RAM, 2 CPUs) will remain the same
7. No additional monitoring or logging requirements beyond what's in the current Chef implementation
8. The migration will not involve changes to the application code or database schema