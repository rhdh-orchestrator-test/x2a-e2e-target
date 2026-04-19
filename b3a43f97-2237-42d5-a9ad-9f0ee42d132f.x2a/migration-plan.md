# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This migration plan outlines the process of converting a Chef-based infrastructure to Ansible. The repository contains three Chef cookbooks that manage a multi-site Nginx web server, caching services (Redis and Memcached), and a FastAPI Python application with PostgreSQL. The estimated complexity is moderate, with security configurations and multiple service dependencies to consider. The migration timeline is estimated at 3-4 weeks with 1-2 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configurations
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

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef configuration file containing run list and node attributes
- `solo.rb`: Chef configuration file for Chef Solo
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration file for development environment

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role or package installation tasks
- **Python 3 and venv**: Use Ansible pip module for Python dependency management
- **PostgreSQL**: Use Ansible postgresql_* modules or community.postgresql collection

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated in the Chef cookbook
  - Migration approach: Use Ansible's openssl_* modules or community.crypto collection

- **Firewall Configuration (UFW)**:
  - Migration approach: Use Ansible's ufw module to configure firewall rules

- **fail2ban Configuration**:
  - Migration approach: Use Ansible to deploy fail2ban configuration templates

- **SSH Hardening**:
  - Root login disabled and password authentication disabled
  - Migration approach: Use Ansible's lineinfile module or ssh_config module

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe
  - PostgreSQL password is hardcoded in the recipe
  - Migration approach: Use Ansible Vault for storing sensitive credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The Chef cookbook dynamically creates multiple virtual hosts with SSL
  - Mitigation: Use Ansible templates with loops to generate site configurations

- **Service Orchestration**: 
  - Description: Interdependent services (Nginx, PostgreSQL, Redis, FastAPI application)
  - Mitigation: Use Ansible handlers and proper dependency ordering

- **SSL Certificate Generation**:
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's openssl_* modules with proper idempotency checks

- **Database User and Schema Creation**:
  - Description: PostgreSQL database and user creation with proper permissions
  - Mitigation: Use Ansible's postgresql_* modules with proper privilege escalation

### Migration Order

1. **cache cookbook** (low risk, foundational services)
   - Implement Redis and Memcached configuration
   - Secure Redis with password authentication

2. **nginx-multisite cookbook** (moderate complexity)
   - Implement base Nginx configuration
   - Configure SSL certificates
   - Set up virtual hosts
   - Implement security hardening (fail2ban, UFW)

3. **fastapi-tutorial cookbook** (high complexity, dependencies)
   - Set up PostgreSQL database
   - Deploy Python application
   - Configure systemd service
   - Integrate with Nginx

### Assumptions

1. The target environment will continue to be Fedora-based systems (the Vagrantfile specifies Fedora 42)
2. Self-signed certificates are acceptable for the migrated solution (production would likely require proper certificates)
3. The same security hardening measures should be maintained in the Ansible solution
4. The FastAPI application source will continue to be pulled from the same Git repository
5. Redis and Memcached configurations should maintain the same performance characteristics
6. The current directory structure in the target system (/opt/fastapi-tutorial, /etc/ssl paths) should be preserved
7. The migration will not introduce new features but maintain functional equivalence
8. No CI/CD pipeline integration is required as part of the migration
9. The current Vagrant-based development workflow should be preserved