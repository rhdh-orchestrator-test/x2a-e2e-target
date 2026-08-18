# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx configuration with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 2-3 weeks, with moderate complexity due to the interdependencies between components and security configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints.
- `solo.json`: Chef node configuration file that defines the run list and attribute overrides.
- `solo.rb`: Chef Solo configuration file.
- `Vagrantfile`: Defines the development VM configuration using Vagrant with Fedora 42.
- `vagrant-provision.sh`: Shell script that installs Chef and runs the cookbooks in the Vagrant environment.

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) based on cookbook metadata, but the Vagrantfile uses Fedora 42.
- **Virtual Machine Technology**: Vagrant with libvirt provider (based on Vagrantfile configuration).
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks

### Security Considerations

- **SSL/TLS Management**: The current setup generates self-signed certificates. Migration should maintain this capability or integrate with Let's Encrypt.
- **Firewall Configuration**: UFW configuration needs to be migrated to equivalent Ansible UFW module tasks.
- **Fail2ban Setup**: Fail2ban configuration needs to be migrated to Ansible tasks.
- **SSH Hardening**: SSH security configurations (disabling root login, password authentication) need to be migrated.
- **Vault/secrets management**: 
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL credentials in fastapi-tutorial cookbook: User "fastapi" with password "fastapi_password"
  - Total credentials detected: 2 hardcoded passwords

### Technical Challenges

- **Multi-site Configuration**: The Nginx multi-site setup with dynamic site generation will require careful templating in Ansible.
- **SSL Certificate Generation**: Self-signed certificate generation logic needs to be replicated in Ansible.
- **Service Dependencies**: Ensuring proper ordering of service deployments (database before application, etc.).
- **Security Hardening**: Comprehensive security configurations need to be maintained across the migration.

### Migration Order

1. **cache cookbook** (low complexity): Simple package installations and configurations for Memcached and Redis.
2. **nginx-multisite cookbook** (moderate complexity): Core infrastructure component with security configurations.
3. **fastapi-tutorial cookbook** (moderate complexity): Application deployment with database dependencies.

### Assumptions

1. The target environment will continue to be Fedora-based (as per Vagrantfile) despite cookbooks supporting Ubuntu and CentOS.
2. Self-signed certificates are acceptable for the migrated solution (production would likely use proper certificates).
3. The current security configurations (fail2ban, UFW, SSH hardening) are required in the migrated solution.
4. The directory structure for web content (/var/www/[site]) should be maintained.
5. PostgreSQL and Python versions are not explicitly specified and will use system defaults.
6. The FastAPI application will continue to be deployed from the same GitHub repository.
7. The Redis password and PostgreSQL credentials will be maintained as-is in the migration.