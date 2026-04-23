# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Scope**: 3 Chef cookbooks with external dependencies
**Complexity**: Medium
**Estimated Timeline**: 3-4 weeks

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and fail2ban/ufw firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, firewall configuration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment, Git repository deployment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef configuration file containing the run list and node attributes
- `solo.rb`: Chef configuration file specifying cookbook paths and log settings
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration file for local development environment

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or custom role
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy or custom role
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role from Galaxy or custom role

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should maintain this capability or integrate with Let's Encrypt.
- **Firewall Configuration**: The current setup uses UFW. Migration should maintain equivalent firewall rules.
- **Fail2ban Configuration**: Fail2ban setup needs to be migrated to protect against brute force attacks.
- **Security Headers**: Nginx security headers need to be preserved in the Ansible templates.
- **Vault/secrets management**:
  - Redis password in cache cookbook (hardcoded as 'redis_secure_password_123')
  - PostgreSQL database credentials in fastapi-tutorial cookbook (hardcoded as 'fastapi_password')
  - No Chef Vault or encrypted data bags are used, all secrets are in plaintext

### Technical Challenges

- **Multi-site Configuration**: The dynamic generation of multiple Nginx sites based on attributes needs to be carefully migrated to Ansible's templating system.
- **SSL Certificate Generation**: The self-signed certificate generation logic needs to be replicated in Ansible.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL, which needs to be maintained in the Ansible playbook ordering.
- **Idempotent Database Setup**: The PostgreSQL user and database creation needs to be made idempotent in Ansible.

### Migration Order

1. **nginx-multisite**: This is the foundation for the web infrastructure and should be migrated first.
2. **cache**: The caching services can be migrated next as they are relatively independent.
3. **fastapi-tutorial**: This should be migrated last as it depends on the web server being properly configured.

### Assumptions

1. The target environment will continue to be Fedora-based systems.
2. Self-signed certificates are acceptable for the migrated solution (production would likely require proper certificates).
3. The current security configurations (fail2ban, ufw, etc.) are appropriate for the target environment.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The current plaintext approach to secrets management is acceptable, though implementing Ansible Vault would be recommended.
6. The current VM resources (2GB RAM, 2 CPUs) are sufficient for the application stack.
7. The current network configuration with port forwarding (80→8080, 443→8443) should be maintained.