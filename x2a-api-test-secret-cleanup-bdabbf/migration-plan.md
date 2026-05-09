# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity:** Medium
- The repository has a clear structure with well-defined cookbooks
- No custom resources or complex Chef-specific features are used
- Security configurations need careful attention during migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, fail2ban integration, UFW firewall setup

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external cookbook dependencies
- `solo.json`: Chef Solo configuration file containing the run list and node attributes
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `Vagrantfile`: Vagrant configuration for local development using Fedora 42
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or create a custom role
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy or create a custom role
- **redisio (~> 7.2.4)**: Replace with Ansible redis role from Galaxy or create a custom role

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration should maintain proper file permissions (640 for private keys)
  - Consider integrating with Ansible Vault for certificate storage

- **Firewall Configuration**: 
  - UFW firewall is configured with specific rules
  - Migrate to equivalent Ansible UFW module or firewalld for Fedora

- **SSH Hardening**:
  - Root login disabled
  - Password authentication disabled
  - Maintain these security practices in Ansible

- **Fail2ban Integration**:
  - Configured for brute force protection
  - Use Ansible to manage fail2ban configuration

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL password is hardcoded in the recipe (`fastapi_password`)
  - These should be moved to Ansible Vault during migration

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - The Chef cookbook dynamically creates multiple virtual hosts
  - Ansible implementation will need to maintain this flexibility using templates and variables

- **SSL Certificate Generation**:
  - Self-signed certificates are generated using OpenSSL commands
  - Ansible has modules for this, but careful testing is needed

- **PostgreSQL User and Database Creation**:
  - Currently using raw SQL commands via sudo
  - Should be replaced with Ansible PostgreSQL modules

- **Redis Configuration Hack**:
  - The Chef recipe includes a ruby_block to modify Redis configuration
  - This will need special attention to implement properly in Ansible

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that others depend on
   - Start with basic Nginx installation and configuration
   - Add SSL and security features
   - Implement multi-site configuration

2. **cache** (Priority 2)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Address the Redis configuration hack

3. **fastapi-tutorial** (Priority 3)
   - Set up PostgreSQL
   - Deploy the FastAPI application
   - Configure the systemd service

### Assumptions

1. The target environment will continue to be Fedora-based systems (specifically Fedora 42 as indicated in the Vagrantfile)
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or other CA)
3. The same security practices (fail2ban, UFW, SSH hardening) should be maintained
4. The FastAPI application source code will continue to be pulled from the same Git repository
5. The current directory structure in the target system (/opt/server/*, /etc/ssl/*) should be preserved
6. The PostgreSQL database name, user, and credentials should remain the same
7. Redis will continue to require password authentication
8. The Vagrant development environment should be maintained but converted to use Ansible provisioner