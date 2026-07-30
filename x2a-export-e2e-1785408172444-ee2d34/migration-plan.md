# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server setup with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- No custom resources or complex Chef-specific patterns
- Standard web and application server configurations
- Some security configurations that need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and SSL certificate management
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup, security hardening (fail2ban, ufw firewall)

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database setup
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment, Git repository deployment, PostgreSQL database, systemd service

- **cache**:
    - Description: Caching services configuration including Memcached and Redis
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Contains node attributes and run list - will be replaced by Ansible inventory variables
- `solo.rb`: Chef Solo configuration - will be replaced by Ansible configuration
- `Vagrantfile`: Development environment configuration - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisioning script for Vagrant - will be replaced by Ansible playbook calls

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) as specified in cookbook metadata, with Fedora 42 used in Vagrant development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider as specified in Vagrantfile
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible `nginx` role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible `geerlingguy.memcached` role or custom memcached role
- **redisio (~> 7.2.4)**: Replace with Ansible `geerlingguy.redis` role or custom Redis role

### Security Considerations

- **SSL/TLS Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration should maintain proper permissions (640) and ownership (root:ssl-cert)
  - Consider integrating with Ansible's `community.crypto` collection for certificate management

- **Firewall Configuration**: 
  - UFW firewall rules need to be migrated to equivalent Ansible UFW module tasks
  - Default deny policy with specific allows for SSH, HTTP, HTTPS

- **Fail2ban Integration**:
  - Custom jail configuration needs to be migrated to Ansible templates
  - Service management needs to be maintained

- **SSH Hardening**:
  - Root login disabled
  - Password authentication disabled
  - These configurations should be maintained in Ansible

- **System Hardening**:
  - Custom sysctl security settings need to be migrated
  - File permissions need to be maintained

- **Vault/secrets management**:
  - Hardcoded credentials found in cache cookbook (Redis password: 'redis_secure_password_123')
  - Hardcoded credentials in fastapi-tutorial cookbook (PostgreSQL user/password: 'fastapi'/'fastapi_password')
  - These should be migrated to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Maintaining the dynamic generation of site configurations based on variables
  - Mitigation: Use Ansible templates with loops over site definitions in variables

- **SSL Certificate Generation**:
  - Challenge: Ensuring certificates are only generated when needed
  - Mitigation: Use Ansible's `stat` module to check for existing certificates and `community.crypto` modules for generation

- **Service Orchestration**:
  - Challenge: Maintaining proper service restart/reload notifications when configurations change
  - Mitigation: Use Ansible handlers to manage service restarts

- **Database Initialization**:
  - Challenge: PostgreSQL database and user creation with idempotency
  - Mitigation: Use Ansible's PostgreSQL modules with proper conditionals

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Relatively self-contained with clear configuration templates

2. **cache** (Priority 2)
   - Supporting service with external dependencies
   - Moderate complexity with Redis configuration customization

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on other services
   - Involves database setup, application code deployment, and service configuration

### Assumptions

1. The target environment will continue to support the same operating systems (Ubuntu 18.04+ or CentOS 7+)
2. The same security requirements will apply in the new Ansible-managed environment
3. Self-signed certificates are acceptable for the migrated solution (no integration with Let's Encrypt or other CA)
4. The PostgreSQL and Redis passwords in the code are development/example passwords and will be replaced with proper secrets management
5. The Vagrant development environment will be maintained for testing the Ansible playbooks
6. No changes to the application code or deployment architecture are required
7. The same multi-site configuration pattern will be maintained
8. No high availability or clustering requirements exist beyond what's in the current code