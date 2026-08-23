# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for migration is 2-3 weeks, with moderate complexity due to the SSL configuration, security hardening, and application deployment requirements.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database setup
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment, Git repository deployment, PostgreSQL database creation, systemd service configuration

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, fail2ban integration, UFW firewall rules

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication, Memcached configuration

**CRITICAL PATH VERIFICATION:**
The following Chef cookbooks with default.rb recipes have been verified:
- cookbooks/fastapi-tutorial/recipes/default.rb
- cookbooks/nginx-multisite/recipes/default.rb
- cookbooks/cache/recipes/default.rb

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef configuration file with run list and node attributes
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Vagrant configuration for local development/testing using Fedora 42
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile) with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Libvirt (from Vagrantfile)
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or system package installation
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or system package installation with custom configuration

### Security Considerations

- **SSL Certificate Management**: Self-signed certificates are generated for development; migration should maintain this capability while allowing for production certificate integration
- **Firewall Configuration**: UFW rules need to be migrated to equivalent firewall-cmd (for Fedora) or ufw Ansible modules
- **fail2ban Configuration**: Configuration needs to be migrated to Ansible
- **SSH Hardening**: SSH security configurations (disable root login, password authentication) need to be migrated
- **Vault/secrets management**: 
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL credentials in fastapi-tutorial cookbook: username "fastapi" with password "fastapi_password"
  - These should be moved to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple virtual hosts with SSL needs careful implementation in Ansible
- **Service Dependencies**: Ensuring proper ordering of service deployments (PostgreSQL before FastAPI, etc.)
- **SSL Certificate Generation**: Implementing self-signed certificate generation in Ansible
- **System Hardening**: Migrating the security configurations and sysctl settings

### Migration Order

1. **cache** (low complexity): Simple service installation and configuration
2. **nginx-multisite** (moderate complexity): Web server with virtual hosts and SSL
3. **fastapi-tutorial** (moderate complexity): Application deployment with database dependencies

### Assumptions

1. The target environment will continue to be Fedora-based, though the cookbooks support Ubuntu and CentOS as well
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or other CA)
3. The same virtual host names will be maintained (test.cluster.local, ci.cluster.local, status.cluster.local)
4. The FastAPI application source will continue to be available at the specified Git repository
5. The current security posture (fail2ban, firewall, SSH hardening) should be maintained
6. The current Redis and PostgreSQL passwords are for development only and will be replaced with more secure values in production
7. The Vagrant development environment should be maintained but converted to use Ansible provisioning