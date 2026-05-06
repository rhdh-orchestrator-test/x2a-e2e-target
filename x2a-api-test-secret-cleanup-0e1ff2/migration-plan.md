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
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and proper SSL configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, fail2ban integration, UFW firewall configuration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, service management

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef configuration file containing the run list and node attributes
- `solo.rb`: Chef configuration file specifying cookbook paths and log settings
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration file for local development environment

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or local development

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated in the nginx-multisite cookbook
  - Migration should maintain proper certificate permissions (640) and ownership (root:ssl-cert)

- **Firewall Configuration**: 
  - UFW is configured in the security.rb recipe
  - Migration should ensure proper firewall rules are maintained

- **Fail2ban Integration**:
  - Fail2ban is configured for intrusion prevention
  - Migration should maintain fail2ban configuration

- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook
  - Migration should use Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - The current setup dynamically generates Nginx site configurations based on node attributes
  - Ansible solution will need to maintain this flexibility with templates and variables

- **SSL Certificate Generation**:
  - Self-signed certificates are generated with specific parameters
  - Ansible solution will need to replicate this or improve with Let's Encrypt integration

- **Service Orchestration**:
  - Multiple interdependent services (Nginx, Redis, Memcached, PostgreSQL, FastAPI)
  - Ansible solution will need to maintain proper service dependencies and ordering

### Migration Order

1. **cache cookbook** (low complexity, foundational service)
   - Simple package installation and configuration
   - Few dependencies on other components

2. **nginx-multisite cookbook** (medium complexity)
   - Core web server configuration
   - Security hardening components
   - SSL certificate management

3. **fastapi-tutorial cookbook** (high complexity)
   - Application deployment
   - Database configuration
   - Depends on both web server and caching services

### Assumptions

1. The target environment will continue to be Fedora-based systems (Fedora 42 as specified in Vagrantfile)
2. Self-signed certificates are acceptable for the migrated solution (production would likely require proper CA-signed certificates)
3. The current security configurations (fail2ban, UFW, SSH hardening) are required in the migrated solution
4. The FastAPI application source will continue to be pulled from the same Git repository
5. The PostgreSQL database structure and user permissions should remain the same
6. Redis will continue to require password authentication
7. The Nginx virtual host configurations and security headers should be preserved
8. The current directory structure for web content will be maintained