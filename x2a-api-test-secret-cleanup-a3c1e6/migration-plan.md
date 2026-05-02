# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks, handling external dependencies, and ensuring proper security configurations are maintained.

**Scope**: 3 Chef cookbooks with dependencies on external cookbooks
**Complexity**: Medium (standard web server patterns, caching services, and application deployment)
**Estimated Timeline**: 3-4 weeks (1 week per cookbook, plus testing and documentation)

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, fail2ban integration, UFW firewall rules

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

- `Berksfile`: Dependency management file listing cookbook dependencies (nginx, memcached, redisio)
- `solo.json`: Chef configuration file with run list and node attributes
- `solo.rb`: Chef configuration file for Chef Solo
- `Vagrantfile`: Defines a Fedora 42 VM for local development and testing
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or local development

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks

### Security Considerations

- **SSL/TLS Configuration**: 
  - Self-signed certificate generation needs to be replicated
  - Secure TLS protocols and ciphers must be maintained
  - Migration approach: Use Ansible's openssl_* modules or community.crypto collection

- **Firewall Configuration**: 
  - UFW rules for SSH, HTTP, HTTPS
  - Migration approach: Use Ansible's community.general.ufw module

- **fail2ban Integration**:
  - Custom jail configuration
  - Migration approach: Use Ansible's community.general.fail2ban module

- **System Hardening**:
  - SSH hardening (disable root login, password authentication)
  - Sysctl security parameters
  - Migration approach: Use Ansible's security modules or dedicated hardening role

- **Vault/secrets management**:
  - Redis password in plaintext in recipe (redis_secure_password_123)
  - PostgreSQL password in plaintext in recipe (fastapi_password)
  - Migration approach: Use Ansible Vault for all credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation dynamically generates site configurations based on node attributes
  - Mitigation: Use Ansible templates with loops over site definitions in variables

- **SSL Certificate Management**: 
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's openssl_* modules with proper idempotency checks

- **Service Orchestration**: 
  - Description: Services have dependencies (FastAPI depends on PostgreSQL)
  - Mitigation: Use Ansible handlers and meta dependencies to ensure proper ordering

- **Database Initialization**: 
  - Description: PostgreSQL user and database creation with idempotency
  - Mitigation: Use Ansible's postgresql_* modules with proper state checking

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Foundation for web services
   - Security configurations needed by other components
   - Relatively self-contained

2. **cache** (Priority 2)
   - Depends on external cookbooks
   - Moderate complexity with Redis configuration fixes

3. **fastapi-tutorial** (Priority 3)
   - Depends on PostgreSQL and web server
   - Most complex with application deployment, database setup, and service configuration

### Assumptions

1. The target environment will continue to be Fedora-based systems (specifically Fedora 42 as indicated in the Vagrantfile)
2. The same security requirements will apply in the new Ansible implementation
3. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or other CA)
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current Redis and Memcached configurations are sufficient for the application needs
6. The current directory structure in `/opt/server/` for website content and `/opt/fastapi-tutorial` for the application will be maintained
7. The PostgreSQL database schema is managed by the FastAPI application and not by the infrastructure code
8. The current security settings (fail2ban, UFW, SSH hardening) are appropriate for the target environment