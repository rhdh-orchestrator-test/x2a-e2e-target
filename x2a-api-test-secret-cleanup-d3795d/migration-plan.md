# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This migration plan outlines the process of converting a Chef-based infrastructure to Ansible. The repository contains three Chef cookbooks that manage a multi-site Nginx setup, caching services (Redis and Memcached), and a FastAPI Python application with PostgreSQL. The estimated complexity is moderate, with an estimated timeline of 4-6 weeks for complete migration, including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW), system hardening

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

- `Berksfile`: Dependency management file listing cookbook dependencies (nginx, memcached, redisio)
- `Vagrantfile`: Defines development environment using Fedora 42 with libvirt provider
- `solo.json`: Chef Solo configuration with run list and node attributes
- `solo.rb`: Chef Solo configuration file defining cookbook paths and log settings
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified (appears to be designed for on-premises or local development)

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration approach: Use Ansible's openssl_* modules or community.crypto collection

- **Firewall Configuration**: 
  - UFW is configured to allow only specific ports (SSH, HTTP, HTTPS)
  - Migration approach: Use Ansible's ufw module or firewalld module depending on target OS

- **System Hardening**:
  - Sysctl security parameters are configured
  - Migration approach: Use Ansible's sysctl module

- **SSH Hardening**:
  - Root login disabled
  - Password authentication disabled
  - Migration approach: Use Ansible's lineinfile module or template module for sshd_config

- **Fail2ban Configuration**:
  - Fail2ban is installed and configured
  - Migration approach: Use Ansible's template module for fail2ban configuration

- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook ("redis_secure_password_123")
  - PostgreSQL password is hardcoded in the fastapi-tutorial cookbook ("fastapi_password")
  - Migration approach: Use Ansible Vault for storing sensitive information

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation dynamically creates Nginx site configurations based on node attributes
  - Mitigation: Use Ansible's template module with loops to generate site configurations

- **SSL Certificate Generation**:
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's openssl_* modules to generate certificates or integrate with Let's Encrypt

- **Service Orchestration**:
  - Description: Services have dependencies (FastAPI depends on PostgreSQL)
  - Mitigation: Use Ansible's meta: flush_handlers and proper handler notification to ensure services start in the correct order

- **Custom Resource Migration**:
  - Description: The nginx-multisite cookbook includes a custom resource (lineinfile)
  - Mitigation: Replace with Ansible's native lineinfile module

### Migration Order

1. **cache** (Priority 1 - Low complexity)
   - Simple configuration of Memcached and Redis
   - Few dependencies
   - Good starting point for the migration

2. **nginx-multisite** (Priority 2 - Moderate complexity)
   - Core infrastructure component
   - Multiple templates and configurations
   - Security configurations that other components may depend on

3. **fastapi-tutorial** (Priority 3 - Moderate complexity)
   - Application deployment that depends on properly configured infrastructure
   - Requires database setup and configuration
   - Systemd service configuration

### Assumptions

1. The target environment will continue to be Fedora-based systems (Fedora 42 as specified in the Vagrantfile)
2. The same directory structure for web content will be maintained (/opt/server/*)
3. Self-signed certificates are acceptable (no requirement for Let's Encrypt or commercial certificates)
4. The same security hardening measures will be implemented in Ansible
5. The FastAPI application will continue to be deployed from the same Git repository
6. PostgreSQL and Redis passwords will be managed securely in the new implementation
7. The same virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local) will be maintained
8. The Vagrant development environment will be migrated to use Ansible provisioning instead of Chef