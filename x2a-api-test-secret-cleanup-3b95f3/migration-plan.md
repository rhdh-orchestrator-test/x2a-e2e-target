# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web server environment with caching services and a FastAPI application. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 3-4 weeks, with complexity rated as moderate due to the interdependencies between services and security configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and custom site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)

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

- `Berksfile`: Dependency management file listing cookbook dependencies and versions. Will be replaced by Ansible Galaxy requirements.yml.
- `solo.json`: Chef node configuration with run list and attributes. Will be replaced by Ansible inventory variables.
- `solo.rb`: Chef configuration file. Will be replaced by Ansible configuration.
- `Vagrantfile`: VM configuration for development/testing. Can be adapted for Ansible-based provisioning.
- `vagrant-provision.sh`: Shell script for Chef provisioning in Vagrant. Will be replaced by Ansible provisioning.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation and configuration
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package installation and configuration
- **Python 3 and pip**: Direct package installation via Ansible package module
- **PostgreSQL**: Replace with Ansible postgresql role or direct package installation and configuration

### Security Considerations

- **SSL Certificate Management**: 
  - Current implementation generates self-signed certificates
  - Migration approach: Use Ansible crypto modules for certificate generation or integrate with Let's Encrypt via certbot

- **Firewall Configuration (UFW)**:
  - Migration approach: Use Ansible ufw module or firewalld module (more appropriate for Fedora)

- **Fail2ban Configuration**:
  - Migration approach: Use Ansible to install and configure fail2ban with templates

- **SSH Hardening**:
  - Migration approach: Use Ansible to configure sshd_config with appropriate security settings

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL password is hardcoded in the recipe (`fastapi_password`)
  - Migration approach: Use Ansible Vault for storing sensitive credentials

### Technical Challenges

- **Custom Resource Migration**: 
  - The `lineinfile` custom resource in nginx-multisite needs to be replaced with Ansible's native lineinfile module
  - Description: The Chef custom resource has backup functionality that needs to be preserved

- **Multi-site Configuration**: 
  - Description: The dynamic generation of multiple Nginx site configurations needs to be preserved
  - Mitigation strategy: Use Ansible with_items/loop constructs and templates

- **Service Interdependencies**:
  - Description: The FastAPI application depends on PostgreSQL, and the web server depends on the application being available
  - Mitigation strategy: Use Ansible handlers and wait_for module to ensure services are available before proceeding

- **Ruby Block Replacements**:
  - Description: Several Ruby blocks are used for dynamic file manipulation
  - Mitigation strategy: Replace with Ansible's lineinfile, replace, or template modules

### Migration Order

1. **cache cookbook** (Priority 1 - low risk, foundational service)
   - Implement Memcached configuration
   - Implement Redis configuration with authentication

2. **fastapi-tutorial cookbook** (Priority 2 - moderate complexity)
   - Implement PostgreSQL installation and configuration
   - Implement Python environment setup
   - Implement application deployment and service configuration

3. **nginx-multisite cookbook** (Priority 3 - highest complexity)
   - Implement base Nginx installation and configuration
   - Implement security hardening (fail2ban, firewall, sysctl)
   - Implement SSL certificate generation
   - Implement multi-site configuration

### Assumptions

1. The target environment will continue to be Fedora-based systems (the current Vagrantfile specifies Fedora 42)
2. Self-signed certificates are acceptable for the migrated solution (production would likely require proper certificates)
3. The same directory structure for web content will be maintained (/opt/server/*)
4. The FastAPI application repository URL will remain accessible
5. The security requirements (fail2ban, firewall, SSH hardening) will remain the same
6. Redis and PostgreSQL passwords will be changed in the migrated solution for better security
7. The current Chef-based solution is functional and represents the desired end state
8. No additional features beyond what's in the current Chef implementation are required