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
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4)
- `solo.json`: Defines the run list and configuration attributes for nginx sites and security settings
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `Vagrantfile`: Defines a Fedora 42 VM with port forwarding for development/testing
- `vagrant-provision.sh`: Bash script to install Chef and run the cookbooks in the Vagrant environment

### Target Details

- **Operating System**: Fedora (based on Vagrantfile using "generic/fedora42"), with support for Ubuntu (>= 18.04) and CentOS (>= 7.0) mentioned in cookbook metadata
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role (e.g., geerlingguy.redis)
- **PostgreSQL**: Replace with Ansible PostgreSQL role (e.g., geerlingguy.postgresql)

### Security Considerations

- **SSL Certificate Management**: 
  - Current implementation generates self-signed certificates
  - Migration approach: Use Ansible's openssl_* modules or community.crypto collection

- **Firewall Configuration**: 
  - Current implementation uses UFW
  - Migration approach: Use Ansible's ufw module or firewalld module depending on target OS

- **Fail2ban Integration**: 
  - Current implementation configures fail2ban for intrusion prevention
  - Migration approach: Use Ansible fail2ban role or direct configuration via templates

- **SSH Hardening**: 
  - Current implementation disables root login and password authentication
  - Migration approach: Use Ansible's lineinfile module or ssh role

- **Vault/secrets management**:
  - Redis password hardcoded in recipe: "redis_secure_password_123"
  - PostgreSQL password hardcoded in recipe: "fastapi_password"
  - Migration approach: Use Ansible Vault for storing sensitive credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation dynamically generates Nginx site configurations based on attributes
  - Mitigation: Use Ansible templates with loops to generate site configurations from variables

- **SSL Certificate Generation**: 
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's openssl_* modules to generate certificates or integrate with Let's Encrypt

- **Service Orchestration**: 
  - Description: Multiple interdependent services (Nginx, Redis, Memcached, PostgreSQL, FastAPI)
  - Mitigation: Use Ansible handlers and proper dependency ordering

- **Python Environment Management**: 
  - Description: Python virtual environment setup for FastAPI application
  - Mitigation: Use Ansible's pip module with virtualenv parameter

### Migration Order

1. **cache cookbook** (low risk, standalone services)
   - Implement Redis and Memcached configuration
   - Address password security with Ansible Vault

2. **nginx-multisite cookbook** (moderate complexity)
   - Implement base Nginx configuration
   - Implement security configurations (fail2ban, UFW)
   - Implement SSL certificate generation
   - Implement virtual host configuration

3. **fastapi-tutorial cookbook** (high complexity, dependencies)
   - Implement PostgreSQL database setup
   - Implement Python environment and application deployment
   - Implement systemd service configuration

### Assumptions

1. The target environment will continue to be Fedora-based, with potential for Ubuntu or CentOS as mentioned in the cookbook metadata.
2. Self-signed certificates are acceptable for the migrated solution, as they are used in the current implementation.
3. The security requirements (fail2ban, UFW, SSH hardening) will remain the same in the migrated solution.
4. The FastAPI application source code will continue to be pulled from the same Git repository.
5. The current hardcoded credentials will be replaced with more secure solutions using Ansible Vault.
6. The current directory structure for web content and application files will be maintained.
7. The Vagrant development environment will be replaced with an equivalent Ansible-based solution.