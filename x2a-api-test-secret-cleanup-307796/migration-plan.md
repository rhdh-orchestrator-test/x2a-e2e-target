# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- External dependencies on community cookbooks need to be replaced with Ansible Galaxy roles
- Security configurations need careful migration
- Secrets management needs improvement in the Ansible implementation

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall)

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints. Will be replaced by Ansible Galaxy requirements.yml.
- `solo.json`: Chef run list and node attributes configuration. Will be replaced by Ansible inventory variables.
- `solo.rb`: Chef Solo configuration file. Will be replaced by Ansible configuration.
- `Vagrantfile`: Defines the development VM using Fedora 42. Can be adapted for Ansible testing with minimal changes.
- `vagrant-provision.sh`: Shell script to install Chef and run the cookbooks in the Vagrant environment. Will be replaced with Ansible provisioner in Vagrant.

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in the Vagrant development environment.
- **Virtual Machine Technology**: Vagrant with libvirt provider (based on Vagrantfile configuration).
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` module or community.general collection
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role for Memcached (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role for Redis (e.g., geerlingguy.redis)

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW. Migration should use Ansible's `ufw` module or `firewalld` module depending on the target OS.
- **fail2ban Setup**: The Chef cookbook configures fail2ban. Migration should use an Ansible role for fail2ban configuration.
- **SSH Hardening**: The Chef cookbook disables root login and password authentication. Migration should use Ansible's `lineinfile` module or a dedicated SSH hardening role.
- **SSL Certificate Management**: The Chef cookbook generates self-signed certificates. Migration should use Ansible's `openssl_*` modules or consider integration with Let's Encrypt.
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - No external vault integration is currently used
  - Recommendation: Use Ansible Vault for storing sensitive values

### Technical Challenges

- **Multi-site Nginx Configuration**: The Chef cookbook dynamically creates Nginx site configurations based on node attributes. The Ansible equivalent will need to use loops with templates.
- **SSL Certificate Generation**: The Chef cookbook generates self-signed certificates. The Ansible equivalent will need to use the `openssl_*` modules or consider integration with Let's Encrypt.
- **Redis Configuration Hack**: The Chef cookbook includes a Ruby block to modify Redis configuration files after they're created. The Ansible equivalent will need to use templates or the `lineinfile` module.
- **PostgreSQL User and Database Creation**: The Chef cookbook uses shell commands to create PostgreSQL users and databases. The Ansible equivalent should use the `postgresql_*` modules for better idempotence.

### Migration Order

1. **nginx-multisite** (Priority 1): Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Add security hardening (fail2ban, UFW)
   - Add multi-site configuration

2. **cache** (Priority 2): Supporting services
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper integration with Nginx

3. **fastapi-tutorial** (Priority 3): Application layer
   - Implement PostgreSQL database setup
   - Implement Python environment and application deployment
   - Configure systemd service
   - Ensure proper integration with Nginx and cache services

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based systems.
2. The self-signed SSL certificates are for development only; production would use proper certificates.
3. The hardcoded passwords in the Chef cookbooks are for development only; production would use a secrets management solution.
4. The Vagrant development environment will continue to be used for testing.
5. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
6. The current security configurations (fail2ban, UFW, SSH hardening) are appropriate for the target environment.
7. The Redis configuration hack is a workaround for compatibility issues that may need to be addressed differently in Ansible.
8. The current Nginx site configurations (test.cluster.local, ci.cluster.local, status.cluster.local) will remain the same.