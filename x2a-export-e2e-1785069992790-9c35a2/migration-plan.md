# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-service environment with web servers, caching, and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 2-3 weeks, with moderate complexity due to the security configurations and multi-site setup.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures nginx with multiple SSL-enabled subdomains, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, fail2ban integration, UFW firewall rules, security headers

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef configuration file with node attributes and run list
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Provisioning script for Vagrant environment
- `Vagrantfile`: Vagrant configuration for development environment

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or local development

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks with custom configuration

### Security Considerations

- **SSL Certificate Management**: The current setup generates self-signed certificates. Migration should maintain this capability or integrate with Let's Encrypt using Ansible's community.crypto modules.
- **Firewall Configuration**: UFW rules need to be migrated to equivalent Ansible UFW module tasks.
- **fail2ban Integration**: Configuration needs to be migrated to Ansible tasks.
- **SSH Hardening**: SSH configuration hardening (disabling root login, password authentication) needs to be preserved.
- **Vault/secrets management**:
  - Redis password in cache cookbook (plaintext in recipe)
  - PostgreSQL credentials in fastapi-tutorial cookbook (plaintext in recipe)
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Configuration**: The nginx-multisite cookbook manages multiple virtual hosts with different configurations. This will require careful template conversion and variable management in Ansible.
- **Service Orchestration**: The current setup has interdependent services (nginx, PostgreSQL, FastAPI application). Proper ordering and handlers will be needed in Ansible.
- **Template Conversion**: Several ERB templates need to be converted to Jinja2 format for Ansible.
- **Security Hardening**: The comprehensive security configurations (headers, fail2ban, firewall) need careful migration to maintain security posture.

### Migration Order

1. **cache role** (low complexity, standalone functionality)
2. **fastapi-tutorial role** (moderate complexity, database integration)
3. **nginx-multisite role** (high complexity, security configurations, multi-site setup)

### Assumptions

1. The target environment will continue to be Vagrant-based for development/testing
2. Self-signed certificates are acceptable (no need for Let's Encrypt integration)
3. The same security posture should be maintained in the Ansible implementation
4. The FastAPI application source will continue to be pulled from the same Git repository
5. Redis and Memcached configurations should remain functionally equivalent
6. The multi-site nginx configuration should support the same three sites with the same settings
7. PostgreSQL database setup should maintain the same user/database configuration