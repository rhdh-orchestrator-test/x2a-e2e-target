# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This migration plan outlines the process of converting a Chef-based infrastructure to Ansible. The repository contains three Chef cookbooks that manage a multi-site Nginx web server, caching services (Redis and Memcached), and a FastAPI Python application with PostgreSQL. The estimated complexity is moderate, with an estimated timeline of 3-4 weeks for complete migration, including testing and documentation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and proper SSL configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, fail2ban integration, UFW firewall configuration

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

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef configuration file containing the run list and node attributes
- `solo.rb`: Chef configuration file specifying cookbook paths and log settings
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration file for local development environment using Fedora 42

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or local development

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or service module
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or service module
- **Python 3**: Use Ansible's package module to install Python dependencies
- **PostgreSQL**: Use Ansible's postgresql_* modules for database management

### Security Considerations

- **SSL Certificate Management**: 
  - Current implementation generates self-signed certificates
  - Migration approach: Use Ansible's openssl_* modules or community.crypto collection

- **Firewall Configuration**: 
  - Current implementation uses UFW
  - Migration approach: Use Ansible's ufw module or firewalld module depending on target OS

- **Fail2ban Integration**: 
  - Current implementation configures fail2ban for intrusion prevention
  - Migration approach: Use Ansible's template module to configure fail2ban

- **SSH Hardening**: 
  - Current implementation disables root login and password authentication
  - Migration approach: Use Ansible's lineinfile or template module to configure SSH

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe
  - PostgreSQL credentials are hardcoded in the recipe
  - Migration approach: Use Ansible Vault for storing sensitive information

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Maintaining the dynamic generation of multiple virtual hosts with SSL
  - Mitigation: Use Ansible's template module with Jinja2 templates to generate site configurations

- **SSL Certificate Generation**: 
  - Challenge: Ensuring proper permissions and security for SSL certificates
  - Mitigation: Use Ansible's file module to set proper permissions and community.crypto collection for certificate generation

- **Service Dependencies**: 
  - Challenge: Ensuring proper service startup order (e.g., PostgreSQL before FastAPI)
  - Mitigation: Use Ansible's meta: flush_handlers and proper handler notification

- **Redis Configuration Hack**: 
  - Challenge: The current implementation uses a ruby_block to modify Redis configuration
  - Mitigation: Create a proper Jinja2 template for Redis configuration

### Migration Order

1. **cache cookbook** (low risk, moderate value)
   - Simple configuration of Memcached and Redis services
   - Good starting point to establish patterns for service management

2. **nginx-multisite cookbook** (moderate complexity, high value)
   - Core infrastructure component with security implications
   - Requires careful testing of SSL configuration and security settings

3. **fastapi-tutorial cookbook** (high complexity, dependencies)
   - Depends on PostgreSQL and proper application deployment
   - Requires testing of application functionality

### Assumptions

1. The target environment will continue to be Fedora-based or compatible with the supported operating systems (Ubuntu 18.04+, CentOS 7+)
2. Self-signed certificates are acceptable for the migrated solution (production would likely require proper certificates)
3. The current security configurations (fail2ban, UFW, SSH hardening) are required in the migrated solution
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current Redis and PostgreSQL passwords are not production values and can be replaced
6. The current directory structure in the target environment (/opt/fastapi-tutorial, /var/www/*, etc.) should be maintained
7. The Vagrant development environment should be preserved for testing