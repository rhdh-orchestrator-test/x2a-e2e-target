# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to Ansible roles and playbooks. The estimated timeline for this migration is 3-4 weeks, with moderate complexity due to the multi-site configuration and security hardening requirements.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and fail2ban integration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, firewall configuration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef configuration file containing the run list and node attributes
- `solo.rb`: Chef configuration file specifying cookbook paths and log settings
- `Vagrantfile`: Defines the development VM configuration using Fedora 42
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development/testing

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or custom role
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy or custom role
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role from Galaxy or custom role

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration should maintain proper file permissions (640 for private keys)
  - Consider using Ansible's crypto modules for certificate generation

- **Firewall Configuration**: 
  - UFW firewall rules need to be migrated to Ansible's ufw module
  - Default deny policy with specific allow rules for SSH, HTTP, HTTPS

- **SSH Hardening**:
  - Disable root login
  - Disable password authentication
  - Maintain in Ansible using lineinfile or template module

- **System Hardening**:
  - Sysctl security settings need to be migrated
  - Fail2ban configuration needs to be preserved

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the FastAPI recipe (`fastapi:fastapi_password`)
  - These should be moved to Ansible Vault

### Technical Challenges

- **Multi-site Configuration**: 
  - The dynamic generation of multiple Nginx site configurations will need to be replicated in Ansible
  - Solution: Use Ansible's with_items/loop constructs with templates

- **SSL Certificate Generation**:
  - Self-signed certificate generation logic needs to be replicated
  - Solution: Use Ansible's openssl_* modules

- **Service Dependencies**:
  - Maintaining proper service dependencies (e.g., FastAPI depends on PostgreSQL)
  - Solution: Use Ansible handlers and meta dependencies between roles

- **Idempotent Execution**:
  - Ensuring database creation commands are idempotent
  - Solution: Use Ansible's postgresql_* modules instead of raw SQL commands

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Implement security hardening (fail2ban, firewall)
   - Configure virtual hosts

2. **cache** (low complexity, standalone service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Set up PostgreSQL
   - Deploy application code
   - Configure environment and systemd service

### Assumptions

1. The target environment will continue to be Fedora-based systems
2. Self-signed certificates are acceptable for the migrated solution
3. The same security hardening requirements will apply
4. The FastAPI application repository will remain available at the specified URL
5. The directory structure for web content and application code will remain the same
6. The Vagrant development environment will be maintained but converted to use Ansible provisioning
7. No additional monitoring or logging requirements beyond what's in the current Chef setup
8. No high availability or clustering requirements for the services