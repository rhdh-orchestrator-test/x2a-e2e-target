# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks, handling external dependencies, and ensuring proper security configurations are maintained.

**Scope**: 3 Chef cookbooks with moderate complexity
**Estimated Timeline**: 2-3 weeks
**Complexity**: Medium

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures nginx with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, fail2ban integration, UFW firewall management

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including external cookbooks from Chef Supermarket (nginx, memcached, redisio)
- `solo.json`: Contains node attributes and run list for Chef Solo
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Defines a Fedora 42 VM for local development with port forwarding
- `vagrant-provision.sh`: Bash script to provision the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or collection (e.g., `ansible.posix.nginx`)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., `geerlingguy.memcached`)
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role (e.g., `geerlingguy.redis`)

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should maintain this capability or integrate with Let's Encrypt.
  - Migration approach: Use Ansible's `openssl_*` modules or `community.crypto` collection

- **Firewall Configuration**: UFW is configured with specific rules for HTTP, HTTPS, and SSH.
  - Migration approach: Use Ansible's `ufw` module to maintain identical firewall rules

- **SSH Hardening**: SSH configuration disables root login and password authentication.
  - Migration approach: Use Ansible's `lineinfile` module or `ansible.posix.ssh_config` to apply identical SSH security settings

- **Fail2ban Integration**: Fail2ban is configured for brute force protection.
  - Migration approach: Use Ansible's `template` module to configure fail2ban with identical settings

- **Vault/secrets management**:
  - Redis password in cache cookbook: `redis_secure_password_123`
  - PostgreSQL database credentials in fastapi-tutorial cookbook: `fastapi:fastapi_password`
  - Migration approach: Use Ansible Vault to secure these credentials

### Technical Challenges

- **Multi-site Configuration**: The nginx-multisite cookbook dynamically creates virtual hosts based on attributes. 
  - Mitigation: Use Ansible loops with templates to achieve the same dynamic configuration

- **Service Dependencies**: The FastAPI application depends on PostgreSQL being configured first.
  - Mitigation: Use Ansible handlers and proper task ordering to ensure dependencies are met

- **Custom Ruby Block**: The cache cookbook uses a Ruby block to modify Redis configuration.
  - Mitigation: Use Ansible's `lineinfile` or `replace` modules to achieve the same configuration changes

### Migration Order

1. **nginx-multisite** (Priority 1): Core infrastructure component that other services depend on
2. **cache** (Priority 2): Supporting services that the application may depend on
3. **fastapi-tutorial** (Priority 3): Application deployment that depends on the infrastructure

### Assumptions

1. The target environment will continue to be Fedora-based systems (specifically Fedora 42 as indicated in the Vagrantfile)
2. The self-signed SSL certificates approach is acceptable for the migrated solution
3. The current security configurations (fail2ban, UFW, SSH hardening) should be maintained in the Ansible implementation
4. The directory structure for web content (/var/www/[site]) should be preserved
5. The PostgreSQL database configuration for the FastAPI application should remain the same
6. Redis will continue to require password authentication
7. The FastAPI application will be deployed from the same Git repository
8. The systemd service configuration for the FastAPI application should be preserved