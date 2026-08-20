# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services (Redis and Memcached). The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for migration is 2-3 weeks, with moderate complexity due to the security configurations and SSL certificate management.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies.
- `solo.json`: Chef configuration data with run list and node attributes for Nginx sites, SSL, and security settings.
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings.
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef.
- `Vagrantfile`: Defines the Vagrant VM configuration using Fedora 42 with port forwarding and networking.

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ (as specified in cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development/testing

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or dedicated tasks for Redis installation and configuration

### Security Considerations

- **Firewall Configuration**: The current setup uses UFW for firewall management. Migration should use the `ansible.posix.firewalld` module for Fedora or `community.general.ufw` module for Ubuntu.
- **Fail2ban Integration**: Current setup configures fail2ban for intrusion prevention. Migration should use Ansible to configure fail2ban with similar jail settings.
- **SSH Hardening**: Current setup disables root login and password authentication. Migration should maintain these security practices.
- **SSL Certificate Management**: Self-signed certificates are generated for each site. Migration should use the `community.crypto` collection for certificate management.
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - These should be moved to Ansible Vault or another secrets management solution

### Technical Challenges

- **Multi-site Nginx Configuration**: The current setup dynamically creates Nginx site configurations based on node attributes. The Ansible equivalent will need to use templates with variable substitution and loops.
- **SSL Certificate Generation**: Self-signed certificates are generated for each site. The migration will need to use the `community.crypto.openssl_*` modules to replicate this functionality.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL. The Ansible playbook will need to ensure proper service ordering and dependencies.
- **Redis Configuration Hack**: The current setup includes a Ruby block to modify Redis configuration files after installation. The Ansible equivalent will need to use lineinfile or template modules to achieve the same result.

### Migration Order

1. **cache cookbook** (low risk, standalone): Convert to Ansible role for Redis and Memcached configuration
2. **nginx-multisite cookbook** (moderate complexity): Convert to Ansible role for Nginx installation, configuration, and security hardening
3. **fastapi-tutorial cookbook** (high complexity): Convert to Ansible role for FastAPI application deployment with PostgreSQL database

### Assumptions

1. The target environment will continue to be Fedora 42 or similar Linux distributions.
2. Self-signed certificates are acceptable for the migrated solution (not using Let's Encrypt or other CA).
3. The current security configurations (fail2ban, ufw, SSH hardening) are required in the migrated solution.
4. The Vagrant development workflow will be maintained, but using Ansible provisioner instead of Chef.
5. The current Redis and Memcached configurations are sufficient and don't require additional tuning.
6. The PostgreSQL database setup for FastAPI is simple and doesn't include replication or advanced features.
7. The current directory structure with multiple sites will be maintained in the Ansible solution.