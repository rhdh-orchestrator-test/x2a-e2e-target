# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks, handling external dependencies, and ensuring proper security configurations are maintained.

**Scope**: 3 Chef cookbooks with external dependencies
**Complexity**: Medium
**Estimated Timeline**: 3-4 weeks

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database provisioning, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks - will be replaced by Ansible requirements.yml
- `Vagrantfile`: Defines development VM using Fedora 42 - can be adapted for Ansible testing
- `solo.json`: Chef node attributes and run list - will be replaced by Ansible inventory variables
- `solo.rb`: Chef configuration file - will be replaced by ansible.cfg
- `vagrant-provision.sh`: Shell script for Chef provisioning in Vagrant - will be replaced by Ansible provisioner

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct configuration

### Security Considerations

- **Firewall Configuration**: UFW firewall rules need to be migrated to Ansible's ufw module
- **Fail2ban Setup**: Configuration needs to be migrated to Ansible tasks
- **SSH Hardening**: SSH configuration (disable root login, password authentication) needs to be migrated
- **Vault/secrets management**:
  - Redis password in cache cookbook (hardcoded as 'redis_secure_password_123')
  - PostgreSQL credentials in fastapi-tutorial cookbook (hardcoded as 'fastapi_password')
  - SSL certificates and private keys management
  - Total credentials detected: 2 hardcoded passwords, plus SSL certificate management

### Technical Challenges

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Consider using Ansible's openssl_* modules or integrating with Let's Encrypt via community modules.
- **Multi-site Configuration**: The dynamic generation of Nginx site configurations based on node attributes will need careful translation to Ansible templates and variables.
- **Service Dependencies**: Ensuring proper ordering of service installations and configurations, particularly for the FastAPI application which depends on PostgreSQL.

### Migration Order

1. **nginx-multisite cookbook** (moderate complexity, foundation for web services)
   - First implement basic Nginx installation and configuration
   - Then implement SSL certificate generation
   - Finally implement security hardening features

2. **cache cookbook** (low complexity, standalone services)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial cookbook** (high complexity, application deployment)
   - Implement PostgreSQL database setup
   - Implement Python environment and application deployment
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions.
2. Self-signed certificates are acceptable for development; production may require integration with proper certificate authorities.
3. The current security configurations (fail2ban, UFW, SSH hardening) are sufficient and should be maintained in the Ansible implementation.
4. The FastAPI application source will continue to be pulled from the same Git repository.
5. Redis and Memcached configurations don't have specific tuning requirements beyond what's in the current cookbooks.
6. The hardcoded credentials in the cookbooks should be replaced with Ansible Vault variables for improved security.
7. The multi-site Nginx configuration pattern should be preserved, with the same domain structure.