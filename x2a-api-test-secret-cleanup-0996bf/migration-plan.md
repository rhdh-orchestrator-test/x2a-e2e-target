# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their recipes, templates, attributes, and resources to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- Well-structured Chef cookbooks with clear separation of concerns
- Standard infrastructure components (Nginx, Redis, Memcached, PostgreSQL)
- Some security configurations that need careful migration
- Hardcoded credentials that should be moved to Ansible Vault

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and firewall rules
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), custom Nginx configurations

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4)
- `Vagrantfile`: Defines a Fedora 42 VM with port forwarding (80->8080, 443->8443) and provisioning via Chef
- `solo.json`: Contains the run list and configuration data for nginx sites and security settings
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Shell script to install Chef and run the cookbooks in the Vagrant environment

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified (appears to be a local development environment)

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (community.general.nginx or custom role)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role (geerlingguy.redis)

### Security Considerations

- **SSL Certificate Management**: 
  - Current approach uses self-signed certificates generated with OpenSSL
  - Migration approach: Use Ansible's openssl_* modules or community.crypto collection

- **Firewall Configuration**: 
  - Current approach uses ufw with specific allow rules
  - Migration approach: Use Ansible's ufw module or firewalld module depending on target OS

- **fail2ban Configuration**: 
  - Current approach installs and configures fail2ban
  - Migration approach: Use Ansible's template module to configure fail2ban

- **SSH Hardening**: 
  - Current approach disables root login and password authentication
  - Migration approach: Use Ansible's lineinfile module or template module for sshd_config

- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook ('redis_secure_password_123')
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook ('fastapi_password')
  - Migration approach: Move all credentials to Ansible Vault

### Technical Challenges

- **Custom Resource Migration**: 
  - The nginx-multisite cookbook includes a custom 'lineinfile' resource
  - Migration approach: Replace with Ansible's native lineinfile module

- **Template Conversion**: 
  - Multiple ERB templates need conversion to Jinja2 format
  - Migration approach: Convert ERB syntax to Jinja2, paying special attention to conditional logic

- **Service Management**: 
  - Chef manages services with notifications for reloads/restarts
  - Migration approach: Use Ansible handlers for service notifications

- **File Ownership and Permissions**: 
  - Chef sets specific ownership and permissions for files and directories
  - Migration approach: Use Ansible's file module with equivalent attributes

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security configurations that should be established first

2. **cache** (Priority 2)
   - Depends on external cookbooks (memcached, redisio)
   - Moderate complexity with Redis authentication

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on PostgreSQL
   - Contains database setup and application configuration

### Assumptions

1. The target environment will continue to be Fedora-based systems (the current Vagrantfile specifies Fedora 42)
2. Self-signed certificates are acceptable for the migrated solution (production would likely require proper certificates)
3. The same directory structure for web content will be maintained (/opt/server/*)
4. The same security policies (fail2ban, ufw, SSH hardening) will be maintained
5. The FastAPI application source will continue to be pulled from the same Git repository
6. The PostgreSQL database structure and user permissions will remain the same
7. The Redis and Memcached configurations will maintain the same performance characteristics
8. The Nginx site configurations will maintain the same security headers and SSL settings