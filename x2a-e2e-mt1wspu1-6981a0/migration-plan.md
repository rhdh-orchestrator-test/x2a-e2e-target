# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- No custom resources or complex Chef-specific patterns
- Standard infrastructure components (Nginx, FastAPI, Redis, Memcached)
- Security configurations that need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (both local and from Chef Supermarket)
  - Migration: Replace with Ansible Galaxy requirements.yml
  
- `solo.json`: Contains node attributes and run list
  - Migration: Convert to Ansible group_vars or host_vars

- `solo.rb`: Chef Solo configuration
  - Migration: Replace with ansible.cfg

- `Vagrantfile`: Defines development VM for testing
  - Migration: Update to use Ansible provisioner instead of Chef

- `vagrant-provision.sh`: Script to install Chef and run cookbooks
  - Migration: Replace with Ansible provisioning commands

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Libvirt (from Vagrantfile)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package installation

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for development
  - Migration approach: Use Ansible's openssl_* modules or community.crypto collection

- **Firewall Configuration**: 
  - UFW is configured with specific rules
  - Migration approach: Use Ansible's ufw module or firewalld for Fedora

- **SSH Hardening**:
  - Root login disabled
  - Password authentication disabled
  - Migration approach: Use Ansible's lineinfile or template module with the openssh_server role

- **System Hardening**:
  - Sysctl security parameters
  - Migration approach: Use Ansible's sysctl module

- **Fail2ban Configuration**:
  - Custom jail configuration
  - Migration approach: Use Ansible's template module or community.general.fail2ban module

- **Vault/secrets management**:
  - Hardcoded credentials in attributes and recipes:
    - PostgreSQL user/password in fastapi-tutorial/recipes/default.rb
    - Redis password in cache/recipes/default.rb
  - Migration approach: Use Ansible Vault for all credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Preserving the dynamic site generation based on attributes
  - Mitigation: Use Ansible's with_items/loop constructs with templates

- **Service Dependencies**: 
  - Challenge: Ensuring proper ordering of service installation and configuration
  - Mitigation: Use Ansible's handlers and meta dependencies between roles

- **SSL Certificate Generation**: 
  - Challenge: Replicating the self-signed certificate generation logic
  - Mitigation: Use Ansible's openssl_* modules with proper conditionals

- **Database Initialization**: 
  - Challenge: PostgreSQL user and database creation
  - Mitigation: Use Ansible's postgresql_* modules from the community.postgresql collection

### Migration Order

1. **cache** (Priority 1 - low risk, standalone services)
   - Simple Redis and Memcached configuration
   - Few dependencies on other components

2. **nginx-multisite** (Priority 2 - moderate complexity)
   - Core web server configuration
   - Security hardening components
   - SSL certificate generation

3. **fastapi-tutorial** (Priority 3 - higher complexity)
   - Application deployment
   - Database configuration
   - Systemd service setup
   - Depends on proper web server configuration

### Assumptions

1. The target environment will continue to use Fedora or similar Linux distributions.
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or other CA).
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
4. The current security configurations (fail2ban, UFW, SSH hardening) are appropriate for the target environment.
5. The PostgreSQL and Redis passwords in the code are development credentials that will be replaced with proper secrets management in production.
6. The Vagrant development environment will be maintained for testing the Ansible playbooks.
7. The current directory structure with separate modules will be preserved in the Ansible roles organization.