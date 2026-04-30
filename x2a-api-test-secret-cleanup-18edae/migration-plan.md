# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, configuration templates, and security settings.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- Well-structured Chef cookbooks with clear separation of concerns
- Standard infrastructure components (Nginx, Redis, Memcached, PostgreSQL)
- Security configurations that need careful migration
- Hardcoded credentials that should be moved to Ansible Vault

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and fail2ban/ufw configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, fail2ban integration, UFW firewall configuration

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4)
- `Vagrantfile`: Defines development environment using Fedora 42, with port forwarding and networking configuration
- `solo.json`: Chef run list and node attributes including nginx site configurations and security settings
- `solo.rb`: Chef Solo configuration
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora (based on Vagrantfile specifying "generic/fedora42")
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or DavidWittman.redis

### Security Considerations

- **SSL Certificate Management**: 
  - Chef cookbook generates self-signed certificates
  - Migration approach: Use Ansible's `openssl_*` modules or community.crypto collection

- **Firewall Configuration**: 
  - Chef cookbook configures UFW with specific rules
  - Migration approach: Use Ansible's `ufw` module to replicate rules

- **fail2ban Integration**: 
  - Chef cookbook installs and configures fail2ban
  - Migration approach: Create an Ansible role for fail2ban configuration

- **Vault/secrets management**:
  - Redis password hardcoded in Chef recipe: `redis_secure_password_123`
  - PostgreSQL credentials hardcoded in FastAPI recipe: `fastapi:fastapi_password`
  - Environment variables in .env file for FastAPI
  - Migration approach: Move all credentials to Ansible Vault

- **Security Headers**:
  - Nginx configured with security headers (HSTS, X-Frame-Options, CSP)
  - Migration approach: Ensure Ansible templates include the same headers

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Chef cookbook dynamically creates site configurations from node attributes
  - Migration approach: Use Ansible loops with templates to create site configurations

- **SSL Certificate Generation**:
  - Chef cookbook generates self-signed certificates for each site
  - Migration approach: Use Ansible's `openssl_certificate` module with proper idempotence checks

- **PostgreSQL Database Setup**:
  - Chef cookbook uses shell commands to create database and user
  - Migration approach: Use Ansible's `postgresql_*` modules for better idempotence

- **Redis Configuration Patching**:
  - Chef cookbook uses a ruby_block to modify Redis configuration
  - Migration approach: Create a proper template for Redis configuration

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Create Ansible role for Nginx installation and configuration
   - Create templates for site configurations
   - Implement SSL certificate generation
   - Configure security settings (fail2ban, ufw)

2. **cache** (low complexity, standalone service)
   - Create Ansible roles for Memcached and Redis
   - Configure Redis with proper authentication
   - Ensure proper service management

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Create Ansible role for PostgreSQL installation and configuration
   - Create role for FastAPI application deployment
   - Implement Python virtual environment setup
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora-based systems
2. Self-signed certificates are acceptable for the migrated solution
3. The same security hardening measures should be applied in the Ansible solution
4. The FastAPI application source will continue to be pulled from the same Git repository
5. The directory structure for web content and application files will remain the same
6. The current hardcoded credentials will be replaced with Ansible Vault variables
7. The Vagrant development environment will be maintained but converted to use Ansible provisioner