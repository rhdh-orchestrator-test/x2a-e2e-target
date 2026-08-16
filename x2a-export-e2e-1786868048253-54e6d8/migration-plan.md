# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their recipes, templates, and files to equivalent Ansible roles and playbooks.

**Scope**: 3 Chef cookbooks with 7 recipes, multiple templates, and static files
**Complexity**: Medium - Standard web infrastructure with common patterns
**Timeline Estimate**: 2-3 weeks for complete migration, testing, and documentation

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), sysctl security settings

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4)
- `solo.json`: Contains node attributes and run list for Chef Solo, including Nginx site configurations and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Defines a Fedora 42 VM with port forwarding and networking for development
- `vagrant-provision.sh`: Shell script to install Chef and run the cookbooks in the Vagrant environment

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in the Vagrant development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible community.nginx collection or geerlingguy.nginx role
- **memcached (~> 6.0)**: Replace with geerlingguy.memcached role
- **redisio (~> 7.2.4)**: Replace with geerlingguy.redis role or community.redis collection
- **PostgreSQL**: Replace with community.postgresql collection or geerlingguy.postgresql role
- **Python/venv**: Use Ansible's built-in pip and package modules

### Security Considerations

- **SSL Certificate Management**: 
  - Migration approach: Use Ansible's openssl_* modules for self-signed certificates or community.crypto collection
  - Consider integrating with Ansible Vault for certificate storage

- **Firewall Configuration (UFW)**:
  - Migration approach: Use Ansible's ufw module to configure firewall rules

- **fail2ban Configuration**:
  - Migration approach: Use community.general.fail2ban module or custom templates

- **SSH Hardening**:
  - Migration approach: Use Ansible's lineinfile module or dedicated ssh hardening role

- **Vault/secrets management**:
  - Redis password: Currently hardcoded as 'redis_secure_password_123' in the cache cookbook
  - PostgreSQL credentials: Currently hardcoded as 'fastapi:fastapi_password' in the fastapi-tutorial cookbook
  - SSL private keys: Generated and stored in /etc/ssl/private
  - Total credentials detected: 3 sets of credentials that need to be secured with Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation uses Chef templates to generate multiple virtual host configurations
  - Mitigation strategy: Create Ansible templates with similar logic, using with_items to iterate through site configurations

- **SSL Certificate Generation**:
  - Description: Custom SSL certificate generation for each virtual host
  - Mitigation strategy: Use Ansible's openssl_* modules with appropriate idempotency checks

- **Redis Configuration Patching**:
  - Description: The Chef cookbook uses a ruby_block to modify Redis configuration files after they're created
  - Mitigation strategy: Create a custom Redis configuration template in Ansible rather than modifying files after creation

- **FastAPI Application Deployment**:
  - Description: Complex deployment process involving Git, Python virtual environment, and systemd service
  - Mitigation strategy: Break into discrete Ansible tasks with appropriate handlers and idempotency checks

### Migration Order

1. **cache** (Priority 1 - low risk, foundational service)
   - Simple configuration with well-defined external dependencies
   - Minimal custom logic

2. **nginx-multisite** (Priority 2 - moderate complexity)
   - Core infrastructure component with security implications
   - Multiple templates and configuration files to convert

3. **fastapi-tutorial** (Priority 3 - application layer)
   - Depends on database and potentially cache services
   - More complex deployment process with multiple steps

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based distributions
2. The Vagrant development environment will be maintained for testing
3. Self-signed certificates are acceptable for the migrated solution (no Let's Encrypt integration required)
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current security configurations (fail2ban, ufw, sysctl) are appropriate for the target environment
6. No CI/CD pipeline integration is required for the initial migration
7. The current Redis and PostgreSQL passwords are development-only and will be replaced with secure values in production
8. No high availability or clustering requirements exist for the services