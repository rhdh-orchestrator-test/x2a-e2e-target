# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, configuration templates, and security settings.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 3-4 weeks
- Testing and Validation: 2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 7-8 weeks

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
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, fail2ban integration, UFW firewall rules

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4)
- `solo.json`: Defines the run list and configuration parameters for nginx sites and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Defines the development VM (Fedora 42) with networking and provisioning
- `vagrant-provision.sh`: Shell script for installing Chef and running the cookbooks

### Target Details

- **Operating System**: Fedora/RHEL-based (Fedora 42 specified in Vagrantfile)
- **Virtual Machine Technology**: Libvirt (specified in Vagrantfile)
- **Cloud Platform**: Not specified, appears to be targeting on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create custom Nginx role
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or DavidWittman.redis

### Security Considerations

- **SSL Certificate Management**: 
  - Chef cookbook generates self-signed certificates
  - Migration approach: Use Ansible `openssl_*` modules or community.crypto collection

- **Firewall Configuration**: 
  - Chef cookbook configures UFW with specific rules
  - Migration approach: Use Ansible `ufw` module or `firewalld` module depending on target OS

- **fail2ban Integration**: 
  - Chef cookbook installs and configures fail2ban
  - Migration approach: Create Ansible tasks using the `template` module for fail2ban configuration

- **Security Headers**: 
  - Nginx is configured with security headers (HSTS, CSP, X-Frame-Options)
  - Migration approach: Ensure these headers are preserved in Ansible templates

- **Vault/secrets management**: 
  - Redis password hardcoded in recipe: "redis_secure_password_123"
  - PostgreSQL credentials hardcoded in recipe: "fastapi" / "fastapi_password"
  - Migration approach: Move all credentials to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Chef cookbook dynamically creates site configurations based on node attributes
  - Migration approach: Use Ansible loops with templates to achieve the same functionality

- **SSL Certificate Generation**: 
  - Chef cookbook generates self-signed certificates with custom attributes
  - Migration approach: Use Ansible's `openssl_certificate` module with similar parameters

- **PostgreSQL User and Database Creation**: 
  - Chef cookbook uses shell commands for PostgreSQL configuration
  - Migration approach: Use Ansible's `postgresql_*` modules for idempotent database management

- **Python Application Deployment**: 
  - Chef cookbook manages Python virtual environment and dependencies
  - Migration approach: Use Ansible's `pip` module and `git` module for application deployment

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security configurations that should be established first

2. **cache** (Priority 2)
   - Supporting service with external dependencies (Redis, Memcached)
   - Moderate complexity with authentication requirements

3. **fastapi-tutorial** (Priority 3)
   - Application layer that depends on both web server and database
   - Most complex with database, application code, and service management

### Assumptions

1. The target environment will continue to be Fedora/RHEL-based systems
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt)
3. The same security policies (fail2ban, ufw, SSH hardening) should be maintained
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current hardcoded credentials will be replaced with more secure practices using Ansible Vault
6. The same virtual host names (test.cluster.local, ci.cluster.local, status.cluster.local) will be maintained
7. The Vagrant development environment will be replaced with an equivalent Ansible-based setup