# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Scope**: 3 Chef cookbooks with external dependencies
**Complexity**: Medium
**Estimated Timeline**: 3-4 weeks

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, fail2ban integration, UFW firewall configuration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file listing both local cookbooks and external dependencies from Chef Supermarket
  - Migration considerations: Dependencies need to be mapped to Ansible Galaxy roles or custom roles
  
- `solo.json`: Chef configuration file containing the run list and node attributes
  - Migration considerations: Convert to Ansible group_vars or host_vars

- `solo.rb`: Chef configuration file specifying paths and log settings
  - Migration considerations: Replace with Ansible configuration settings

- `Vagrantfile`: Defines the development VM configuration using Vagrant
  - Migration considerations: Update provisioner from Chef to Ansible

- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
  - Migration considerations: Replace with Ansible provisioning commands

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible community.general.nginx_vhost or geerlingguy.nginx role
- **memcached (~> 6.0)**: Replace with geerlingguy.memcached role
- **redisio (~> 7.2.4)**: Replace with geerlingguy.redis role

### Security Considerations

- **SSL Certificate Management**: 
  - Current implementation generates self-signed certificates
  - Migration approach: Use Ansible's openssl_* modules for certificate generation or community.crypto collection

- **Firewall Configuration**: 
  - Current implementation uses UFW
  - Migration approach: Use Ansible's ufw module or firewalld module depending on target OS

- **Fail2ban Integration**: 
  - Current implementation configures fail2ban for intrusion prevention
  - Migration approach: Use Ansible's template module to configure fail2ban or use community.general.fail2ban module

- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook
  - Migration approach: Use Ansible Vault to encrypt sensitive values

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation dynamically generates Nginx site configurations based on node attributes
  - Mitigation strategy: Use Ansible templates with loops to generate site configurations from variables

- **Redis Configuration Patching**: 
  - Description: The cache cookbook includes a ruby_block to modify Redis configuration files after they're created
  - Mitigation strategy: Create a custom Redis configuration template in Ansible that includes the correct settings initially

- **Service Orchestration**: 
  - Description: The current implementation manages service dependencies and notifications
  - Mitigation strategy: Use Ansible handlers and meta dependencies to ensure proper service restart ordering

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Create base Nginx role
   - Implement SSL certificate generation
   - Configure security settings
   - Set up virtual hosts

2. **cache** (low complexity, standalone services)
   - Set up Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, application deployment)
   - Set up PostgreSQL database
   - Deploy Python application
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora-based systems (specifically Fedora 42 as indicated in the Vagrantfile)
2. Self-signed SSL certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or other CA)
3. The current security configurations (fail2ban, UFW, SSH hardening) are required in the migrated solution
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The Redis configuration workaround in the cache cookbook is addressing a specific issue that may need investigation during migration
6. The current Vagrant development workflow should be preserved with Ansible
7. No CI/CD pipeline integration is required as none is present in the current implementation