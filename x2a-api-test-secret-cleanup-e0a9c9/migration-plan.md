# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 3-4 weeks, with moderate complexity due to the multi-site configuration and security considerations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site-specific configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), custom Nginx configurations

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef run list and configuration data including site configurations and security settings
- `solo.rb`: Chef Solo configuration file defining cookbook paths and log settings
- `Vagrantfile`: Defines a Fedora 42 VM for development/testing with port forwarding and network settings
- `vagrant-provision.sh`: Shell script to install Chef and run the cookbooks in the Vagrant environment

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with development environment using Fedora 42
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or dedicated tasks for Redis installation and configuration

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW; migration should use Ansible's `ufw` module or `firewalld` module depending on target OS
- **Fail2ban Setup**: Migrate fail2ban configuration using Ansible's package and template modules
- **SSH Hardening**: Preserve SSH security settings (disable root login, password authentication) using Ansible's `lineinfile` or templates
- **SSL Certificate Management**: Self-signed certificate generation should be migrated using Ansible's `openssl_*` modules
- **Vault/secrets management**: 
  - Redis password in cache cookbook (hardcoded as 'redis_secure_password_123')
  - PostgreSQL credentials in fastapi-tutorial cookbook (hardcoded as 'fastapi_password')
  - These should be migrated to Ansible Vault or another secrets management solution

### Technical Challenges

- **Multi-site Configuration**: The dynamic generation of multiple Nginx sites will require careful templating in Ansible
- **Service Orchestration**: Ensuring proper service restart notifications when configurations change
- **PostgreSQL User/DB Creation**: Ensuring idempotent database operations in Ansible
- **Python Environment Management**: Properly setting up virtual environments and dependencies
- **SSL Certificate Management**: Generating and managing SSL certificates across multiple domains

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation and configuration
   - Add security components (fail2ban, firewall)
   - Implement SSL certificate generation
   - Configure multi-site setup

2. **cache** (low complexity, standalone service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on database)
   - Set up PostgreSQL database and user
   - Deploy application from Git
   - Configure Python environment and dependencies
   - Set up systemd service

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based systems
2. Self-signed certificates are acceptable for the migrated environment (production would likely use Let's Encrypt or other CA)
3. The current hardcoded credentials will be replaced with more secure solutions
4. The Vagrant development environment will be maintained but converted to use Ansible provisioner
5. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
6. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate for the target environment
7. The multi-site configuration with test.cluster.local, ci.cluster.local, and status.cluster.local domains will be maintained
8. Redis and Memcached configurations don't require significant changes beyond what's in the current cookbooks