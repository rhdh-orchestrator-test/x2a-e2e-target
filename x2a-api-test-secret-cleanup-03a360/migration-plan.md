# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks. The estimated timeline for migration is 2-3 weeks, with moderate complexity due to the interdependencies between components and security configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and proper SSL certificate management
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup, security headers, fail2ban integration, UFW firewall configuration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python web application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies (nginx, memcached, redisio)
- `solo.json`: Chef run list and node attributes configuration, defines nginx sites and security settings
- `solo.rb`: Chef Solo configuration file, defines cookbook paths and log settings
- `Vagrantfile`: Defines development VM using Fedora 42, with port forwarding and network configuration
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development/testing

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or collection (e.g., `geerlingguy.nginx`)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., `geerlingguy.memcached`)
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role (e.g., `geerlingguy.redis` or `DavidWittman.redis`)

### Security Considerations

- **SSL/TLS Configuration**: Migrate self-signed certificate generation for development environments
  - Migration approach: Use Ansible's `openssl_*` modules to generate certificates
  
- **Firewall Rules**: Convert UFW rules to appropriate firewall module
  - Migration approach: Use Ansible's `ufw` module for Ubuntu or `firewalld` module for Fedora/RHEL

- **fail2ban Configuration**: Migrate fail2ban setup
  - Migration approach: Create Ansible tasks using the `template` module for fail2ban configuration

- **SSH Hardening**: Migrate SSH security settings
  - Migration approach: Use Ansible's `lineinfile` module or dedicated SSH role

- **Vault/secrets management**:
  - Redis password in cache cookbook (hardcoded as 'redis_secure_password_123')
  - PostgreSQL credentials in fastapi-tutorial cookbook (hardcoded as 'fastapi_password')
  - Migration approach: Use Ansible Vault for storing sensitive credentials

### Technical Challenges

- **Multi-site Configuration**: The dynamic generation of Nginx site configurations based on node attributes
  - Mitigation: Use Ansible's template module with loops to generate site configurations

- **Service Dependencies**: Ensuring proper ordering of service installation and configuration
  - Mitigation: Use Ansible's handlers and meta dependencies to manage service relationships

- **SSL Certificate Management**: Proper handling of SSL certificates and private keys
  - Mitigation: Use Ansible's `openssl_*` modules and ensure proper permissions

- **Database Configuration**: PostgreSQL user and database creation
  - Mitigation: Use Ansible's PostgreSQL modules for idempotent database management

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Create base Nginx role with templates
   - Implement security configurations
   - Set up SSL certificate generation
   - Configure virtual hosts

2. **cache** (low complexity, standalone services)
   - Set up Memcached configuration
   - Configure Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on database)
   - Set up PostgreSQL database
   - Deploy application from Git
   - Configure Python environment
   - Set up systemd service

### Assumptions

1. The target environment will continue to be Fedora-based systems (Fedora 42 as specified in Vagrantfile)
2. Self-signed certificates are acceptable for development environments
3. The same security hardening measures are required in the Ansible implementation
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current hardcoded credentials will be replaced with Ansible Vault secured variables
6. The same port configurations and networking setup will be maintained
7. The directory structure for deployed applications will remain the same
8. No additional features beyond what's in the current Chef implementation are required