# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks, handling external dependencies, and ensuring proper security configurations are maintained.

**Scope**: 3 Chef cookbooks with external dependencies
**Complexity**: Medium
**Estimated Timeline**: 3-4 weeks

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site-specific configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)

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

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints.
- `solo.json`: Chef Solo configuration file defining the run list and node attributes.
- `solo.rb`: Chef Solo configuration file specifying file paths and log settings.
- `Vagrantfile`: Defines a Vagrant VM configuration using Fedora 42 with port forwarding and resource allocation.
- `vagrant-provision.sh`: Shell script that installs Chef and Berkshelf, then runs Chef Solo in the Vagrant environment.

### Target Details

- **Operating System**: Fedora (based on Vagrantfile specifying "generic/fedora42"), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting local development/testing environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)

### Security Considerations

- **Firewall Configuration**: The nginx-multisite cookbook configures UFW with specific rules for SSH, HTTP, and HTTPS. Migration should use Ansible's `ufw` module to maintain these configurations.
- **Fail2ban Setup**: The cookbook configures fail2ban for intrusion prevention. Migration should use Ansible's `fail2ban` modules or a dedicated role.
- **SSH Hardening**: The cookbook disables root login and password authentication. Migration should maintain these security practices using Ansible's `lineinfile` or template modules.
- **SSL Certificate Management**: Self-signed certificates are generated for development. Migration should use Ansible's `openssl_*` modules to maintain this functionality.
- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123" (hardcoded)
  - PostgreSQL password in fastapi-tutorial cookbook: "fastapi_password" (hardcoded)
  - No Chef Vault or encrypted data bags detected, but credentials should be moved to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The nginx-multisite cookbook dynamically generates site configurations based on node attributes. The Ansible equivalent will need to use loops with templates to achieve the same functionality.
- **Redis Configuration Hack**: The cache cookbook includes a ruby_block to modify Redis configuration files after they're created. This will need special handling in Ansible, possibly using `lineinfile` or templates with proper conditionals.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL being configured first. Ansible handlers and proper task ordering will be needed to maintain these dependencies.
- **SSL Certificate Generation**: The current implementation generates self-signed certificates. This logic needs to be replicated in Ansible using the `openssl_*` modules.

### Migration Order

1. **nginx-multisite** (Priority 1): This provides the core web server functionality and should be migrated first to establish the base infrastructure.
2. **cache** (Priority 2): The caching services can be migrated next as they are relatively self-contained.
3. **fastapi-tutorial** (Priority 3): This should be migrated last as it depends on both the web server and potentially the caching services.

### Assumptions

1. The target environment will continue to be Fedora-based, but with compatibility for Ubuntu and CentOS as specified in the cookbook metadata.
2. The self-signed certificates are for development only and not production use.
3. The hardcoded passwords in the cookbooks are not production values and will be replaced with Ansible Vault variables.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The current directory structure with separate modules will be maintained in the Ansible roles structure.
6. The Vagrant development environment will be maintained but converted to use Ansible provisioning instead of Chef.
7. No custom Chef resources or libraries are in use that would require special handling.
8. The current security configurations (fail2ban, ufw, SSH hardening) are sufficient and should be maintained as-is.