# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks, handling external dependencies, and ensuring proper security configurations are maintained.

**Scope**: 3 Chef cookbooks with dependencies on external cookbooks
**Complexity**: Medium
**Estimated Timeline**: 3-4 weeks

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and proper SSL configuration
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

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external cookbook dependencies
- `solo.json`: Chef configuration file containing the run list and node attributes
- `solo.rb`: Chef configuration file specifying cookbook paths and log settings
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration file for local development environment

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in Vagrant
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct configuration

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated in the nginx-multisite cookbook
  - Migration should maintain proper certificate permissions (640) and ownership (root:ssl-cert)
  - Consider using Ansible's community.crypto.openssl_* modules

- **Firewall Configuration**:
  - UFW is configured with default deny and specific allow rules
  - Migrate to Ansible's community.general.ufw module

- **Fail2ban Integration**:
  - Custom fail2ban configuration is applied
  - Use Ansible's community.general.fail2ban module

- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook
  - Recommend using Ansible Vault for these secrets

### Technical Challenges

- **Multi-site Configuration**: The nginx-multisite cookbook dynamically creates virtual hosts based on node attributes. Ansible templates will need to replicate this dynamic behavior.

- **SSL Certificate Generation**: Self-signed certificates are generated with specific parameters. Ensure Ansible maintains the same level of security.

- **System Hardening**: Security configurations in sysctl and SSH need to be properly migrated to maintain security posture.

- **Service Dependencies**: The FastAPI application depends on PostgreSQL. Ensure proper service ordering in Ansible.

### Migration Order

1. **cache cookbook** (low complexity, standalone functionality)
   - Implement Memcached configuration
   - Implement Redis with authentication

2. **nginx-multisite cookbook** (medium complexity, core infrastructure)
   - Implement base Nginx configuration
   - Implement SSL certificate generation
   - Implement virtual host configuration
   - Implement security hardening (fail2ban, UFW, headers)

3. **fastapi-tutorial cookbook** (high complexity, application deployment)
   - Implement PostgreSQL database setup
   - Implement Python environment configuration
   - Implement application deployment
   - Implement systemd service configuration

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based systems.
2. Self-signed certificates are acceptable for the migrated environment (production would likely use proper certificates).
3. The same security posture is required in the Ansible implementation.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The Vagrant development environment should be maintained but converted to use Ansible provisioning.
6. No changes to the application architecture are required as part of the migration.