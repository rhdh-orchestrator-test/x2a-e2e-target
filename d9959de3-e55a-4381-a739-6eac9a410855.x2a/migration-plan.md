# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx configuration with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for migration is 2-3 weeks, with moderate complexity due to the interdependencies between services and security configurations.

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
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Configuration data for Chef Solo, contains site configurations and security settings
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Defines the development VM using Fedora 42, with port forwarding and networking

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in the Vagrant development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or dedicated tasks for Redis installation and configuration

### Security Considerations

- **SSL/TLS Management**: 
  - Self-signed certificates are generated for each site
  - Migration should maintain the same certificate structure or integrate with Ansible's crypto modules
  - Certificate and key paths are configurable

- **Firewall Configuration**:
  - UFW firewall is configured with default deny policy
  - SSH, HTTP, and HTTPS ports are explicitly allowed
  - Replace with Ansible's firewall modules (ufw or firewalld depending on target OS)

- **SSH Hardening**:
  - Root login disabled
  - Password authentication disabled
  - Maintain these security practices in Ansible

- **Fail2ban Integration**:
  - Configured for brute force protection
  - Migrate to equivalent Ansible fail2ban role

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the FastAPI recipe (`fastapi`/`fastapi_password`)
  - These should be moved to Ansible Vault or other secure storage

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - The current setup dynamically generates site configurations based on node attributes
  - Ansible will need to use templates and variables to achieve the same flexibility
  - Solution: Use Ansible templates with variable substitution

- **SSL Certificate Generation**:
  - Self-signed certificates are generated for each site
  - Solution: Use Ansible's openssl_* modules to generate certificates or integrate with Let's Encrypt

- **Service Interdependencies**:
  - FastAPI depends on PostgreSQL
  - Nginx depends on the FastAPI service being available
  - Solution: Use Ansible handlers and conditional checks to manage service dependencies

- **Redis Configuration Hack**:
  - The current setup includes a Ruby block to modify Redis configuration
  - Solution: Create a custom Redis configuration template in Ansible

### Migration Order

1. **cache cookbook** (Low complexity)
   - Simple package installations and configurations
   - Good starting point to establish patterns

2. **nginx-multisite cookbook** (Medium complexity)
   - Core infrastructure component
   - Security configurations should be established early

3. **fastapi-tutorial cookbook** (Medium complexity)
   - Application deployment can build on the established infrastructure
   - Depends on PostgreSQL being configured correctly

### Assumptions

1. The target environment will continue to be Fedora/CentOS/Ubuntu based systems
2. Self-signed certificates are acceptable for the migrated solution (not production-ready)
3. The same security hardening requirements will apply in the Ansible version
4. The directory structure for web content will remain the same
5. PostgreSQL and Redis passwords will need to be securely managed in the new solution
6. The Vagrant development environment will be maintained but updated to use Ansible provisioning