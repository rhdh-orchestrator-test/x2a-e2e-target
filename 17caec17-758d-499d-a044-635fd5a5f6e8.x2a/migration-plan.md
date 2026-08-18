# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup focused on web hosting with Nginx, caching services, and a FastAPI application. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for migration is 2-3 weeks, with moderate complexity due to the security configurations and multi-site setup.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment, Git repository deployment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Manages cookbook dependencies, including external cookbooks from Chef Supermarket (nginx, memcached, redisio)
- `solo.json`: Contains node configuration including the run list and attribute overrides for Nginx sites and security settings
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Defines the development VM using Fedora 42, with port forwarding and network configuration

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks with custom configuration

### Security Considerations

- **SSL Certificate Management**: The current setup generates self-signed certificates. Migration should maintain this capability while allowing for future integration with Let's Encrypt.
- **Security Hardening**: Several security measures need to be preserved:
  - fail2ban configuration for intrusion prevention
  - ufw firewall rules for ports 22, 80, and 443
  - sysctl security settings
  - SSH hardening (disabling root login, password authentication)
- **Vault/secrets management**: 
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Configuration**: The nginx-multisite cookbook manages multiple virtual hosts with SSL. This will require careful templating in Ansible.
- **Custom Resource**: The `lineinfile` resource in nginx-multisite will need to be replaced with Ansible's `lineinfile` module.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL, which needs to be reflected in the Ansible playbook ordering.
- **Template Conversion**: Several ERB templates need to be converted to Jinja2 format for Ansible.

### Migration Order

1. **cache cookbook** (low complexity, minimal dependencies)
   - Simple package installations and configurations
   - Good starting point to establish patterns

2. **nginx-multisite cookbook** (moderate complexity)
   - Core infrastructure component
   - Required for the application to be accessible

3. **fastapi-tutorial cookbook** (moderate complexity, depends on PostgreSQL)
   - Application deployment
   - Depends on database setup

### Assumptions

1. The target environment will continue to be Fedora-based systems, with potential for Ubuntu and CentOS as indicated in the cookbook metadata.
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or other certificate authority).
3. The current security configurations are appropriate and should be maintained in the Ansible implementation.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The current Redis and PostgreSQL passwords are for development only and will be replaced with secure passwords in production.
6. The Vagrant development environment should be preserved with equivalent functionality.