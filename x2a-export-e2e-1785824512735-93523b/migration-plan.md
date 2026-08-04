# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for migration is 2-3 weeks, with moderate complexity due to the security configurations and SSL certificate management.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW), sysctl security settings

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database setup
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment setup, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Caching services configuration including Memcached and Redis
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks, lists external dependencies (nginx, memcached, redisio)
- `solo.json`: Chef configuration with run list and node attributes
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment configuration using Fedora 42
- `vagrant-provision.sh`: Script to provision the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile) with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks

### Security Considerations

- **Firewall Configuration**: UFW rules need to be migrated to Ansible's `community.general.ufw` module
- **fail2ban**: Configuration needs to be migrated to Ansible tasks using templates
- **SSH Hardening**: SSH configuration needs to be migrated to Ansible's `ansible.posix.sshd_config` module
- **SSL Certificates**: Self-signed certificate generation needs to be migrated to Ansible's `community.crypto.openssl_*` modules
- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL database credentials in fastapi-tutorial cookbook: "fastapi:fastapi_password"
  - These should be migrated to Ansible Vault

### Technical Challenges

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should consider using Let's Encrypt with Ansible's `community.crypto.acme_certificate` module for production environments.
- **Multi-site Configuration**: The dynamic generation of Nginx site configurations based on node attributes needs careful translation to Ansible variables and templates.
- **Security Hardening**: The comprehensive security settings (sysctl, SSH, fail2ban) need to be properly migrated to maintain the same security posture.
- **Service Dependencies**: Ensuring proper service dependencies and ordering in Ansible (e.g., PostgreSQL before FastAPI application)

### Migration Order

1. **cache** (low risk, standalone): Migrate the Redis and Memcached configuration first as it has the fewest dependencies
2. **nginx-multisite** (moderate complexity): Migrate the Nginx configuration with its security components
3. **fastapi-tutorial** (high complexity): Migrate the application deployment with its database dependencies

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions
2. Self-signed certificates are acceptable for development, but production deployment may require proper certificates
3. The same security posture is required in the Ansible implementation
4. The FastAPI application source code will continue to be pulled from the same Git repository
5. The current directory structure and file paths will be maintained in the target environment
6. No changes to the application configuration or behavior are required during migration
7. The Vagrant development environment will be maintained but converted to use Ansible provisioner