# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, configuration templates, and security hardening practices.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- Total: 5-6 weeks

**Complexity Assessment:** Medium
- Well-structured Chef cookbooks with clear separation of concerns
- Standard web server, caching, and application deployment patterns
- Security hardening configurations that need careful migration
- External cookbook dependencies that need Ansible equivalents

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and fail2ban/ufw configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, firewall configuration

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git-based deployment, Python virtual environment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file listing cookbook dependencies (nginx, memcached, redisio)
- `solo.json`: Chef configuration file with run list and node attributes
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Vagrant configuration for local development using Fedora 42
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or local development

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Ansible role
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or DavidWittman.redis

### Security Considerations

- **SSL/TLS Configuration**: 
  - Self-signed certificate generation needs to be migrated
  - Strong cipher configuration and security headers need to be preserved
  - Migration approach: Use Ansible's `openssl_*` modules for certificate management

- **Firewall Configuration**:
  - UFW configuration needs to be migrated
  - Migration approach: Use Ansible's `ufw` module

- **Fail2ban Configuration**:
  - Fail2ban setup needs to be migrated
  - Migration approach: Use Ansible's `template` module for fail2ban configuration

- **SSH Hardening**:
  - SSH configuration hardening (disable root login, password authentication)
  - Migration approach: Use Ansible's `lineinfile` module or `template` module for sshd_config

- **Vault/secrets management**:
  - Redis password in cache cookbook: `redis_secure_password_123`
  - PostgreSQL credentials in fastapi-tutorial cookbook: `fastapi:fastapi_password`
  - Migration approach: Use Ansible Vault for storing sensitive information

### Technical Challenges

- **Custom Resource Migration**: 
  - The `lineinfile` custom resource in nginx-multisite needs to be replaced with Ansible's native `lineinfile` module
  - Challenge: Ensuring identical behavior, especially with regex pattern matching

- **Template Conversion**:
  - Converting ERB templates to Jinja2 format
  - Challenge: Syntax differences between ERB and Jinja2, especially for conditionals and loops

- **Service Management**:
  - Chef's service resource needs to be replaced with Ansible's service module
  - Challenge: Ensuring proper service restart/reload notifications

- **Idempotency**:
  - Ensuring Ansible playbooks are as idempotent as the original Chef recipes
  - Challenge: Replicating Chef's idempotent behavior, especially for complex operations

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security configurations that should be established first

2. **cache** (Priority 2)
   - Depends on external cookbooks (memcached, redisio)
   - Moderate complexity with Redis authentication

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on web server and potentially caching
   - Contains database setup and application configuration

### Assumptions

1. The target environment will continue to be Fedora-based systems (specifically Fedora 42 as indicated in the Vagrantfile)
2. The same network topology and port configurations will be maintained
3. Self-signed certificates are acceptable for the migrated environment (production would likely use Let's Encrypt or other CA)
4. The FastAPI application source will continue to be pulled from the same Git repository
5. The current security hardening practices are appropriate for the target environment
6. Redis and Memcached configurations (memory allocation, etc.) will remain the same
7. The PostgreSQL database schema and user permissions will remain unchanged
8. The directory structure for web content and application files will be preserved
9. SSL certificate paths will remain the same (/etc/ssl/certs and /etc/ssl/private)
10. The Vagrant development environment will be maintained but converted to use Ansible provisioner