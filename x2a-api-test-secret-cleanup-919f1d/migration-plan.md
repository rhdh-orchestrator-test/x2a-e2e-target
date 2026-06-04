# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application with PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- Well-structured Chef cookbooks with clear separation of concerns
- Standard web server, caching, and application configurations
- Security hardening requirements that need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site SSL configuration, security hardening (fail2ban, UFW firewall), custom Nginx configurations

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

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4)
- `solo.json`: Defines the Chef run list and configuration attributes for Nginx sites and security settings
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `Vagrantfile`: Defines a Fedora 42 VM with port forwarding for development and testing
- `vagrant-provision.sh`: Shell script to install Chef and run the cookbooks in the Vagrant environment

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or local development

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or DavidWittman.redis

### Security Considerations

- **SSL/TLS Configuration**: 
  - Migration approach: Use Ansible's `openssl_*` modules to generate self-signed certificates
  - Ensure proper file permissions are maintained for private keys

- **Firewall (UFW)**:
  - Migration approach: Use Ansible's `ufw` module to configure firewall rules
  - Ensure SSH access is maintained during migration to prevent lockouts

- **fail2ban**:
  - Migration approach: Create an Ansible role for fail2ban configuration
  - Migrate jail.local template to Ansible template

- **SSH Hardening**:
  - Migration approach: Use Ansible's `lineinfile` module or templates to configure SSH daemon
  - Ensure root login and password authentication settings are properly migrated

- **Vault/secrets management**:
  - Redis password: Currently hardcoded in the cache cookbook as 'redis_secure_password_123'
  - PostgreSQL credentials: Hardcoded in the fastapi-tutorial cookbook as user 'fastapi' with password 'fastapi_password'
  - Migration approach: Move all credentials to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation uses Chef attributes and templates to generate multiple virtual host configurations
  - Mitigation strategy: Create an Ansible role with templates that can iterate through site configurations defined in variables

- **Service Dependencies**:
  - Description: The FastAPI application depends on PostgreSQL being configured first
  - Mitigation strategy: Use Ansible handlers and proper task ordering to ensure dependencies are met

- **SSL Certificate Generation**:
  - Description: Self-signed certificates are generated for each site
  - Mitigation strategy: Use Ansible's `openssl_certificate` module with proper idempotency checks

- **Systemd Service Management**:
  - Description: The FastAPI application is deployed as a systemd service
  - Mitigation strategy: Use Ansible's `systemd` module and templates for service files

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Add virtual host configuration
   - Add security hardening (fail2ban, UFW)

2. **cache** (low complexity, independent service)
   - Configure Memcached
   - Configure Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Configure PostgreSQL
   - Deploy FastAPI application
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora-based systems (specifically Fedora 42 as specified in the Vagrantfile)
2. The same directory structure for web content will be maintained (/opt/server/*)
3. Self-signed certificates are acceptable for the migrated solution
4. The same security hardening requirements will apply (fail2ban, UFW, SSH hardening)
5. The FastAPI application source will continue to be pulled from the same Git repository
6. The PostgreSQL database schema does not need to be migrated, only the database and user creation
7. The Redis and Memcached configurations do not have custom tuning beyond what's visible in the cookbooks
8. No external monitoring or logging systems need to be integrated
9. The Vagrant development environment should be preserved for testing the Ansible playbooks