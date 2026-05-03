# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- Total: 5-6 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- No complex custom resources or libraries
- External dependencies are clearly defined in Berksfile
- Security configurations are present and need careful migration

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
    - Key Features: Git repository deployment, Python virtual environment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4)
- `Vagrantfile`: Defines development VM using Fedora 42 with libvirt provider, port forwarding, and provisioning
- `solo.json`: Defines Chef run list and node attributes including nginx site configurations and security settings
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Shell script to install Chef and run the cookbooks in the Vagrant environment

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Ansible role
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or `DavidWittman.redis`

### Security Considerations

- **SSL Certificate Management**: 
  - Chef cookbook generates self-signed certificates
  - Migration approach: Use Ansible's `openssl_*` modules or `community.crypto` collection

- **Firewall Configuration (UFW)**:
  - Chef cookbook configures UFW with specific rules
  - Migration approach: Use Ansible's `ufw` module to configure identical rules

- **Fail2Ban Configuration**:
  - Chef cookbook installs and configures fail2ban
  - Migration approach: Use Ansible's `template` module to create fail2ban configuration files

- **System Hardening**:
  - Chef cookbook applies sysctl security settings
  - Migration approach: Use Ansible's `sysctl` module to apply the same settings

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe as 'redis_secure_password_123'
  - PostgreSQL password is hardcoded in the recipe as 'fastapi_password'
  - Migration approach: Use Ansible Vault to securely store these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**:
  - Challenge: Replicating the dynamic site configuration from Chef to Ansible
  - Mitigation: Create Ansible templates that iterate through site configurations defined in variables

- **SSL Certificate Generation**:
  - Challenge: Ensuring proper permissions and ownership of SSL certificates and keys
  - Mitigation: Use Ansible's file and openssl modules with appropriate permissions

- **Service Dependencies**:
  - Challenge: Ensuring proper service startup order (PostgreSQL before FastAPI)
  - Mitigation: Use Ansible handlers and meta dependencies between roles

- **Idempotency**:
  - Challenge: Ensuring database creation commands are idempotent
  - Mitigation: Use Ansible's PostgreSQL modules instead of raw SQL commands

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation
   - Add SSL certificate generation
   - Add virtual host configuration
   - Add security hardening (fail2ban, ufw, headers)

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Implement PostgreSQL installation and configuration
   - Implement Python environment setup
   - Implement application deployment
   - Implement systemd service configuration

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions.
2. Self-signed SSL certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or other CA).
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
4. The current security settings (fail2ban, ufw, SSH hardening) are appropriate for the target environment.
5. The Redis and PostgreSQL passwords in the current code are development passwords and will be replaced with secure passwords in production.
6. The current Nginx site configurations (test.cluster.local, ci.cluster.local, status.cluster.local) will remain the same in the migrated solution.