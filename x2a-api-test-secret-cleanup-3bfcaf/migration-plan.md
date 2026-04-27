# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 3-4 weeks, with moderate complexity due to the multi-site configuration and security considerations.

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
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef configuration file containing the run list and node attributes
- `solo.rb`: Chef configuration file specifying cookbook paths and log settings
- `Vagrantfile`: Defines the development VM configuration using Fedora 42
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora (based on Vagrantfile specifying "generic/fedora42"), with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Libvirt (specified in Vagrantfile)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create custom Nginx role
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or DavidWittman.redis

### Security Considerations

- **SSL Certificate Management**: 
  - Migration approach: Use Ansible's `openssl_*` modules for certificate generation
  - Consider integration with Let's Encrypt using `geerlingguy.certbot` role for production environments

- **Firewall Configuration (UFW)**:
  - Migration approach: Use Ansible's `ufw` module to manage firewall rules

- **Fail2ban Integration**:
  - Migration approach: Create an Ansible role for fail2ban configuration using templates

- **SSH Hardening**:
  - Migration approach: Use Ansible's `lineinfile` module or the `dev-sec.ssh-hardening` Galaxy role

- **Vault/secrets management**:
  - Redis password in cache cookbook (hardcoded as 'redis_secure_password_123')
  - PostgreSQL credentials in fastapi-tutorial cookbook (hardcoded as 'fastapi_password')
  - Consider using Ansible Vault for storing these credentials securely

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current Chef implementation dynamically generates Nginx site configurations based on node attributes
  - Mitigation strategy: Create Ansible templates for Nginx site configurations and use loops to iterate through site definitions

- **SSL Certificate Generation**:
  - Description: Self-signed certificates are generated for each site
  - Mitigation strategy: Use Ansible's `openssl_certificate` module with proper idempotency checks

- **Service Dependencies**:
  - Description: The FastAPI application depends on PostgreSQL being configured first
  - Mitigation strategy: Use Ansible handlers and proper task ordering to ensure dependencies are met

### Migration Order

1. **cache** (Priority 1 - low risk, foundational service)
   - Simple configuration of Memcached and Redis services
   - Few dependencies and straightforward migration path

2. **nginx-multisite** (Priority 2 - moderate complexity)
   - Core web server configuration with security hardening
   - Multiple templates and security configurations to migrate

3. **fastapi-tutorial** (Priority 3 - application layer)
   - Depends on PostgreSQL and Python environment
   - Application deployment should come after infrastructure components

### Assumptions

1. The target environment will continue to be Fedora-based systems, with potential support for Ubuntu and CentOS as specified in the cookbook metadata
2. The self-signed SSL certificates approach is acceptable for development, but production environments may require proper certificates
3. The current security configurations (fail2ban, UFW, SSH hardening) are required in the migrated solution
4. The Redis and PostgreSQL passwords in the current code are development passwords and will be replaced with proper secrets management in production
5. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
6. The current multi-site configuration with test.cluster.local, ci.cluster.local, and status.cluster.local domains will be maintained
7. The Vagrant development environment will be replaced with an equivalent Ansible-based local development solution