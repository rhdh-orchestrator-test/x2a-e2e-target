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
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and fail2ban/ufw firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site SSL configuration, security headers, firewall rules, self-signed certificate generation

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies - will be replaced by Ansible Galaxy requirements.yml
- `Vagrantfile`: Defines development VM configuration - can be adapted for Ansible testing with minimal changes
- `solo.json`: Contains Chef node attributes and run list - will be converted to Ansible group_vars or host_vars
- `solo.rb`: Chef configuration file - not needed in Ansible
- `vagrant-provision.sh`: Shell script for provisioning Vagrant VM - will be replaced by Ansible playbook

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or direct package installation
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role from Galaxy or direct package installation

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration approach: Use Ansible's openssl_* modules to generate certificates

- **Firewall Configuration**: 
  - UFW is configured with specific rules
  - Migration approach: Use Ansible's ufw module to configure firewall rules

- **Fail2ban Configuration**: 
  - Fail2ban is installed and configured
  - Migration approach: Use Ansible's template module to configure fail2ban

- **SSH Hardening**: 
  - Root login disabled, password authentication disabled
  - Migration approach: Use Ansible's lineinfile or template module to configure SSH

- **Vault/secrets management**:
  - Redis password is hardcoded in the Chef recipe
  - PostgreSQL credentials are hardcoded in the FastAPI recipe
  - Migration approach: Use Ansible Vault to encrypt sensitive data

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current setup dynamically generates Nginx site configurations based on node attributes
  - Mitigation: Use Ansible templates with loops to generate site configurations from variables

- **SSL Certificate Generation**: 
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's openssl_* modules to generate certificates

- **PostgreSQL User and Database Creation**: 
  - Description: PostgreSQL users and databases are created using shell commands
  - Mitigation: Use Ansible's postgresql_* modules for more idempotent database management

- **Python Application Deployment**: 
  - Description: Python virtual environment and dependencies are managed through shell commands
  - Mitigation: Use Ansible's pip module for more idempotent Python package management

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Configure virtual hosts
   - Implement security hardening

2. **cache** (low complexity, standalone service)
   - Configure Memcached
   - Configure Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Set up PostgreSQL
   - Deploy FastAPI application
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora-based systems (Fedora 42 as specified in the Vagrantfile)
2. The same network configuration will be maintained (IP addresses, port forwarding)
3. Self-signed certificates are acceptable for development/testing purposes
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate for the target environment
6. Redis and Memcached configurations don't require significant changes from their current setup
7. The PostgreSQL database schema is managed by the FastAPI application and doesn't require additional migration steps
8. The current directory structure in the target environment (/opt/fastapi-tutorial, /var/www/*, etc.) should be maintained