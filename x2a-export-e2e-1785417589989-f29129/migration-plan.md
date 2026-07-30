# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The Chef cookbooks are well-structured and follow standard patterns
- No custom resources or complex Chef-specific features are used
- Security configurations need careful attention during migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and SSL certificate management
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (nginx, memcached, redisio) - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Contains node attributes and run list - will be replaced by Ansible inventory variables
- `solo.rb`: Chef Solo configuration - not needed in Ansible
- `vagrant-provision.sh`: Provisioning script for Vagrant - will need adaptation for Ansible
- `Vagrantfile`: VM configuration - will need updates to use Ansible provisioner instead of Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development/testing

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or custom role
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy or custom role
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role from Galaxy or custom role

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration should maintain the same level of security
  - Consider using Ansible's openssl_* modules

- **Firewall Configuration**: 
  - UFW firewall rules need to be migrated
  - Use Ansible's ufw module to maintain the same configuration

- **SSH Hardening**:
  - Root login disabled
  - Password authentication disabled
  - Use Ansible's lineinfile or template module to configure SSH

- **System Hardening**:
  - sysctl security settings
  - fail2ban configuration
  - Use Ansible's sysctl and template modules

- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL password in fastapi-tutorial cookbook: "fastapi_password"
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Configuration**: 
  - The nginx-multisite cookbook dynamically creates site configurations based on node attributes
  - Ansible will need to use loops with the template module to achieve the same functionality

- **SSL Certificate Generation**:
  - Chef uses execute resources to generate SSL certificates
  - Ansible should use the openssl_* modules for better idempotency

- **Service Dependencies**:
  - The FastAPI application depends on PostgreSQL
  - Ensure proper ordering of tasks in Ansible playbooks

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx configuration and site setup
   - Add SSL and security features

2. **cache** (Priority 2)
   - Relatively simple configuration
   - Depends on external roles (memcached, redis)

3. **fastapi-tutorial** (Priority 3)
   - Application deployment
   - Depends on PostgreSQL and potentially the Nginx configuration

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distribution
2. The same directory structure for web content will be maintained
3. Self-signed certificates are acceptable (not using Let's Encrypt or other CA)
4. The same security policies should be applied in the Ansible configuration
5. The Vagrant development environment will be maintained
6. No changes to the application code or database schema are required
7. The same hostnames and domain structure will be used