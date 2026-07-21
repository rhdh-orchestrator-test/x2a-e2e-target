# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup focused on deploying a multi-site Nginx configuration with SSL, security hardening, and a FastAPI application with PostgreSQL and caching services (Redis and Memcached). The migration to Ansible is estimated to be of moderate complexity, with approximately 2-3 weeks of effort required for a complete migration, testing, and documentation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and SSL certificate management
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
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Manages cookbook dependencies, including external dependencies from Chef Supermarket (nginx, memcached, redisio)
- `solo.json`: Contains node configuration including the run list and attributes for Nginx sites, SSL, and security settings
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Defines the development VM using Fedora 42, with port forwarding and network configuration

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development/testing

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks with custom configuration

### Security Considerations

- **Firewall Configuration**: The current setup uses UFW for firewall management, which should be migrated to appropriate Ansible firewall modules (e.g., ansible.posix.firewalld for Fedora)
- **Fail2ban Configuration**: Migrate fail2ban configuration to Ansible tasks
- **SSH Hardening**: Current configuration disables root login and password authentication, which should be preserved in Ansible
- **SSL Certificate Management**: Self-signed certificates are generated for development; consider using ansible.builtin.openssl_* modules or community.crypto collection
- **Secrets Management**: 
  - Redis password is hardcoded in the cache cookbook
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook
  - Consider using Ansible Vault for storing these secrets

### Technical Challenges

- **Multi-site Nginx Configuration**: The current setup dynamically generates Nginx site configurations based on node attributes; this pattern needs to be replicated in Ansible using templates and variables
- **SSL Certificate Management**: Self-signed certificates are generated for each site; this needs to be handled in Ansible
- **Service Dependencies**: The FastAPI application depends on PostgreSQL; ensure proper ordering of tasks in Ansible
- **Redis Configuration Hack**: The current setup includes a Ruby block to modify Redis configuration files after installation; this needs a clean implementation in Ansible

### Migration Order

1. **cache cookbook** (low complexity, standalone)
   - Implement Memcached installation and configuration
   - Implement Redis installation with authentication

2. **nginx-multisite cookbook** (moderate complexity)
   - Implement base Nginx installation
   - Implement security hardening (fail2ban, firewall)
   - Implement SSL certificate generation
   - Implement virtual host configuration

3. **fastapi-tutorial cookbook** (moderate complexity, has dependencies)
   - Implement Python environment setup
   - Implement PostgreSQL installation and configuration
   - Implement application deployment
   - Implement systemd service configuration

### Assumptions

1. The target environment will continue to be Fedora-based, though the cookbooks support Ubuntu and CentOS as well
2. Self-signed certificates are acceptable for the migrated solution (production environments would likely use Let's Encrypt or other CA-signed certificates)
3. The current security configurations (fail2ban, firewall, SSH hardening) are appropriate for the target environment
4. The FastAPI application source code will remain available at the specified Git repository
5. The Redis and Memcached configurations do not require advanced tuning beyond what's currently specified
6. The PostgreSQL database schema is managed by the FastAPI application itself, not by the infrastructure code