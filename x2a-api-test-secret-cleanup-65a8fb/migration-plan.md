# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This migration plan outlines the process of converting a Chef-based infrastructure to Ansible. The repository contains three Chef cookbooks that manage a multi-site Nginx setup, caching services (Redis and Memcached), and a FastAPI Python application with PostgreSQL. The estimated complexity is moderate, with security configurations and multiple service dependencies to consider. The estimated timeline for migration is 3-4 weeks with 1-2 dedicated engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site-specific configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall), sysctl security settings

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

- `Berksfile`: Dependency management for Chef cookbooks - lists both local and external cookbook dependencies with version constraints
- `solo.json`: Chef run list and node attribute configuration - defines which recipes to run and configuration values
- `solo.rb`: Chef Solo configuration - defines cookbook paths and logging settings
- `Vagrantfile`: Defines development VM configuration using Fedora 42 with port forwarding and resource allocation
- `vagrant-provision.sh`: Bash script to provision the Vagrant VM with Chef and run the cookbooks

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with development environment using Fedora 42
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)
- **PostgreSQL**: Replace with Ansible PostgreSQL role (e.g., geerlingguy.postgresql)
- **Python/FastAPI**: Replace with Ansible Python role for virtualenv and pip management

### Security Considerations

- **SSL Certificate Management**: 
  - Migration approach: Use Ansible's openssl_* modules for certificate generation or community.crypto collection
  - Consider integrating with Ansible Vault for storing private keys

- **Firewall Configuration (UFW)**:
  - Migration approach: Use Ansible's ufw module to manage firewall rules

- **Fail2ban Configuration**:
  - Migration approach: Use Ansible to deploy fail2ban configuration templates

- **SSH Hardening**:
  - Migration approach: Use Ansible's lineinfile or template module to configure sshd_config

- **Vault/secrets management**:
  - Redis password in cache cookbook (hardcoded as 'redis_secure_password_123')
  - PostgreSQL user password in fastapi-tutorial cookbook (hardcoded as 'fastapi_password')
  - Database connection string in .env file for FastAPI application
  - Total credentials detected: 3 hardcoded passwords

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation dynamically generates Nginx site configurations based on node attributes
  - Mitigation: Use Ansible templates with loops to generate site configurations from variables

- **SSL Certificate Generation**:
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's openssl_* modules or community.crypto collection to generate certificates

- **Service Orchestration**:
  - Description: Multiple interdependent services (Nginx, Redis, Memcached, PostgreSQL, FastAPI application)
  - Mitigation: Use Ansible handlers and proper dependency ordering to ensure services are configured and restarted in the correct order

- **Environment-specific Configuration**:
  - Description: The current setup uses Chef attributes for environment-specific configuration
  - Mitigation: Use Ansible group_vars and host_vars to manage environment-specific variables

### Migration Order

1. **cache cookbook** (Priority 1 - low complexity)
   - Simple configuration of Memcached and Redis services
   - Few dependencies on other modules

2. **nginx-multisite cookbook** (Priority 2 - moderate complexity)
   - Core web server configuration with multiple sites
   - Security hardening features
   - SSL certificate generation

3. **fastapi-tutorial cookbook** (Priority 3 - higher complexity)
   - Depends on PostgreSQL database
   - Requires application deployment from Git
   - Involves Python virtual environment setup
   - Requires systemd service configuration

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based distributions
2. Self-signed certificates are acceptable for development, but production may require proper certificates
3. The current security configurations (fail2ban, ufw, SSH hardening) are required in the migrated solution
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current Redis and PostgreSQL passwords are development passwords and will be replaced with proper secrets management in production
6. The Vagrant development environment will be maintained but migrated to use Ansible provisioning
7. No custom Chef resources or libraries are used that would require special handling
8. The current directory structure in the target environment (/opt/fastapi-tutorial, /etc/ssl/certs, etc.) should be preserved