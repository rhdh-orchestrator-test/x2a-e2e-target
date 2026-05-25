# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- No complex custom resources or libraries
- Standard infrastructure components (web server, caching, application deployment)
- Security configurations that need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and SSL certificate management
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup with self-signed certificates, security hardening (fail2ban, ufw, sysctl), virtual host management

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef Solo configuration file with run list and node attributes
- `solo.rb`: Chef Solo configuration file with file paths and log settings
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration file for local development environment using Fedora 42

### Target Details

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ based on cookbook metadata
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or direct package installation
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package configuration
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package configuration

### Security Considerations

- **SSL/TLS Configuration**: 
  - Self-signed certificate generation needs to be migrated
  - SSL certificate and private key paths need to be maintained
  - Strong cipher configuration should be preserved

- **Firewall Configuration**: 
  - UFW rules need to be migrated to equivalent Ansible UFW module tasks
  - Default deny policy with specific allow rules for SSH, HTTP, HTTPS

- **Fail2ban Setup**:
  - Configuration needs to be migrated to Ansible tasks
  - Jail configuration template needs to be preserved

- **SSH Hardening**:
  - Root login disable option
  - Password authentication disable option

- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL user/password in fastapi-tutorial cookbook: "fastapi"/"fastapi_password"
  - No Chef Vault or encrypted data bags detected, but plain text credentials should be moved to Ansible Vault

### Technical Challenges

- **Multi-site Configuration**: 
  - The dynamic generation of Nginx site configurations based on node attributes needs to be carefully migrated to Ansible's template system
  - Ensure the same level of flexibility for adding new sites

- **SSL Certificate Management**: 
  - Self-signed certificate generation logic needs to be preserved
  - Proper permissions and ownership for private keys

- **Service Dependencies**: 
  - Ensure proper ordering of service installations and configurations
  - Maintain notification system for service restarts when configurations change

- **PostgreSQL User/Database Creation**:
  - The idempotent database and user creation commands need to be migrated to Ansible's PostgreSQL modules

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security configurations that should be established first

2. **cache** (Priority 2)
   - Supporting services that the application may depend on
   - Relatively simple configuration with external dependencies

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on the infrastructure being in place
   - More complex with database setup, git deployment, and service configuration

### Assumptions

1. The target environment will continue to be Fedora-based systems, with potential support for Ubuntu and CentOS as indicated in the cookbook metadata.
2. The same network configuration and port mappings will be maintained.
3. Self-signed certificates are acceptable for the migrated environment (production would likely use proper certificates).
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The current security configurations are appropriate for the target environment.
6. No custom Chef libraries or resources are in use beyond what's visible in the examined files.
7. The Redis and Memcached configurations don't have specific tuning requirements beyond what's visible in the recipes.
8. The PostgreSQL database schema is managed by the FastAPI application itself, not by Chef.