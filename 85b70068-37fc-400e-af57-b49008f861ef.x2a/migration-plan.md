# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- Total: 5-6 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- External dependencies on community cookbooks need to be replaced with Ansible Galaxy roles
- Security configurations and SSL certificate management require careful handling
- Hardcoded secrets need to be migrated to Ansible Vault

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificates
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall)

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

- `Berksfile`: Defines cookbook dependencies including external cookbooks from Chef Supermarket (nginx, memcached, redisio)
- `solo.json`: Contains node configuration including run list and attributes for Nginx sites and security settings
- `solo.rb`: Chef Solo configuration file defining cookbook paths and log settings
- `Vagrantfile`: Defines a Fedora 42 VM for local development with port forwarding and networking
- `vagrant-provision.sh`: Shell script to install Chef and run the cookbooks in the Vagrant environment

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or local development

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role from Galaxy or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role or direct package installation and configuration
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` role or direct package installation and configuration

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should:
  - Maintain the same certificate generation logic or improve it
  - Consider using Ansible's `openssl_*` modules for certificate management
  - Ensure proper permissions on private keys

- **Firewall Configuration**: The current implementation uses UFW. Migration should:
  - Use Ansible's `ufw` module or appropriate firewall module for the target OS
  - Maintain the same firewall rules (SSH, HTTP, HTTPS)

- **SSH Hardening**: The current implementation disables root login and password authentication. Migration should:
  - Use Ansible's `lineinfile` or templates to configure SSH
  - Maintain the same security settings

- **Fail2ban Configuration**: The current implementation installs and configures fail2ban. Migration should:
  - Use Ansible's `fail2ban` module or direct configuration
  - Maintain the same jail settings

- **Vault/secrets management**: 
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL user and password in fastapi-tutorial cookbook: "fastapi" / "fastapi_password"
  - Database connection string in .env file
  - These should be migrated to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The current implementation dynamically creates Nginx site configurations based on node attributes. Migration should:
  - Use Ansible's template module with loops to achieve the same dynamic configuration
  - Ensure proper reloading of Nginx when configurations change

- **Redis Configuration Hack**: The current implementation includes a Ruby block to modify Redis configuration. Migration should:
  - Use Ansible's template module to generate a clean Redis configuration
  - Avoid post-processing of configuration files

- **Service Management**: The current implementation manages multiple services (Nginx, Redis, Memcached, PostgreSQL, FastAPI). Migration should:
  - Use Ansible's service module consistently
  - Ensure proper service dependencies and ordering

- **Idempotence**: Ensure all Ansible tasks are idempotent, especially database creation and user setup tasks

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Includes security hardening that should be applied first

2. **cache** (Priority 2)
   - Dependent services that should be configured before the application
   - Moderate complexity due to external dependencies

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on the infrastructure being in place
   - Highest complexity due to database setup, environment configuration, and service management

### Assumptions

1. The target environment will continue to be Fedora or a similar Linux distribution
2. Self-signed certificates are acceptable for the migrated solution
3. The same security practices (fail2ban, ufw, SSH hardening) should be maintained
4. The FastAPI application source will continue to be pulled from the same Git repository
5. The current Redis and PostgreSQL passwords are for development only and will be replaced with secure passwords in production
6. The Vagrant setup is primarily for development/testing and may not need to be migrated if another testing approach is preferred