# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server setup with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible is estimated to be of medium complexity, with an approximate timeline of 2-3 weeks for a complete migration, including testing and validation.

The repository consists of three main Chef cookbooks that need to be migrated to Ansible roles:
1. nginx-multisite: Configures Nginx with multiple SSL-enabled virtual hosts
2. cache: Sets up Memcached and Redis caching services
3. fastapi-tutorial: Deploys a FastAPI application with PostgreSQL database

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw)

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

- `Berksfile`: Manages cookbook dependencies, including external cookbooks from Chef Supermarket (nginx, memcached, redisio)
- `solo.json`: Contains node configuration including the run list and attribute values for Nginx sites and security settings
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `Vagrantfile`: Defines a Vagrant VM for development and testing with port forwarding and network configuration
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef Solo

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in Vagrant development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks with custom configuration

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration approach: Use Ansible's openssl_* modules or community.crypto collection

- **Firewall Configuration**: 
  - UFW is configured with default deny and specific allow rules
  - Migration approach: Use Ansible's ufw module or firewalld module depending on target OS

- **Fail2ban Configuration**: 
  - Fail2ban is installed and configured for SSH and web services
  - Migration approach: Use Ansible's template module with fail2ban configuration templates

- **SSH Hardening**: 
  - Root login disabled and password authentication disabled
  - Migration approach: Use Ansible's lineinfile module or template module for sshd_config

- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook ('redis_secure_password_123')
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook
  - Migration approach: Use Ansible Vault for storing sensitive credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current setup dynamically creates Nginx site configurations based on node attributes
  - Mitigation: Use Ansible's with_items/loop to iterate through site configurations and template module to create site configs

- **SSL Certificate Generation**: 
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's openssl_* modules to generate certificates or integrate with Let's Encrypt via community modules

- **Service Orchestration**: 
  - Description: Services have dependencies (e.g., FastAPI depends on PostgreSQL)
  - Mitigation: Use Ansible handlers and meta dependencies to ensure proper service start order

- **Configuration Templating**: 
  - Description: Multiple configuration templates are used for Nginx, security settings, etc.
  - Mitigation: Convert ERB templates to Jinja2 templates for Ansible

### Migration Order

1. **cache role** (low risk, moderate value)
   - Simple configuration of Memcached and Redis services
   - Few dependencies on other components

2. **nginx-multisite role** (moderate complexity, high value)
   - Core web server functionality
   - Includes security configurations that should be established early

3. **fastapi-tutorial role** (high complexity, depends on others)
   - Depends on PostgreSQL database
   - Requires proper web server configuration to be accessible

### Assumptions

1. The target environment will continue to support either Ubuntu (>= 18.04) or CentOS (>= 7.0)
2. Self-signed certificates are acceptable for development/testing, but production may require proper certificates
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain accessible
4. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate for the target environment
5. Redis and Memcached configurations don't require significant tuning beyond what's currently specified
6. The PostgreSQL database will be local to the application server (not using a remote database service)
7. The current Vagrant setup is primarily for development/testing and may not reflect production deployment