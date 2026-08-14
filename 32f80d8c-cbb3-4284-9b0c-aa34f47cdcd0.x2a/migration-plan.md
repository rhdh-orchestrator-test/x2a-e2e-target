# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with FastAPI application backend and caching services (Redis and Memcached). The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 2-3 weeks, with moderate complexity due to the SSL certificate management, security configurations, and external dependencies.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall)

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Configures caching services (Memcached and Redis) with security settings
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies.
- `solo.json`: Chef configuration file containing the run list and node attributes.
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings.
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef.
- `Vagrantfile`: Vagrant configuration for development environment using Fedora 42.

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in the Vagrant development environment.
- **Virtual Machine Technology**: Vagrant with libvirt provider.
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.nginx collection
- **memcached (~> 6.0)**: Replace with Ansible memcached role or community.general.memcached module
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or community.redis collection

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates for development. Migration should maintain this capability while allowing for production certificate management.
  - Migration approach: Use Ansible's openssl_* modules for certificate generation and management.

- **Firewall Configuration**: The current implementation uses UFW for firewall management.
  - Migration approach: Use Ansible's ufw module or firewalld module depending on target OS.

- **Fail2ban Configuration**: The current implementation configures fail2ban for intrusion prevention.
  - Migration approach: Use Ansible's community.general.fail2ban module.

- **SSH Hardening**: The current implementation disables root login and password authentication.
  - Migration approach: Use Ansible's openssh_config module or security role.

- **Vault/secrets management**: 
  - Redis password in cache cookbook (hardcoded as 'redis_secure_password_123')
  - PostgreSQL database credentials in fastapi-tutorial cookbook (hardcoded as 'fastapi_password')
  - Migration approach: Use Ansible Vault for storing sensitive credentials.

### Technical Challenges

- **Multi-site Nginx Configuration**: The current implementation dynamically creates Nginx site configurations based on node attributes.
  - Mitigation: Use Ansible templates with variable substitution to achieve the same dynamic configuration.

- **SSL Certificate Generation**: The current implementation generates self-signed certificates for each site.
  - Mitigation: Use Ansible's openssl_* modules to generate certificates with similar parameters.

- **Service Dependencies**: The FastAPI application depends on PostgreSQL, and Nginx depends on the SSL certificates.
  - Mitigation: Use Ansible handlers and notify mechanisms to ensure proper service restart order.

- **Redis Configuration Hack**: The current implementation includes a ruby_block to modify Redis configuration files after they're created.
  - Mitigation: Create a custom Redis configuration template in Ansible that doesn't require post-processing.

### Migration Order

1. **cache** (Priority 1): Lowest complexity, minimal dependencies
   - Create Ansible roles for Memcached and Redis
   - Implement secure password management with Ansible Vault

2. **nginx-multisite** (Priority 2): Moderate complexity
   - Create Ansible role for Nginx with SSL and security configurations
   - Implement site template generation
   - Configure security features (fail2ban, ufw)

3. **fastapi-tutorial** (Priority 3): Highest complexity
   - Create Ansible role for Python application deployment
   - Configure PostgreSQL database
   - Set up systemd service

### Assumptions

1. The target environment will continue to be Fedora/CentOS/Ubuntu Linux systems.
2. Self-signed certificates are acceptable for development, but production deployment may require integration with Let's Encrypt or other certificate providers.
3. The FastAPI application source will continue to be available at the specified Git repository.
4. The security requirements (fail2ban, firewall, SSH hardening) will remain the same.
5. The current password values in the Chef recipes are development passwords and will be replaced with secure values in Ansible Vault.
6. The Nginx site configuration structure will remain similar, with multiple virtual hosts and SSL enabled for each.
7. The PostgreSQL database will be local to the application server rather than a remote database service.