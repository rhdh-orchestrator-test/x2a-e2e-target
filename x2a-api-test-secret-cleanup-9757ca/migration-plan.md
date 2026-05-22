# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup with three main cookbooks: nginx-multisite, cache, and fastapi-tutorial. The migration to Ansible will involve converting Chef recipes, templates, and attributes to Ansible roles, tasks, templates, and variables. The estimated timeline for migration is 3-4 weeks, with moderate complexity due to the interdependencies between components and security configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and fail2ban/ufw firewall setup
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
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database provisioning, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file listing cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef run list and node attributes configuration
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Defines development VM using Fedora 42, with port forwarding and resource allocation
- `vagrant-provision.sh`: Bash script to provision the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create custom Ansible tasks
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or DavidWittman.redis

### Security Considerations

- **SSL Certificate Management**: 
  - Migration approach: Use Ansible's `openssl_*` modules to generate self-signed certificates
  - Consider integrating with Ansible Vault for certificate storage

- **Firewall Configuration (UFW)**:
  - Migration approach: Use Ansible's `ufw` module to configure firewall rules

- **Fail2ban Configuration**:
  - Migration approach: Use Ansible Galaxy role `geerlingguy.security` or create custom tasks

- **SSH Hardening**:
  - Migration approach: Use Ansible's `lineinfile` module or the `geerlingguy.security` role

- **Vault/secrets management**:
  - Redis password: Currently hardcoded in the cache cookbook as "redis_secure_password_123"
  - PostgreSQL credentials: Hardcoded in the fastapi-tutorial cookbook as "fastapi" / "fastapi_password"
  - Migration approach: Move all credentials to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current Chef implementation uses a dynamic approach to configure multiple Nginx sites
  - Mitigation strategy: Use Ansible loops with templates to achieve similar functionality

- **Service Dependencies**:
  - Description: The FastAPI application depends on PostgreSQL being configured first
  - Mitigation strategy: Use Ansible handlers and proper task ordering to ensure dependencies are met

- **SSL Certificate Generation**:
  - Description: Self-signed certificates are generated for each site
  - Mitigation strategy: Use Ansible's `openssl_*` modules with proper conditionals

- **Redis Configuration Patching**:
  - Description: The Chef cookbook uses a ruby_block to modify Redis configuration
  - Mitigation strategy: Create a proper Ansible template for Redis configuration instead of patching

### Migration Order

1. **nginx-multisite** (moderate complexity)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Implement security configurations (fail2ban, ufw)
   - Configure virtual hosts

2. **cache** (low complexity)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity)
   - Set up PostgreSQL database
   - Deploy Python application with virtual environment
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions.
2. Self-signed certificates are acceptable for development; production would require proper certificates.
3. The security requirements (fail2ban, ufw, SSH hardening) will remain the same.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The current hardcoded credentials will be replaced with more secure, environment-specific credentials.
6. The Nginx configuration will maintain the same security headers and SSL settings.
7. The Redis and Memcached configurations will maintain the same memory allocation and security settings.
8. The PostgreSQL database will maintain the same user permissions and database name.