# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- External dependencies on community cookbooks need to be replaced with Ansible Galaxy roles
- Security configurations and SSL certificate management require careful migration
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

- `Berksfile`: Dependency management file listing both local cookbooks and external dependencies from Chef Supermarket. Migration will require finding equivalent Ansible Galaxy roles or creating custom roles.
- `solo.json`: Contains the Chef run list and configuration data that will need to be converted to Ansible variables.
- `solo.rb`: Chef configuration file that defines paths and log settings.
- `Vagrantfile`: Defines the development VM configuration using Fedora 42. Can be adapted to use Ansible provisioner instead of Chef.
- `vagrant-provision.sh`: Shell script that installs Chef and runs the cookbooks. Will need to be replaced with Ansible installation and execution.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu (>= 18.04) and CentOS (>= 7.0) mentioned in cookbook metadata
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` module or community.general collection
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role for Memcached (e.g., `geerlingguy.memcached`)
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role for Redis (e.g., `geerlingguy.redis` or `DavidWittman.redis`)

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Consider using Ansible's `openssl_*` modules or integrating with Let's Encrypt via `community.crypto.acme_certificate`.
- **Firewall Configuration**: Replace UFW commands with Ansible's `ufw` module or `firewalld` module depending on the target OS.
- **fail2ban Configuration**: Use Ansible Galaxy roles for fail2ban or create a custom role using Ansible's template module.
- **SSH Hardening**: Migrate SSH security settings using Ansible's `lineinfile` module or a dedicated SSH hardening role.
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - Consider using Ansible Vault for storing these secrets securely

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple Nginx site configurations will require careful templating in Ansible.
- **Redis Configuration Hack**: The Chef cookbook includes a hack to fix Redis configuration. This will need special attention during migration to ensure Redis works correctly.
- **PostgreSQL User and Database Creation**: The current implementation uses direct SQL commands. Consider using Ansible's PostgreSQL modules for better idempotence.
- **Service Management**: Ensure proper handling of service notifications and restarts in Ansible, which has a different notification system than Chef.

### Migration Order

1. **nginx-multisite** (Priority 1): Core infrastructure component that other services depend on
   - Create Ansible role for Nginx installation and configuration
   - Implement virtual host configuration with SSL support
   - Migrate security hardening features (fail2ban, ufw, sysctl)

2. **cache** (Priority 2): Supporting services for the application
   - Create Ansible roles for Memcached and Redis
   - Implement Redis authentication using Ansible Vault for password storage
   - Ensure proper service configuration and startup

3. **fastapi-tutorial** (Priority 3): Application deployment
   - Create Ansible role for Python application deployment
   - Implement PostgreSQL database setup using Ansible modules
   - Configure systemd service for the FastAPI application

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions.
2. Self-signed certificates are acceptable for development; production would require proper certificate management.
3. The FastAPI application repository at `https://github.com/dibanez/fastapi_tutorial.git` will remain available.
4. The current security settings (disable root login, password authentication disabled) will be maintained.
5. The current Redis configuration hack is necessary due to compatibility issues that may need to be addressed differently in Ansible.
6. The Nginx sites configuration in solo.json overrides the default attributes in the cookbook.
7. No specific backup or disaster recovery procedures are defined in the current implementation.
8. No monitoring or logging solutions are configured beyond standard service logs.