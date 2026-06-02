# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site web server with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated complexity is medium, with security configurations and multiple service integrations requiring careful attention. The estimated timeline for migration is 3-4 weeks with 1-2 engineers.

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
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment, Git repository deployment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks, lists external dependencies (nginx, memcached, redisio)
- `solo.json`: Chef run list and node attributes configuration, defines site configurations and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Defines development VM using Fedora 42, port forwarding, and provisioning
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create custom Nginx role
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or DavidWittman.redis

### Security Considerations

- **SSL Certificate Management**: 
  - Migration approach: Use Ansible `openssl_*` modules to generate self-signed certificates
  - Consider integration with Let's Encrypt using `geerlingguy.certbot` role for production

- **Firewall Configuration**: 
  - Migration approach: Use Ansible `ufw` module to configure firewall rules
  - Ensure idempotent rule application

- **SSH Hardening**: 
  - Migration approach: Use Ansible `lineinfile` module to modify SSH configuration
  - Consider using `dev-sec.ssh-hardening` role for comprehensive SSH security

- **Fail2ban Configuration**: 
  - Migration approach: Use Ansible template module to create fail2ban configuration
  - Ensure service is enabled and running

- **Vault/secrets management**:
  - Redis password in cache cookbook (hardcoded as 'redis_secure_password_123')
  - PostgreSQL credentials in fastapi-tutorial cookbook (hardcoded as 'fastapi_password')
  - Consider using Ansible Vault to secure these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current Chef implementation dynamically generates Nginx site configurations from node attributes
  - Mitigation strategy: Use Ansible templates with loops to generate site configurations from variables

- **SSL Certificate Generation**: 
  - Description: Self-signed certificates are generated for each site
  - Mitigation strategy: Use Ansible's `openssl_certificate` module with proper idempotency checks

- **Redis Configuration Patching**: 
  - Description: The Chef cookbook uses a ruby_block to modify Redis configuration
  - Mitigation strategy: Create a proper Redis configuration template in Ansible rather than modifying files after creation

- **PostgreSQL User/Database Creation**: 
  - Description: Current implementation uses shell commands via execute resource
  - Mitigation strategy: Use Ansible's `postgresql_*` modules for proper idempotent database management

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Create base Nginx role
   - Implement SSL certificate generation
   - Configure virtual hosts
   - Implement security hardening

2. **cache** (moderate complexity)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper service management

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Implement PostgreSQL installation and configuration
   - Configure Python environment and application deployment
   - Set up systemd service

### Assumptions

1. The target environment will continue to be Fedora-based systems (Fedora 42 as specified in Vagrantfile)
2. Self-signed certificates are acceptable for development, but production may require proper CA-signed certificates
3. The security configurations (fail2ban, ufw, SSH hardening) are required in the migrated solution
4. The current hardcoded credentials will be replaced with more secure credential management
5. The FastAPI application source code will remain available at the specified Git repository
6. The multi-site configuration pattern will be maintained with the same domain structure
7. Redis and Memcached configurations will maintain the same port and basic settings
8. The PostgreSQL database will maintain the same name and access patterns