# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, templates, and security configurations.

**Scope**: 3 Chef cookbooks with external dependencies
**Complexity**: Medium
**Estimated Timeline**: 2-3 weeks

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), sysctl security settings

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (nginx, memcached, redisio) - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Contains node attributes and run list - will be replaced by Ansible inventory variables
- `solo.rb`: Chef configuration file - will be replaced by Ansible configuration
- `Vagrantfile`: Defines VM configuration for testing - can be adapted for Ansible testing
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM - will be replaced by Ansible playbook

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in Vagrant testing
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks

### Security Considerations

- **SSL/TLS Configuration**: 
  - Self-signed certificate generation needs to be migrated
  - Certificate and key paths need to be maintained
  - TLS protocol and cipher configurations need to be preserved

- **Firewall Configuration**:
  - UFW rules need to be migrated to Ansible ufw module
  - Default deny policy and specific allow rules need to be preserved

- **fail2ban Configuration**:
  - fail2ban jail configuration needs to be migrated

- **System Hardening**:
  - sysctl security settings need to be migrated
  - SSH hardening (disable root login, password authentication) needs to be preserved

- **Vault/secrets management**:
  - Redis password ("redis_secure_password_123") should be moved to Ansible Vault
  - PostgreSQL credentials ("fastapi"/"fastapi_password") should be moved to Ansible Vault

### Technical Challenges

- **Multi-site Configuration**: The dynamic generation of Nginx site configurations based on node attributes will need to be replicated in Ansible using templates and variables
- **SSL Certificate Management**: Self-signed certificate generation logic needs to be preserved
- **Service Dependencies**: Ensuring proper ordering of service installation, configuration, and startup
- **PostgreSQL User/Database Creation**: Ensuring idempotent database operations
- **Python Environment Management**: Setting up virtual environments and package installation

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Add security hardening (fail2ban, ufw, sysctl)
   - Add multi-site configuration

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Implement PostgreSQL installation and configuration
   - Set up Python environment and dependencies
   - Deploy application from Git
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Vagrant with libvirt for testing
2. The same operating systems (Ubuntu/CentOS) will be supported
3. The same security requirements will be maintained
4. Self-signed certificates are acceptable for development/testing
5. The FastAPI application source code will remain available at the same Git repository
6. The current network configuration (ports, IP addresses) will be preserved
7. The current directory structure for web content will be maintained