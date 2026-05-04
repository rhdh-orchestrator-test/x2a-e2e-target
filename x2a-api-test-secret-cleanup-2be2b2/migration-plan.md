# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application with PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- External dependencies on community cookbooks will need Ansible equivalents
- Security configurations and SSL certificate management require careful handling

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, dependency on community cookbooks

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef configuration with run list and node attributes
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Provisioning script for Vagrant environment
- `Vagrantfile`: Defines the development VM using Fedora 42

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create custom Nginx role
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or DavidWittman.redis

### Security Considerations

- **SSL Certificate Management**: 
  - Current implementation generates self-signed certificates
  - Migration approach: Use Ansible's `openssl_*` modules for certificate generation
  - Consider integrating with Let's Encrypt via `geerlingguy.certbot` role

- **Firewall Configuration**: 
  - Current implementation uses UFW
  - Migration approach: Use Ansible's `ufw` module or `firewalld` module (more appropriate for Fedora)

- **SSH Hardening**:
  - Current implementation disables root login and password authentication
  - Migration approach: Use Ansible's `lineinfile` module or `geerlingguy.security` role

- **Fail2ban Configuration**:
  - Current implementation installs and configures fail2ban
  - Migration approach: Use Ansible's package and template modules or `geerlingguy.security` role

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe
  - PostgreSQL credentials are hardcoded in the recipe
  - Migration approach: Use Ansible Vault for storing sensitive information

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Preserving the dynamic site configuration capability
  - Mitigation: Use Ansible's template module with Jinja2 templates to generate site configurations based on variables

- **SSL Certificate Generation**:
  - Challenge: Ensuring proper permissions and security for SSL certificates
  - Mitigation: Use Ansible's `openssl_*` modules with appropriate file permissions

- **PostgreSQL User and Database Creation**:
  - Challenge: Converting the inline SQL commands to idempotent Ansible tasks
  - Mitigation: Use Ansible's `postgresql_*` modules which ensure idempotency

- **Redis Configuration Workaround**:
  - Challenge: The Chef recipe includes a hack to fix Redis configuration
  - Mitigation: Create proper Redis configuration template in Ansible without requiring post-configuration fixes

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Add security hardening features
   - Add multi-site configuration

2. **cache** (Priority 2)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper integration with Nginx

3. **fastapi-tutorial** (Priority 3)
   - Set up PostgreSQL database
   - Deploy Python application with virtual environment
   - Configure systemd service
   - Integrate with Nginx and caching services

### Assumptions

1. The target environment will continue to be Fedora-based systems
2. Self-signed certificates are acceptable for development (production would likely use Let's Encrypt or other CA)
3. The current security configurations (fail2ban, UFW, SSH hardening) are appropriate for the target environment
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current Redis and Memcached configurations are sufficient for the application's needs
6. The PostgreSQL database schema is managed by the application itself (no explicit schema management in the Chef code)
7. No CI/CD pipeline integration is required as part of the migration
8. The Vagrant development environment will be preserved or replaced with an equivalent