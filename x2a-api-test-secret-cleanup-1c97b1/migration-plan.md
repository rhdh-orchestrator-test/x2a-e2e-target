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
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificates
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
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies.
- `solo.json`: Chef Solo configuration file containing the run list and node attributes.
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings.
- `Vagrantfile`: Defines a Fedora 42 VM with port forwarding and resource allocation.
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef.

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in Vagrant development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)

### Security Considerations

- **Firewall Configuration**: UFW firewall rules need to be migrated to appropriate Ansible firewall modules
  - Migration approach: Use Ansible's `ufw` module to configure firewall rules
  
- **Fail2ban Setup**: Fail2ban configuration needs to be migrated
  - Migration approach: Use Ansible's `template` module to create fail2ban configuration files

- **SSH Hardening**: SSH security configurations need to be maintained
  - Migration approach: Use Ansible's `lineinfile` module or dedicated SSH role to configure SSH daemon

- **Vault/secrets management**:
  - Redis password in cache cookbook (hardcoded as 'redis_secure_password_123')
  - PostgreSQL database credentials in fastapi-tutorial cookbook (hardcoded as 'fastapi_password')
  - Migration approach: Move all credentials to Ansible Vault

- **SSL Certificate Management**: Self-signed certificate generation needs to be migrated
  - Migration approach: Use Ansible's `openssl_certificate` module to generate self-signed certificates

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple virtual hosts based on node attributes
  - Mitigation: Use Ansible loops with templates to generate site configurations

- **Service Orchestration**: Ensuring proper service restart only when configuration changes
  - Mitigation: Use Ansible handlers to restart services only when needed

- **PostgreSQL User and Database Creation**: Ensuring idempotent database operations
  - Mitigation: Use Ansible's postgresql_user and postgresql_db modules instead of shell commands

- **Python Application Deployment**: Managing virtual environments and dependencies
  - Mitigation: Use Ansible's pip module with virtualenv parameter

### Migration Order

1. **nginx-multisite cookbook** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Implement security hardening (fail2ban, firewall)
   - Configure virtual hosts

2. **cache cookbook** (low complexity, standalone services)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial cookbook** (high complexity, application deployment)
   - Set up PostgreSQL database
   - Deploy application code from Git
   - Configure Python environment and dependencies
   - Create systemd service

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based distributions
2. The self-signed certificates are for development only and may be replaced with proper certificates in production
3. The current security configurations (fail2ban, UFW, SSH hardening) are sufficient and should be maintained
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current Redis and PostgreSQL passwords are development passwords and will be replaced with secure passwords in production
6. The Vagrant development environment will be maintained for testing
7. No custom Nginx modules or configurations beyond what's visible in the cookbook are required