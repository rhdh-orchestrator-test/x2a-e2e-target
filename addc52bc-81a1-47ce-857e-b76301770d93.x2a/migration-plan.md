# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx configuration with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three primary Chef cookbooks to Ansible roles and playbooks, addressing external dependencies, and ensuring security configurations are properly maintained.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Core Infrastructure Migration: 2 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- Total: 5 weeks

**Complexity Assessment:** Medium
- Well-structured Chef cookbooks with clear dependencies
- Standard infrastructure components (Nginx, Redis, Memcached, PostgreSQL)
- Security configurations that need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks - will be replaced by Ansible Galaxy requirements.yml
- `Policyfile.rb`: Chef policy configuration - will be replaced by Ansible playbook structure
- `Vagrantfile`: VM configuration for development - can be adapted for Ansible testing
- `vagrant-provision.sh`: Chef provisioning script - will be replaced by Ansible provisioning
- `solo.json`: Chef node attributes - will be migrated to Ansible group_vars and host_vars
- `solo.rb`: Chef configuration - will be replaced by ansible.cfg

### Target Details

Based on the source configuration files:

- **Operating System**: Supports Ubuntu 18.04+ and CentOS 7+, with Fedora 42 used in Vagrant development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role (e.g., geerlingguy.redis)
- **ssl_certificate (~> 2.1)**: Replace with Ansible certificate management tasks

### Security Considerations

- **SSL Certificate Management**: Migration must maintain proper certificate generation and permissions
  - Current implementation uses self-signed certificates with proper permissions
  - Ansible equivalent will use the `openssl_*` modules

- **Firewall Configuration (UFW)**: Maintain security rules
  - Current implementation blocks all traffic except SSH, HTTP, and HTTPS
  - Ansible equivalent will use the `ufw` module

- **fail2ban Configuration**: Maintain intrusion prevention
  - Current implementation installs and configures fail2ban
  - Ansible equivalent will use templates for fail2ban configuration

- **SSH Hardening**: Maintain secure SSH configuration
  - Current implementation disables root login and password authentication
  - Ansible equivalent will use templates or lineinfile module for SSH configuration

- **Redis Authentication**: Maintain Redis password protection
  - Current implementation sets a Redis password
  - Ansible equivalent will use templates for Redis configuration

- **PostgreSQL Authentication**: Maintain database security
  - Current implementation creates a PostgreSQL user with password
  - Ansible equivalent will use the `postgresql_*` modules

### Technical Challenges

- **Multi-site Nginx Configuration**: The current Chef cookbook dynamically creates Nginx site configurations based on attributes
  - Solution: Use Ansible templates with loops over site definitions in variables

- **SSL Certificate Generation**: The current implementation generates self-signed certificates with proper permissions
  - Solution: Use Ansible's `openssl_*` modules with appropriate file permissions

- **Service Dependencies**: Ensuring services start in the correct order
  - Solution: Use Ansible handlers and proper task ordering with appropriate dependencies

- **Idempotency**: Ensuring Ansible playbooks are idempotent like the Chef recipes
  - Solution: Use Ansible's state modules and conditional checks

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that others depend on
   - Create Ansible role with templates for Nginx configuration
   - Implement SSL certificate generation
   - Implement security hardening (fail2ban, UFW)

2. **cache** (Priority 2)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper service management

3. **fastapi-tutorial** (Priority 3)
   - Implement PostgreSQL database setup
   - Implement Python application deployment
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Ubuntu 18.04+/CentOS 7+ as specified in the cookbook metadata
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt)
3. The Redis password "redis_secure_password_123" in the Chef recipe is a placeholder and should be replaced with a secure password management solution in Ansible
4. The PostgreSQL password "fastapi_password" is also a placeholder and should be secured
5. The current Chef implementation doesn't use encrypted data bags or other secret management, so we'll need to implement Ansible Vault for secrets
6. The Vagrant development environment will be maintained for testing the Ansible playbooks
7. The FastAPI application source will continue to be pulled from the same Git repository