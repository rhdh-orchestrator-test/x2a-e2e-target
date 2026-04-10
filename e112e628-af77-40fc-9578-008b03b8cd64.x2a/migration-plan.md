# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx configuration with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 3-4 weeks, with moderate complexity due to the security configurations and multi-site SSL setup.

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

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `Policyfile.rb`: Chef policy file defining the run list and cookbook dependencies
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `solo.json`: Node attributes and run list for Chef Solo
- `Vagrantfile`: Defines a Fedora 42 VM for development and testing
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation and configuration
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package installation and configuration
- **ssl_certificate (~> 2.1)**: Replace with Ansible certificate management modules (openssl_*, crypto_*)

### Security Considerations

- **SSL Certificate Management**: Migration must handle self-signed certificate generation for development environments
- **Firewall Configuration**: UFW rules need to be converted to appropriate firewall modules (ufw or firewalld depending on target OS)
- **fail2ban Configuration**: Configuration needs to be migrated to Ansible fail2ban role or direct configuration
- **SSH Hardening**: SSH security configurations (disabling root login, password authentication) need to be preserved
- **Redis Authentication**: Redis password must be securely managed in Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple site configurations needs careful translation to Ansible templates
- **SSL Certificate Management**: Self-signed certificate generation logic needs to be preserved or enhanced
- **System Hardening**: Security configurations across multiple services need to be maintained
- **Service Dependencies**: Ensuring proper ordering of service installation and configuration (e.g., PostgreSQL before FastAPI app)

### Migration Order

1. **cache cookbook** (Low complexity, standalone services)
   - Implement Memcached configuration
   - Implement Redis with authentication

2. **nginx-multisite cookbook** (Medium complexity, core infrastructure)
   - Basic Nginx installation and configuration
   - SSL certificate generation
   - Multi-site configuration
   - Security hardening (fail2ban, UFW)

3. **fastapi-tutorial cookbook** (High complexity, application deployment)
   - PostgreSQL installation and database setup
   - Python environment configuration
   - Application deployment
   - Systemd service configuration

### Assumptions

1. The target environment will continue to be Fedora/CentOS/Ubuntu based on the current configuration
2. Self-signed certificates are acceptable for development environments
3. The FastAPI application source will continue to be pulled from the same Git repository
4. The Redis password and PostgreSQL credentials will need to be stored securely in Ansible Vault
5. The multi-site configuration pattern will be maintained with the same domain structure
6. The security hardening requirements will remain the same in the new implementation
7. The current Chef attributes structure will map to Ansible variables with minimal restructuring