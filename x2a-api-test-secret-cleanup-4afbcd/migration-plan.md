# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup with three main cookbooks: nginx-multisite, cache, and fastapi-tutorial. The migration to Ansible will involve converting these cookbooks to Ansible roles and playbooks, preserving the functionality while adapting to Ansible's paradigms.

**Scope**: 3 Chef cookbooks with dependencies on external cookbooks
**Complexity**: Medium (standard web server, caching, and application deployment patterns)
**Timeline Estimate**: 2-3 weeks for complete migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw)

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

- `Berksfile`: Dependency management for Chef cookbooks - will be replaced by Ansible Galaxy requirements.yml
- `Vagrantfile`: VM configuration for development/testing - can be preserved with modifications to use Ansible provisioner
- `solo.json`: Chef node attributes and run list - will be converted to Ansible group_vars or host_vars
- `solo.rb`: Chef configuration - will be replaced by Ansible configuration
- `vagrant-provision.sh`: Shell script for Chef provisioning in Vagrant - will be replaced by Ansible provisioning

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting local development/testing environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or custom role
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy or custom role
- **redisio (~> 7.2.4)**: Replace with Ansible redis role from Galaxy or custom role

### Security Considerations

- **SSL Certificate Management**: 
  - Current approach uses self-signed certificates generated with OpenSSL
  - Migration approach: Use Ansible's openssl_* modules or community.crypto collection

- **Firewall Configuration (UFW)**:
  - Current approach configures UFW with specific rules
  - Migration approach: Use Ansible's ufw module

- **Fail2ban Configuration**:
  - Current approach installs and configures fail2ban
  - Migration approach: Use Ansible's template module for fail2ban configuration

- **SSH Hardening**:
  - Current approach modifies sshd_config to disable root login and password authentication
  - Migration approach: Use Ansible's lineinfile module or openssh_config module

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe
  - PostgreSQL credentials are hardcoded in the recipe
  - Migration approach: Use Ansible Vault for storing sensitive information

### Technical Challenges

- **Multi-site Nginx Configuration**:
  - Challenge: Preserving the dynamic site configuration capability
  - Mitigation: Use Ansible's with_items/loop constructs and templates to generate site configurations

- **Redis Configuration Hack**:
  - Challenge: The current Chef recipe includes a ruby_block to modify Redis configuration
  - Mitigation: Use Ansible's lineinfile module or template with proper configuration options

- **PostgreSQL User/Database Creation**:
  - Challenge: Current approach uses shell commands via execute resource
  - Mitigation: Use Ansible's postgresql_* modules for proper idempotent management

- **Service Dependencies**:
  - Challenge: Ensuring proper service ordering and dependencies
  - Mitigation: Use Ansible's handlers and meta dependencies between roles

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Add security hardening (fail2ban, ufw)
   - Add multi-site configuration

2. **cache** (low complexity, standalone services)
   - Implement Memcached configuration
   - Implement Redis configuration with authentication

3. **fastapi-tutorial** (high complexity, application deployment)
   - Implement PostgreSQL database setup
   - Implement Python environment and application deployment
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora-based systems (the Vagrantfile specifies Fedora 42)
2. Self-signed certificates are acceptable for development/testing (production would likely use Let's Encrypt or other CA)
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
4. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate for the target environment
5. The Redis configuration "hack" in the cache cookbook is addressing compatibility issues that may need investigation
6. The PostgreSQL database setup is for development purposes and may need additional security for production
7. The current Vagrant setup with libvirt provider will continue to be used for development/testing