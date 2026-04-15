# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for migration is 3-4 weeks, with moderate complexity due to the security configurations and multi-site SSL setup.

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
    - Key Features: Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `Policyfile.rb`: Chef policy file defining the run list and cookbook dependencies
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `solo.json`: Node attributes and run list for Chef Solo
- `Vagrantfile`: Defines a Fedora 42 VM for development and testing
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in Vagrant for testing
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **ssl_certificate (~> 2.1)**: Replace with Ansible crypto modules (community.crypto.openssl_*)
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks

### Security Considerations

- **SSL Certificate Management**: Migration must preserve the self-signed certificate generation for development environments
- **Firewall Configuration**: UFW rules need to be converted to appropriate firewall modules (ufw or firewalld depending on target OS)
- **fail2ban Configuration**: Ensure fail2ban setup is properly migrated with equivalent templates
- **SSH Hardening**: Preserve SSH security settings (disable root login, password authentication)
- **Redis Authentication**: Ensure Redis password is properly managed in Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of site configurations based on attributes needs careful translation to Ansible variables and templates
- **SSL Certificate Generation**: Self-signed certificate generation logic needs to be replicated with Ansible crypto modules
- **System Hardening**: Security configurations across multiple services need to be carefully migrated
- **Service Dependencies**: Ensure proper ordering of service installations and configurations (e.g., PostgreSQL before FastAPI application)

### Migration Order

1. **cache cookbook** (low complexity, standalone functionality)
   - Implement Memcached configuration
   - Implement Redis with authentication

2. **nginx-multisite cookbook** (moderate complexity, core infrastructure)
   - Implement base Nginx installation and configuration
   - Implement SSL certificate generation
   - Implement site configuration templates
   - Implement security hardening (fail2ban, UFW)

3. **fastapi-tutorial cookbook** (high complexity, application deployment)
   - Implement PostgreSQL database setup
   - Implement Python environment and application deployment
   - Implement systemd service configuration

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based systems
2. Self-signed certificates are acceptable for development environments
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain accessible
4. The Redis password "redis_secure_password_123" will need to be stored securely in Ansible Vault
5. The PostgreSQL credentials (fastapi/fastapi_password) will need to be stored securely in Ansible Vault
6. The current security hardening approach (fail2ban, UFW, SSH configuration) is appropriate for the target environment

## Implementation Plan

### 1. Project Structure Setup

Create the following Ansible project structure:
```
ansible-nginx-multisite/
├── inventory/
│   ├── hosts.yml
│   └── group_vars/
│       ├── all.yml
│       └── webservers.yml
├── roles/
│   ├── nginx-multisite/
│   ├── cache/
│   └── fastapi-tutorial/
├── playbooks/
│   ├── site.yml
│   ├── nginx.yml
│   ├── cache.yml
│   └── fastapi.yml
└── ansible.cfg
```

### 2. Variable Migration

Convert Chef attributes to Ansible variables:
- Move node['nginx']['sites'] to group_vars/webservers.yml
- Move security settings to appropriate group_vars files
- Store sensitive information in Ansible Vault

### 3. Template Migration

Convert Chef templates to Ansible templates:
- Nginx configuration templates
- Site configuration templates
- Security configuration templates

### 4. Task Implementation

Implement tasks for each role based on the corresponding Chef recipes:
- Use Ansible modules instead of Chef resources (package, template, file, service)
- Use Ansible handlers for service notifications
- Implement idempotent task execution

### 5. Testing Strategy

- Use Molecule for role testing
- Create Vagrant-based test environment similar to the existing one
- Test each role individually and then the complete playbook

### 6. Documentation

- Document each role with README.md files
- Provide example playbooks
- Document variable requirements and defaults