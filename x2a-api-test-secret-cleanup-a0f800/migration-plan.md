# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for migration is 3-4 weeks, with moderate complexity due to the multi-component architecture and security configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and fail2ban/ufw firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, firewall configuration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4)
- `solo.json`: Defines the Chef run list and configuration attributes for nginx sites and security settings
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Defines the Vagrant VM configuration (Fedora 42) with port forwarding and networking

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development/testing

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or collection (e.g., `ansible.posix.nginx`)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., `geerlingguy.memcached`)
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role (e.g., `geerlingguy.redis`)
- **PostgreSQL**: Replace with Ansible PostgreSQL role (e.g., `geerlingguy.postgresql`)

### Security Considerations

- **SSL Certificate Management**: 
  - Current approach uses self-signed certificates generated with OpenSSL
  - Migration should maintain or improve this with Ansible's `openssl_*` modules
  - Consider integrating with Let's Encrypt for production environments

- **Firewall Configuration**: 
  - Current implementation uses UFW
  - Migrate to Ansible's `ufw` module or `firewalld` module for Fedora

- **Fail2ban Integration**:
  - Migrate fail2ban configuration to Ansible using the `template` module
  - Ensure service is properly enabled and configured

- **SSH Hardening**:
  - Maintain SSH security settings (disable root login, password authentication)
  - Use Ansible's `lineinfile` or `template` modules for sshd_config

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL password is hardcoded in the recipe (`fastapi_password`)
  - Migrate these to Ansible Vault for secure storage

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Dynamically generating multiple virtual host configurations
  - Mitigation: Use Ansible loops with templates to generate site configurations

- **SSL Certificate Generation**:
  - Challenge: Replicating the self-signed certificate generation logic
  - Mitigation: Use Ansible's `openssl_certificate` module with proper idempotency checks

- **Service Orchestration**:
  - Challenge: Ensuring proper service start order (PostgreSQL before FastAPI)
  - Mitigation: Use Ansible handlers and dependencies between roles

- **Python Environment Management**:
  - Challenge: Setting up Python virtual environment and dependencies
  - Mitigation: Use Ansible's `pip` module with virtualenv support

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx configuration, then add SSL and security features

2. **cache** (Priority 2)
   - Independent service that can be migrated after Nginx
   - Moderate complexity due to Redis configuration

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on PostgreSQL
   - Higher complexity due to database setup and application deployment

### Assumptions

1. The target environment will continue to be Fedora 42 or similar Linux distribution
2. Self-signed certificates are acceptable for development (production would need proper certificates)
3. The same network configuration (ports, IP addresses) will be maintained
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current security settings (fail2ban, ufw, SSH hardening) are appropriate for the target environment
6. No custom Chef resources or libraries are being used that would require special handling
7. The PostgreSQL database schema is managed by the FastAPI application, not by Chef
8. The current Redis configuration workarounds (ruby_block "fix_redis_config") will not be needed in Ansible