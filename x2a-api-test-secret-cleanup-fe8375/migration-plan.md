# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, configuration templates, and security settings. Based on the complexity and scope, this migration is estimated to require 3-4 weeks with a team of 2 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, fail2ban integration, UFW firewall rules

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

- `Berksfile`: Dependency management file listing cookbook dependencies (nginx, memcached, redisio)
- `solo.json`: Chef configuration file with run list and node attributes
- `solo.rb`: Chef configuration file for Chef Solo
- `Vagrantfile`: Defines development VM using Fedora 42 with libvirt provider
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)
- **PostgreSQL**: Replace with Ansible PostgreSQL role (e.g., geerlingguy.postgresql)
- **Python/venv**: Replace with Ansible Python modules (pip, virtualenv)

### Security Considerations

- **SSL Certificate Management**: 
  - Migration approach: Use Ansible crypto modules for self-signed certificates or integrate with ansible-role-certbot for Let's Encrypt
  - Current implementation generates self-signed certificates for each site

- **Firewall Configuration**: 
  - Migration approach: Use Ansible UFW module to configure firewall rules
  - Current implementation enables UFW with rules for SSH, HTTP, and HTTPS

- **fail2ban Integration**: 
  - Migration approach: Use Ansible to install and configure fail2ban
  - Current implementation installs fail2ban with a custom jail configuration

- **SSH Hardening**: 
  - Migration approach: Use Ansible to configure SSH security settings
  - Current implementation disables root login and password authentication

- **Vault/secrets management**:
  - Redis password: Hardcoded in cache/recipes/default.rb as 'redis_secure_password_123'
  - PostgreSQL credentials: Hardcoded in fastapi-tutorial/recipes/default.rb (user: fastapi, password: fastapi_password)
  - Total credentials detected: 2 sets of database credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation dynamically generates Nginx site configurations based on node attributes
  - Mitigation strategy: Use Ansible templates with loops to generate site configurations from variables

- **SSL Certificate Generation**: 
  - Description: Self-signed certificates are generated for each site
  - Mitigation strategy: Use Ansible crypto modules or integrate with certbot for Let's Encrypt certificates

- **Service Orchestration**: 
  - Description: Multiple interdependent services (Nginx, Redis, Memcached, PostgreSQL, FastAPI)
  - Mitigation strategy: Use Ansible handlers and dependencies to ensure proper service ordering

- **Security Hardening**: 
  - Description: Comprehensive security measures across multiple components
  - Mitigation strategy: Leverage existing Ansible security roles or create dedicated security tasks

### Migration Order

1. **cache cookbook** (low risk, moderate value)
   - Simple configuration of Memcached and Redis
   - Few dependencies and templates

2. **nginx-multisite cookbook** (moderate complexity, high value)
   - Core web server functionality
   - Multiple templates and security configurations
   - SSL certificate generation

3. **fastapi-tutorial cookbook** (high complexity, dependencies)
   - Depends on PostgreSQL
   - Involves Git, Python, and systemd configuration
   - Database initialization and credentials management

### Assumptions

1. The target environment will continue to be Fedora-based systems (specifically Fedora 42 as indicated in the Vagrantfile)
2. Self-signed certificates are acceptable for development/testing (production would likely use proper certificates)
3. The security requirements will remain the same (fail2ban, UFW, SSH hardening)
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current Redis and PostgreSQL passwords are for development only and will be replaced with secure passwords in production
6. The Nginx sites configuration (test.cluster.local, ci.cluster.local, status.cluster.local) will remain the same
7. The current directory structure in the target system (/opt/server/*, /var/www/*) will be maintained