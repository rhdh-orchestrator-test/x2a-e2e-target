# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- **Total**: 5-6 weeks

**Complexity Assessment**: Medium
- The repository has a clear structure with well-defined cookbooks
- External dependencies on community cookbooks need to be replaced with Ansible Galaxy roles
- Security configurations and SSL certificate management require careful handling
- Secrets management needs to be improved during migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), sysctl security settings

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, dependency on community cookbooks

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints.
- `solo.json`: Chef Solo configuration file containing the run list and node attributes for Nginx sites and security settings.
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and logging settings.
- `Vagrantfile`: Defines the development VM using Fedora 42, with port forwarding and resource allocation.
- `vagrant-provision.sh`: Shell script to install Chef and Berkshelf, and run the Chef provisioning process in the Vagrant VM.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting local development with Vagrant

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy nginx role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible Galaxy memcached role or direct package installation and configuration
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy redis role or direct package installation and configuration

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW. Ansible should use the `ufw` module to manage firewall rules.
- **fail2ban Setup**: The Chef cookbook configures fail2ban. Ansible should use templates to configure fail2ban jails.
- **SSH Hardening**: The Chef cookbook disables root login and password authentication. Ansible should use the `lineinfile` module to modify SSH configuration.
- **SSL Certificate Management**: The Chef cookbook generates self-signed certificates. Ansible should use the `openssl_certificate` module for certificate generation.
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - No centralized secrets management is currently implemented

### Technical Challenges

- **Multi-site Nginx Configuration**: The Chef cookbook dynamically creates Nginx site configurations based on node attributes. Ansible will need to use templates and loops to achieve the same functionality.
- **SSL Certificate Generation**: The Chef cookbook generates self-signed certificates for each site. Ansible will need to use the `openssl_certificate` module to generate certificates.
- **Redis Configuration Hack**: The Chef cookbook includes a Ruby block to modify Redis configuration files. Ansible will need to use the `lineinfile` or `replace` module to achieve the same functionality.
- **PostgreSQL User and Database Creation**: The Chef cookbook uses shell commands to create PostgreSQL users and databases. Ansible should use the `postgresql_user` and `postgresql_db` modules instead.

### Migration Order

1. **nginx-multisite** (Priority 1): This is the foundation for the web server and should be migrated first.
   - Create Ansible role for Nginx installation and configuration
   - Create Ansible role for security hardening (fail2ban, ufw, sysctl)
   - Create Ansible role for SSL certificate generation
   - Create templates for Nginx site configurations

2. **cache** (Priority 2): This provides caching services for the web applications.
   - Create Ansible role for Memcached installation and configuration
   - Create Ansible role for Redis installation and configuration
   - Implement proper secrets management for Redis password

3. **fastapi-tutorial** (Priority 3): This deploys the application that depends on the web server and database.
   - Create Ansible role for Python environment setup
   - Create Ansible role for PostgreSQL installation and configuration
   - Create Ansible role for FastAPI application deployment
   - Implement proper secrets management for database credentials

### Assumptions

1. The target environment will continue to be Fedora 42, as specified in the Vagrantfile.
2. Self-signed certificates are acceptable for development, but production environments may require proper certificates.
3. The current hardcoded passwords in the Chef cookbooks are not suitable for production and will need to be replaced with a proper secrets management solution.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The current security hardening measures (fail2ban, ufw, SSH configuration) are sufficient for the target environment.
6. The Nginx sites configuration in solo.json overrides the default attributes in the cookbook.
7. The Redis configuration hack is necessary due to compatibility issues with the redisio cookbook.
8. The PostgreSQL database is only used by the FastAPI application and does not require additional configuration.