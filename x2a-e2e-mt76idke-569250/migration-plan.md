# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated complexity is moderate, with an estimated timeline of 2-3 weeks for a complete migration, including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW), sysctl security settings

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Configures caching services (Memcached and Redis) with security settings
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef Solo configuration file containing the run list and node attributes
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration file for local development/testing environment

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ mentioned in cookbook metadata
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should maintain this capability while allowing for future integration with Let's Encrypt or other certificate providers.
- **Firewall Configuration**: UFW rules need to be migrated to equivalent Ansible UFW module tasks.
- **fail2ban Configuration**: Configuration needs to be migrated to Ansible tasks.
- **SSH Hardening**: SSH configuration hardening (disable root login, password authentication) needs to be migrated.
- **Vault/secrets management**: 
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL credentials in fastapi-tutorial cookbook: "fastapi:fastapi_password"
  - No external vault integration is currently used; credentials are hardcoded

### Technical Challenges

- **Multi-site Configuration**: The dynamic generation of multiple Nginx virtual hosts based on node attributes needs to be carefully migrated to Ansible's templating system.
- **SSL Certificate Generation**: The self-signed certificate generation logic needs to be preserved in Ansible.
- **Service Orchestration**: The current Chef implementation has a specific order of operations (security → nginx → ssl → sites) that needs to be maintained in Ansible.
- **Idempotency**: Ensuring that the Ansible playbooks maintain the idempotent behavior of the Chef recipes, especially for operations like database creation and SSL certificate generation.

### Migration Order

1. **nginx-multisite** (Priority 1): This is the foundation for the web infrastructure and should be migrated first.
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Add virtual host configuration
   - Add security hardening features

2. **cache** (Priority 2): This has external dependencies but is relatively self-contained.
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (Priority 3): This depends on a properly configured web server and potentially the caching services.
   - Implement Python environment setup
   - Implement PostgreSQL configuration
   - Implement application deployment and service configuration

### Assumptions

1. The target environment will continue to be Fedora-based, with potential support for Ubuntu and CentOS as mentioned in the cookbook metadata.
2. The self-signed SSL certificates are sufficient for the migration; no integration with external certificate authorities is required initially.
3. The current security configurations (fail2ban, UFW, SSH hardening) are appropriate and should be maintained in the Ansible implementation.
4. The Vagrant-based development/testing workflow will be maintained post-migration.
5. No CI/CD pipeline integration is required as part of the initial migration.
6. The current hardcoded credentials will be maintained in the initial migration, with potential enhancement to use Ansible Vault in a future phase.
7. The FastAPI application source code will continue to be pulled from the same Git repository.