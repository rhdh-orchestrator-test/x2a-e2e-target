# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

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
- Multiple services need to be coordinated (Nginx, Redis, Memcached, PostgreSQL, FastAPI)

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4). These will need to be replaced with Ansible Galaxy roles or custom Ansible roles.
- `solo.json`: Contains the run list and configuration data for the Chef run, including Nginx site configurations and security settings. This will be converted to Ansible variables.
- `solo.rb`: Chef configuration file that sets paths and log levels. Will be replaced by Ansible configuration.
- `Vagrantfile`: Defines the development VM using Fedora 42. Can be adapted for Ansible testing with minimal changes.
- `vagrant-provision.sh`: Shell script that installs Chef and runs the cookbooks. Will be replaced with Ansible provisioning.

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ as indicated in cookbook metadata
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with `ansible.builtin.package` for installation and Ansible templates for configuration
- **memcached (~> 6.0)**: Replace with `community.general.memcached` module or direct package installation and configuration
- **redisio (~> 7.2.4)**: Replace with `community.general.redis` module or direct package installation and configuration

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migrate to Ansible's `community.crypto.openssl_*` modules for certificate management.
- **Firewall Configuration**: Replace UFW configuration with Ansible's `ansible.posix.firewalld` or `community.general.ufw` modules.
- **fail2ban Configuration**: Use Ansible templates to configure fail2ban similar to the Chef implementation.
- **SSH Hardening**: Migrate SSH security configurations using Ansible's `ansible.builtin.lineinfile` or templates.
- **Vault/secrets management**:
  - Redis password in `cookbooks/cache/recipes/default.rb` (hardcoded as 'redis_secure_password_123')
  - PostgreSQL credentials in `cookbooks/fastapi-tutorial/recipes/default.rb` (hardcoded as 'fastapi_password')
  - These should be moved to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple virtual hosts based on node attributes will need to be replicated using Ansible loops and templates.
- **SSL Certificate Generation**: The self-signed certificate generation logic needs to be carefully migrated to ensure proper permissions and ownership.
- **Service Coordination**: The interdependencies between services (e.g., FastAPI depending on PostgreSQL) need to be maintained in the Ansible playbook ordering.
- **Python Environment Management**: The Python virtual environment setup for FastAPI will need to be handled with Ansible's `ansible.builtin.pip` module.

### Migration Order

1. **nginx-multisite** (Priority 1): Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add SSL certificate management
   - Implement security hardening (fail2ban, UFW)
   - Configure virtual hosts

2. **cache** (Priority 2): Supporting services
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (Priority 3): Application layer
   - Set up PostgreSQL database
   - Deploy FastAPI application
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora 42 or similar Linux distributions.
2. Self-signed certificates are acceptable for development; production would likely use different certificate sources.
3. The current security configurations are appropriate for the target environment.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The Redis configuration hack in the cache cookbook may not be necessary with newer Redis versions.
6. The hardcoded credentials in the recipes are for development only and would be replaced with secure values in production.