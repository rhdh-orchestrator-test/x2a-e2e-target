# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application with PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- Total: 5-6 weeks

**Complexity Assessment:** Medium
- The repository has well-structured Chef cookbooks with clear dependencies
- Security configurations are present and need careful migration
- External cookbook dependencies need to be replaced with Ansible Galaxy roles or custom implementations

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall)

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints.
- `solo.json`: Chef configuration file containing the run list and node attributes for Nginx sites and security settings.
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings.
- `Vagrantfile`: Defines the development VM using Fedora 42, with port forwarding and resource allocation.
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef and run the cookbooks.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be a local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` module or community.general collection
- **memcached (~> 6.0)**: Replace with Ansible's `memcached` module or dedicated role
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role from Galaxy or custom implementation

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW. Migration should use Ansible's `ufw` module.
- **Fail2ban Setup**: Migrate fail2ban configuration using Ansible's `template` module for configuration files.
- **SSH Hardening**: Migrate SSH security settings (disable root login, password authentication) using Ansible's `lineinfile` or `template` modules.
- **SSL Certificate Management**: Replace self-signed certificate generation with Ansible's `openssl_*` modules.
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: The Chef cookbook dynamically creates Nginx site configurations based on node attributes. This pattern needs to be replicated in Ansible using templates and loops.
- **SSL Certificate Generation**: Self-signed certificate generation needs to be migrated to use Ansible's `openssl_*` modules.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL. Ensure proper service ordering in Ansible playbooks.
- **Idempotent Database Creation**: Ensure PostgreSQL database and user creation is idempotent in Ansible.

### Migration Order

1. **nginx-multisite** (Priority 1): Core infrastructure component that other services depend on
   - Create Ansible role for Nginx installation and configuration
   - Implement templates for site configuration
   - Migrate security hardening (fail2ban, ufw)
   - Implement SSL certificate generation

2. **cache** (Priority 2): Supporting services
   - Create Ansible roles for Memcached and Redis
   - Implement Redis authentication using Ansible Vault for password storage
   - Ensure proper service configuration and startup

3. **fastapi-tutorial** (Priority 3): Application layer
   - Create Ansible role for PostgreSQL installation and configuration
   - Implement FastAPI application deployment
   - Configure systemd service
   - Set up environment variables and database connection

### Assumptions

1. The target environment will continue to be Fedora-based systems (specifically Fedora 42 as indicated in the Vagrantfile).
2. The same directory structure for web content will be maintained (`/var/www/[site_name]`).
3. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or other CA).
4. The FastAPI application repository at `https://github.com/dibanez/fastapi_tutorial.git` will remain available.
5. The current security settings (fail2ban, ufw, SSH hardening) are appropriate for the target environment.
6. The Redis and PostgreSQL passwords in the current configuration are development passwords and will be replaced with more secure passwords in production.
7. The Nginx sites configuration in solo.json overrides the default attributes in the cookbook.