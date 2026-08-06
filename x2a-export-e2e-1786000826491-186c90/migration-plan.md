# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx configuration with FastAPI application and caching services. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Scope**: 3 Chef cookbooks with external dependencies
**Complexity**: Medium
**Estimated Timeline**: 2-3 weeks

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), custom Nginx configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Configures caching services (Memcached and Redis) with security settings
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (nginx, memcached, redisio) - will be replaced with Ansible Galaxy requirements.yml
- `solo.json`: Contains Chef run list and configuration data - will be converted to Ansible inventory variables
- `solo.rb`: Chef configuration file - not needed in Ansible
- `Vagrantfile`: VM configuration for testing - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisioning script for Vagrant - will be replaced with Ansible provisioning

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or custom role
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy or custom role
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role from Galaxy or custom role

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should maintain this capability while allowing for future integration with Let's Encrypt.
  - Migration approach: Use Ansible's openssl_* modules for certificate generation

- **Firewall Configuration**: UFW is configured with specific rules for HTTP, HTTPS, and SSH.
  - Migration approach: Use Ansible's ufw module to configure identical rules

- **Fail2ban Configuration**: Custom fail2ban configuration is applied.
  - Migration approach: Create Ansible tasks to install and configure fail2ban with identical settings

- **SSH Hardening**: SSH is configured to disable root login and password authentication.
  - Migration approach: Use Ansible's lineinfile or template module to configure SSH settings

- **Vault/secrets management**:
  - Redis password in cache cookbook: 1 credential (plaintext in recipe)
  - PostgreSQL credentials in fastapi-tutorial cookbook: 2 credentials (plaintext in recipe)
  - Migration approach: Use Ansible Vault for all credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: The current implementation uses Chef templates to generate site configurations dynamically based on node attributes.
  - Mitigation: Create Ansible templates with similar logic, using host_vars or group_vars to store site configurations

- **Redis Configuration Hack**: The cache cookbook includes a ruby_block to modify Redis configuration files after they're created.
  - Mitigation: Create a custom Redis configuration template in Ansible that doesn't require post-processing

- **SSL Certificate Generation**: The current implementation generates self-signed certificates for each site.
  - Mitigation: Use Ansible's openssl_* modules to generate certificates with similar parameters

- **PostgreSQL User and Database Creation**: The fastapi-tutorial cookbook uses execute resources to create PostgreSQL users and databases.
  - Mitigation: Use Ansible's postgresql_* modules for more idempotent database management

### Migration Order

1. **nginx-multisite** (Priority 1): This is the foundation for the web infrastructure and should be migrated first.
   - Create base Nginx role
   - Implement security hardening (fail2ban, ufw)
   - Implement SSL certificate generation
   - Implement site configuration templates

2. **cache** (Priority 2): This provides caching services that may be required by applications.
   - Create Memcached role
   - Create Redis role with authentication

3. **fastapi-tutorial** (Priority 3): This depends on both web server and database services.
   - Create Python application deployment role
   - Implement PostgreSQL database configuration
   - Implement systemd service management

### Assumptions

1. The current Chef setup is functional and represents the desired state.
2. The target environment will continue to be Fedora-based systems.
3. Vagrant will continue to be used for development and testing.
4. Self-signed certificates are acceptable for the migrated solution.
5. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git is accessible and contains the expected code.
6. The current security settings (fail2ban, ufw, SSH hardening) are appropriate for the target environment.
7. The Redis configuration "hack" in the cache cookbook is necessary due to compatibility issues with the redisio cookbook.
8. The PostgreSQL database configuration in the fastapi-tutorial cookbook is appropriate for the application's needs.