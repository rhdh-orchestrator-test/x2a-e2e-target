# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with FastAPI application backend and caching services (Redis and Memcached). The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- External dependencies on community cookbooks need to be replaced with Ansible Galaxy roles
- Security configurations need careful migration to maintain hardening standards
- SSL certificate management requires special attention

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening (fail2ban, ufw), and SSL certificate management
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and ufw

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints.
- `solo.json`: Chef configuration file containing the run list and node attributes. Defines Nginx site configurations and security settings.
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings.
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef Solo.
- `Vagrantfile`: Vagrant configuration file for creating a development environment using Fedora 42.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be a local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or DavidWittman.redis

### Security Considerations

- **fail2ban configuration**: Migrate fail2ban jail configuration to Ansible templates
- **ufw firewall rules**: Use Ansible's `ufw` module to configure firewall rules
- **SSH hardening**: Ensure SSH configuration (disable root login, password authentication) is maintained
- **SSL certificate management**: Replace self-signed certificate generation with Ansible's `openssl_*` modules
- **Vault/secrets management**:
  - Redis password in cache cookbook: Move to Ansible Vault
  - PostgreSQL credentials in fastapi-tutorial cookbook: Move to Ansible Vault
  - Count: 2 sets of credentials detected

### Technical Challenges

- **Multi-site Nginx configuration**: Ensure the dynamic generation of virtual host configurations is preserved in Ansible
- **SSL certificate management**: Properly handle certificate generation and permissions
- **Service dependencies**: Maintain proper ordering of service installations and configurations
- **PostgreSQL user and database creation**: Ensure idempotent database operations

### Migration Order

1. **nginx-multisite** (Priority 1): Core infrastructure component that other services depend on
   - Create base Nginx role
   - Add virtual host configuration
   - Add SSL management
   - Add security hardening (fail2ban, ufw)

2. **cache** (Priority 2): Supporting services
   - Create Memcached role
   - Create Redis role with authentication

3. **fastapi-tutorial** (Priority 3): Application deployment
   - Create PostgreSQL role
   - Create Python application deployment role
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora-based systems (the Vagrantfile specifies Fedora 42)
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt)
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
4. The directory structure for web content (/opt/server/test, /opt/server/ci, /opt/server/status) should be preserved
5. The security hardening requirements (fail2ban, ufw, SSH settings) will remain the same
6. The PostgreSQL database configuration (user: fastapi, password: fastapi_password) can be maintained
7. Redis will continue to require password authentication