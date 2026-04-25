# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, configuration templates, and security settings. Based on the complexity and scope, this migration is estimated to require 3-4 weeks of effort with a team of 2 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall), sysctl security settings

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file listing cookbook dependencies (nginx, memcached, redisio) - will be replaced by Ansible Galaxy requirements.yml
- `Vagrantfile`: VM configuration for development/testing - can be adapted for Ansible Vagrant provisioner
- `solo.json`: Chef node attributes and run list - will be replaced by Ansible inventory variables
- `solo.rb`: Chef configuration file - will be replaced by ansible.cfg
- `vagrant-provision.sh`: Shell script for Chef provisioning in Vagrant - will be replaced by Ansible playbook

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package module
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package module
- **Python 3**: Use Ansible's package module to install Python dependencies
- **PostgreSQL**: Use Ansible's postgresql_* modules for database management

### Security Considerations

- **SSL Certificate Management**: The current setup generates self-signed certificates; migrate to Ansible crypto modules
  - Migration approach: Use ansible.builtin.openssl_* modules for certificate generation
  
- **Firewall Configuration (UFW)**: Current setup configures UFW firewall rules
  - Migration approach: Use ansible.posix.ufw module for firewall management
  
- **Fail2ban Configuration**: Current setup installs and configures fail2ban
  - Migration approach: Use community.general.fail2ban module or template module for configuration
  
- **SSH Hardening**: Current setup disables root login and password authentication
  - Migration approach: Use ansible.posix.sshd_config module
  
- **Sysctl Security Settings**: Current setup applies sysctl security configurations
  - Migration approach: Use ansible.posix.sysctl module
  
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL password is hardcoded in the fastapi-tutorial cookbook (`fastapi_password`)
  - Migrate to Ansible Vault for secure credential storage

### Technical Challenges

- **Multi-site Nginx Configuration**: The current setup dynamically generates Nginx site configurations based on node attributes
  - Mitigation: Use Ansible templates with variable loops to generate site configurations
  
- **SSL Certificate Generation**: The current setup generates self-signed certificates for each site
  - Mitigation: Use Ansible's openssl_* modules with loops for certificate generation
  
- **Redis Configuration Patching**: The current setup uses a Ruby block to modify Redis configuration files
  - Mitigation: Use Ansible's lineinfile or template module with proper configuration parameters
  
- **Service Orchestration**: The current setup manages service dependencies and notifications
  - Mitigation: Use Ansible handlers and meta dependencies to ensure proper service restart ordering

### Migration Order

1. **nginx-multisite cookbook** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation and configuration
   - Add security hardening (fail2ban, ufw, sysctl)
   - Implement SSL certificate generation
   - Configure virtual hosts

2. **cache cookbook** (low complexity, standalone service)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper service management

3. **fastapi-tutorial cookbook** (high complexity, application deployment)
   - Implement PostgreSQL database setup
   - Configure Python environment and dependencies
   - Deploy application code from Git
   - Set up systemd service

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions
2. Self-signed certificates are acceptable for the migrated solution (not using Let's Encrypt or other CA)
3. The current security configurations are appropriate and should be maintained in the Ansible version
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current hardcoded passwords will be replaced with Ansible Vault secured variables
6. The Vagrant development environment should be preserved with equivalent functionality
7. No changes to the application architecture or deployment model are required