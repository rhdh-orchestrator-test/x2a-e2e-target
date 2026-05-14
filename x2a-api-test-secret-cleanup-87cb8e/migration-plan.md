# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup with three main cookbooks: nginx-multisite, cache, and fastapi-tutorial. The migration to Ansible will involve converting Chef recipes, templates, and attributes to Ansible roles, templates, and variables. The estimated timeline for migration is 2-3 weeks, with moderate complexity due to the interdependencies between components and security configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and fail2ban/ufw firewall setup
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
    - Key Features: Python virtual environment, Git repository deployment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4)
- `Vagrantfile`: Defines a Fedora 42 VM with port forwarding (80→8080, 443→8443) and rsync folder sync
- `solo.json`: Defines the run list and configuration attributes for nginx sites and security settings
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Bash script to install Chef and run the cookbooks in the Vagrant environment

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development/testing

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks
- **PostgreSQL**: Replace with Ansible postgresql_* modules or community.postgresql collection

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated in the nginx-multisite cookbook
  - Migration approach: Use Ansible's openssl_* modules to generate certificates

- **Firewall Configuration**: 
  - UFW is configured in the security.rb recipe
  - Migration approach: Use Ansible's ufw module to configure firewall rules

- **Fail2ban Setup**: 
  - Configured in the security.rb recipe
  - Migration approach: Use Ansible's template module to configure fail2ban

- **SSH Hardening**: 
  - Root login and password authentication disabled
  - Migration approach: Use Ansible's lineinfile or template module to configure SSH

- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook
  - Migration approach: Use Ansible Vault to encrypt sensitive values

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - The nginx-multisite cookbook dynamically creates site configurations based on attributes
  - Mitigation: Create Ansible templates with loops to generate site configurations

- **SSL Certificate Generation**: 
  - Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's openssl_* modules with proper idempotency checks

- **Service Dependencies**: 
  - FastAPI application depends on PostgreSQL
  - Mitigation: Use Ansible's meta dependencies and handlers to ensure proper ordering

- **Firewall Configuration**: 
  - Multiple firewall rules with idempotency checks
  - Mitigation: Use Ansible's ufw module with proper state management

### Migration Order

1. **cache** (Priority 1 - low risk, foundational service)
   - Simple configuration of Memcached and Redis
   - Few dependencies on other components

2. **nginx-multisite** (Priority 2 - moderate complexity)
   - Core web server configuration
   - Security hardening components
   - SSL certificate generation

3. **fastapi-tutorial** (Priority 3 - highest complexity)
   - Depends on PostgreSQL
   - Involves application deployment, database setup, and service configuration

### Assumptions

1. The target environment will continue to be Fedora 42 as specified in the Vagrantfile
2. The same security requirements (fail2ban, ufw, SSH hardening) will be maintained
3. Self-signed certificates are acceptable for the migrated solution
4. The FastAPI application source code will remain available at the specified Git repository
5. The current Redis and PostgreSQL passwords are not production values and can be replaced
6. The current directory structure in the target environment (/opt/fastapi-tutorial, /etc/ssl/certs, etc.) should be maintained
7. The Vagrant development environment should continue to work with the Ansible solution
8. Port forwarding requirements (80→8080, 443→8443) will remain the same