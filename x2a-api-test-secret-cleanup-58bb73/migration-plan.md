# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their recipes, templates, attributes, and custom resources to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:**
- Medium complexity due to multiple interconnected services
- Security configurations that need careful migration
- Custom resource handling (lineinfile resource)
- SSL certificate management

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server configured to host multiple SSL-enabled virtual hosts with security hardening
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall), custom site templates

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, service management

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file listing cookbook dependencies (both local and external from Chef Supermarket)
- `Vagrantfile`: Defines the development VM using Fedora 42 with port forwarding and resource allocation
- `solo.json`: Chef Solo configuration with run list and node attributes
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in the Vagrant development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_config module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks with custom configuration

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each virtual host
  - Migration approach: Use Ansible's openssl_* modules for certificate generation

- **Firewall Configuration**: 
  - UFW is configured to allow only SSH, HTTP, and HTTPS
  - Migration approach: Use Ansible's ufw module or firewalld module depending on target OS

- **Fail2ban Integration**: 
  - Configured for SSH and web services
  - Migration approach: Create Ansible tasks to install and configure fail2ban

- **SSH Hardening**: 
  - Root login disabled
  - Password authentication disabled
  - Migration approach: Use Ansible's lineinfile module or template module for sshd_config

- **Vault/secrets management**:
  - Redis password hardcoded in recipe: "redis_secure_password_123"
  - PostgreSQL credentials hardcoded in recipe: "fastapi:fastapi_password"
  - Migration approach: Move credentials to Ansible Vault

### Technical Challenges

- **Custom Resource Migration**: 
  - The nginx-multisite cookbook includes a custom `lineinfile` resource
  - Migration approach: Replace with Ansible's native lineinfile module

- **Multi-site Configuration**: 
  - Dynamic creation of multiple virtual hosts based on node attributes
  - Migration approach: Use Ansible loops with templates to create site configurations

- **Service Orchestration**: 
  - Interdependent services (PostgreSQL, FastAPI, Nginx)
  - Migration approach: Use Ansible handlers and proper task ordering with dependencies

- **SSL Certificate Generation**: 
  - Self-signed certificates generated on-the-fly
  - Migration approach: Use Ansible's openssl_* modules with proper idempotency checks

### Migration Order

1. **cache** (Priority 1 - Low complexity)
   - Simple package installation and configuration
   - Few dependencies on other modules

2. **fastapi-tutorial** (Priority 2 - Medium complexity)
   - Application deployment with database
   - Requires database setup before application deployment

3. **nginx-multisite** (Priority 3 - Higher complexity)
   - Complex configuration with multiple sites
   - Security hardening
   - SSL certificate management
   - Depends on applications being available

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based systems
2. Self-signed certificates are acceptable for the migrated solution (not using Let's Encrypt or other CA)
3. The same directory structure for web content will be maintained
4. The same security policies (SSH hardening, firewall rules) will be applied
5. Redis and PostgreSQL passwords will be managed more securely in the Ansible solution
6. The Vagrant development environment will be maintained but converted to use Ansible provisioner
7. No changes to the FastAPI application codebase are required
8. The migration will not involve containerization of the services