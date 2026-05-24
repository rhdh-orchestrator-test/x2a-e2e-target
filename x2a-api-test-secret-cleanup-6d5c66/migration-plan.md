# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- External dependencies on community cookbooks will need Ansible equivalents
- Security configurations are present and need careful migration
- Secrets management needs improvement in the Ansible implementation

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw)

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks. Lists both local and external dependencies with version constraints.
- `solo.json`: Chef configuration file defining the run list and node attributes. Contains site configurations and security settings.
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings.
- `Vagrantfile`: Defines the development VM using Fedora 42, with port forwarding and resource allocation.
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef, installs dependencies and runs Chef Solo.

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in the Vagrant development environment.
- **Virtual Machine Technology**: Vagrant with libvirt provider (based on Vagrantfile configuration).
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or DavidWittman.redis

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW. Migrate to Ansible's `ufw` module or `firewalld` module depending on target OS.
- **Fail2ban Setup**: Migrate fail2ban configuration to Ansible using the `template` module for configuration files.
- **SSH Hardening**: The Chef cookbook disables root login and password authentication. Use Ansible's `lineinfile` or `template` module to configure SSH.
- **SSL Certificate Management**: Self-signed certificates are generated in the Chef cookbook. Use Ansible's `openssl_certificate` module for certificate generation.
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi`/`fastapi_password`)
  - No centralized secrets management is currently implemented
  - Recommend implementing Ansible Vault for all credentials in the Ansible migration

### Technical Challenges

- **Multi-site Nginx Configuration**: The Chef cookbook dynamically creates Nginx site configurations from node attributes. Ansible templates will need to replicate this dynamic behavior.
- **SSL Certificate Generation**: The Chef cookbook generates self-signed certificates. Ansible will need to handle certificate generation and management.
- **Database Initialization**: The FastAPI application requires PostgreSQL database setup. Ansible's PostgreSQL modules will need to replace the current shell commands.
- **Service Orchestration**: The current setup has interdependent services (Nginx, Redis, Memcached, PostgreSQL, FastAPI). Ansible handlers and proper ordering will be needed.

### Migration Order

1. **cache** (Priority 1): Relatively simple cookbook with external dependencies, good starting point
2. **nginx-multisite** (Priority 2): Core infrastructure component with security configurations
3. **fastapi-tutorial** (Priority 3): Application deployment that depends on properly configured infrastructure

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based systems.
2. The Vagrant development environment will be maintained for testing the Ansible playbooks.
3. Self-signed certificates are acceptable for development, but production may require proper certificates.
4. The current hardcoded credentials will be replaced with Ansible Vault variables.
5. The FastAPI application source will continue to be available at the specified Git repository.
6. The current security configurations (fail2ban, ufw, SSH hardening) are still required in the target environment.
7. The multi-site Nginx configuration pattern will be maintained in the Ansible roles.
8. Redis and Memcached configurations will remain largely the same.