# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, configuration templates, and security settings. Based on the complexity and scope, this migration is estimated to require 3-4 weeks with 1-2 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW

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

- `Berksfile`: Dependency management for Chef cookbooks, lists both local and external dependencies
- `Policyfile.rb`: Chef policy file defining the run list and cookbook dependencies
- `Vagrantfile`: Defines development VM for testing with Fedora 42
- `solo.json`: Configuration data for Chef solo, contains site configurations and security settings
- `solo.rb`: Chef solo configuration file
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) based on cookbook metadata, with development environment using Fedora 42
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role or dedicated tasks for Redis installation and configuration
- **ssl_certificate (~> 2.1)**: Replace with Ansible's openssl_* modules for certificate management

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW; migrate to Ansible's `ufw` module or `firewalld` module depending on target OS
- **fail2ban Setup**: Migrate fail2ban configuration to Ansible tasks using the `template` module
- **SSH Hardening**: Preserve SSH security settings (root login disabled, password authentication disabled) using Ansible's `lineinfile` or `template` modules
- **SSL Management**: Ensure secure handling of SSL certificates and private keys with appropriate permissions
- **Redis Authentication**: Maintain Redis password authentication in Ansible configuration
- **PostgreSQL Security**: Preserve database user credentials and access controls

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple site configurations will require careful templating in Ansible
- **SSL Certificate Generation**: Self-signed certificate generation logic needs to be replicated in Ansible
- **System Hardening**: Security configurations across multiple services need to be maintained
- **Service Dependencies**: Ensure proper ordering of service installations and configurations (e.g., PostgreSQL before FastAPI application)
- **Python Environment Management**: Virtual environment setup and dependency installation needs careful handling in Ansible

### Migration Order

1. **cache cookbook** (Low complexity, foundational service)
   - Basic package installation and configuration
   - Minimal dependencies on other services

2. **nginx-multisite cookbook** (Medium complexity, core infrastructure)
   - Base Nginx installation and configuration
   - SSL certificate generation
   - Site configuration
   - Security hardening

3. **fastapi-tutorial cookbook** (High complexity, application layer)
   - Depends on PostgreSQL database
   - Requires Python environment setup
   - Involves git repository cloning and application configuration

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS as specified in the cookbook metadata
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or other CA)
3. The Redis password "redis_secure_password_123" will need to be managed securely in Ansible (consider using Ansible Vault)
4. The PostgreSQL credentials (fastapi/fastapi_password) will need to be managed securely
5. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
6. The Vagrant development environment will be maintained for testing the Ansible playbooks
7. The current directory structure with three separate sites will be preserved
8. Security hardening measures (fail2ban, UFW, SSH configuration) are required in the Ansible implementation