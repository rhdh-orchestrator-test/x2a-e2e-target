# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 3-4 weeks, with moderate complexity due to the multi-component architecture and security configurations.

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
    - Key Features: Redis password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment, Git repository deployment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external cookbook dependencies
- `solo.json`: Chef configuration file containing the run list and node attributes
- `solo.rb`: Chef configuration file specifying cookbook paths and log settings
- `Vagrantfile`: Defines the development VM configuration using Fedora 42
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora (based on Vagrantfile specifying "generic/fedora42"), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create custom Nginx role
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or DavidWittman.redis

### Security Considerations

- **SSL Certificate Management**: 
  - Migration approach: Use Ansible's `openssl_*` modules for certificate generation
  - Consider integration with Let's Encrypt using `geerlingguy.certbot` role for production

- **Firewall Configuration (UFW)**:
  - Migration approach: Use Ansible's `ufw` module to configure firewall rules

- **Fail2ban Configuration**:
  - Migration approach: Create Ansible tasks using the `template` module for fail2ban configuration

- **Vault/secrets management**:
  - Redis password in cache cookbook: Store in Ansible Vault
  - PostgreSQL credentials in fastapi-tutorial cookbook: Store in Ansible Vault
  - Count: 2 credentials detected (Redis password, PostgreSQL user/password)

- **SSH Hardening**:
  - Migration approach: Use Ansible's `lineinfile` module or the `dev-sec.ssh-hardening` Galaxy role

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current Chef implementation uses a template to generate multiple virtual host configurations
  - Mitigation: Create an Ansible role with templates and a variable structure similar to the current node attributes

- **SSL Certificate Generation**:
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's `openssl_certificate` module with appropriate parameters

- **Service Orchestration**:
  - Description: The current implementation manages multiple interdependent services
  - Mitigation: Use Ansible handlers and proper dependency ordering in playbooks

- **Database Initialization**:
  - Description: PostgreSQL database and user creation for FastAPI application
  - Mitigation: Use Ansible's `postgresql_*` modules with proper idempotence checks

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Create base Nginx role
   - Implement multi-site configuration
   - Implement security configurations

2. **cache** (low complexity, standalone services)
   - Implement Memcached configuration
   - Implement Redis configuration with authentication

3. **fastapi-tutorial** (high complexity, application deployment)
   - Implement Python environment setup
   - Implement PostgreSQL database configuration
   - Implement application deployment and service configuration

### Assumptions

1. The target environment will continue to be Fedora-based systems, with potential support for Ubuntu and CentOS as specified in the cookbook metadata.
2. Self-signed certificates are acceptable for development, but production environments may require proper CA-signed certificates.
3. The current security configurations (fail2ban, ufw, SSH hardening) are required in the migrated solution.
4. The FastAPI application source will continue to be pulled from the same Git repository.
5. The current Redis and PostgreSQL passwords are development credentials and will be replaced with proper secrets management in production.
6. The Vagrant development environment should be preserved with equivalent functionality.
7. No changes to the application architecture or services are required as part of the migration.