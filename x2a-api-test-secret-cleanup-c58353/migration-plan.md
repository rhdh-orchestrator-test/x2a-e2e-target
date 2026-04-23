# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks, handling external dependencies, and ensuring proper security configurations are maintained.

**Scope**: 3 Chef cookbooks with dependencies on external cookbooks
**Complexity**: Medium (standard web server patterns, caching services, and application deployment)
**Timeline Estimate**: 3-4 weeks (1 week per cookbook, plus testing and documentation)

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, fail2ban integration, UFW firewall configuration

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

- `Berksfile`: Dependency management file listing both local cookbooks and external dependencies from Chef Supermarket
- `solo.json`: Chef configuration file defining the run list and node attributes
- `solo.rb`: Chef configuration file defining paths and log settings
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration for local development/testing environment

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified (appears to be a local development environment)

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or collection (e.g., `geerlingguy.nginx`)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., `geerlingguy.memcached`)
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role (e.g., `geerlingguy.redis` or `DavidWittman.redis`)

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should maintain this capability while allowing for future integration with Let's Encrypt.
  - Migration approach: Use Ansible's `openssl_*` modules for certificate generation or community roles for Let's Encrypt integration.

- **Firewall Configuration**: The current implementation uses UFW. 
  - Migration approach: Use Ansible's `ufw` module or adapt to use `firewalld` for Fedora.

- **Fail2ban Integration**: Current implementation installs and configures fail2ban.
  - Migration approach: Use Ansible's `template` module to configure fail2ban or use a community role.

- **SSH Hardening**: Current implementation disables root login and password authentication.
  - Migration approach: Use Ansible's `lineinfile` module or a dedicated SSH hardening role.

- **Vault/secrets management**: 
  - Redis password in `cache/recipes/default.rb` (hardcoded as 'redis_secure_password_123')
  - PostgreSQL credentials in `fastapi-tutorial/recipes/default.rb` (hardcoded as 'fastapi_password')
  - Migration approach: Use Ansible Vault to securely store and manage these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: The current implementation uses templates to generate site configurations dynamically based on node attributes.
  - Mitigation: Create Ansible templates that replicate this functionality, using host variables instead of node attributes.

- **Redis Configuration Hack**: The current implementation includes a Ruby block to modify Redis configuration files after they're created.
  - Mitigation: Use Ansible templates to generate proper Redis configuration files directly, avoiding post-creation modifications.

- **PostgreSQL User/Database Creation**: The current implementation uses shell commands via `execute` resources.
  - Mitigation: Use Ansible's `postgresql_*` modules for more idiomatic database management.

### Migration Order

1. **nginx-multisite** (Priority 1): This module provides the web server foundation and should be migrated first to establish the basic infrastructure.

2. **cache** (Priority 2): The caching services should be migrated next as they are relatively self-contained and don't depend on the application.

3. **fastapi-tutorial** (Priority 3): The application deployment should be migrated last as it depends on both the web server and potentially the caching services.

### Assumptions

1. The target environment will continue to be Fedora-based systems (the Vagrantfile specifies Fedora 42).
2. The self-signed SSL certificates approach is acceptable for the migrated solution (rather than integrating with Let's Encrypt or another CA).
3. The current security configurations (fail2ban, UFW, SSH hardening) are required in the migrated solution.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The current directory structure in `/opt/server/` for website content and `/opt/fastapi-tutorial/` for the application will be maintained.
6. The current approach of using a Python virtual environment for the FastAPI application will be maintained.
7. The PostgreSQL database configuration (database name, user, password) can remain the same.
8. The Redis password can remain the same or be updated during migration.
9. The Nginx site configurations (server names, document roots) will remain the same.
10. The systemd service configuration for the FastAPI application will remain largely the same.