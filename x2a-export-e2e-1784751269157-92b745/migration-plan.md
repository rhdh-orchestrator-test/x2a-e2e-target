# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site web application environment with FastAPI backend, Nginx web server, and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- Well-structured Chef cookbooks with clear separation of concerns
- Standard web application stack with common components
- Some security configurations that need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Contains node attributes and run list - will be replaced by Ansible inventory variables
- `solo.rb`: Chef configuration file - will be replaced by ansible.cfg
- `Vagrantfile`: VM configuration for development/testing - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisioning script for Vagrant - will be replaced by Ansible playbook calls

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for development
  - Migration should maintain the same security level or improve with Let's Encrypt integration
  - Certificate paths and permissions must be preserved

- **Firewall Configuration**: 
  - UFW rules need to be migrated to equivalent Ansible UFW module tasks
  - Default deny policy with specific allow rules for SSH, HTTP, HTTPS

- **SSH Hardening**:
  - Root login disabled
  - Password authentication disabled
  - These settings should be preserved in the Ansible configuration

- **Fail2ban Integration**:
  - Current configuration protects against brute force attacks
  - Ansible should maintain the same protection level

- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook
  - Migration should move these to Ansible Vault or another secrets management solution

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - The current implementation uses templates to generate site configurations
  - Ansible will need equivalent template functionality with proper variable substitution

- **Service Orchestration**: 
  - The current setup has interdependent services (Nginx, FastAPI, PostgreSQL)
  - Ansible playbook ordering and handlers will need to maintain these dependencies

- **SSL Certificate Generation**:
  - Self-signed certificates are generated with OpenSSL commands
  - Ansible has modules for this but the implementation details differ

- **Database Initialization**:
  - PostgreSQL database and user creation is done via shell commands
  - Ansible has dedicated modules that should be used instead

### Migration Order

1. **cache cookbook** (Low complexity, standalone functionality)
   - Create Ansible roles for memcached and redis
   - Implement secure password management with Ansible Vault

2. **fastapi-tutorial cookbook** (Medium complexity)
   - Create Ansible role for Python application deployment
   - Implement PostgreSQL configuration using Ansible modules
   - Configure systemd service using Ansible systemd module

3. **nginx-multisite cookbook** (High complexity)
   - Create Ansible role for Nginx configuration
   - Implement SSL certificate generation
   - Configure security features (fail2ban, UFW)
   - Set up multi-site configuration

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions.
2. The same directory structure for web content will be maintained.
3. Self-signed certificates are acceptable for the migrated solution (or Let's Encrypt could be implemented as an enhancement).
4. The FastAPI application source will continue to be available at the same Git repository.
5. The same security policies (SSH hardening, firewall rules) should be maintained.
6. Redis and PostgreSQL passwords will need to be securely managed in the new solution.
7. The Vagrant development environment should be preserved for testing the Ansible solution.