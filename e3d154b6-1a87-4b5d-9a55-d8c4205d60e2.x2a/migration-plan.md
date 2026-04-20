# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks, handling external dependencies, and ensuring proper security configurations are maintained.

**Scope**: 3 Chef cookbooks with interdependencies and external cookbook dependencies
**Complexity**: Medium
**Estimated Timeline**: 3-4 weeks

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
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (both local and external from Chef Supermarket)
  - Migration considerations: Replace with Ansible Galaxy requirements.yml
- `solo.json`: Defines the Chef run list and node attributes
  - Migration considerations: Convert to Ansible group_vars or host_vars
- `solo.rb`: Chef configuration file
  - Migration considerations: Replace with ansible.cfg
- `Vagrantfile`: Defines the development VM configuration
  - Migration considerations: Update to use Ansible provisioner instead of Chef
- `vagrant-provision.sh`: Shell script to install Chef and run the cookbooks
  - Migration considerations: Replace with Ansible playbook execution

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or create custom role
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role from Galaxy
- **PostgreSQL**: Use Ansible PostgreSQL role from Galaxy

### Security Considerations

- **SSL Certificate Management**: 
  - Current approach uses self-signed certificates generated with OpenSSL
  - Migration approach: Use Ansible crypto modules for certificate generation or integrate with Let's Encrypt

- **Firewall Configuration**: 
  - Current approach uses UFW with specific rules
  - Migration approach: Use Ansible UFW module or firewalld module depending on target OS

- **Fail2ban Integration**: 
  - Current approach configures fail2ban with custom jail settings
  - Migration approach: Use Ansible to deploy fail2ban configuration templates

- **SSH Hardening**: 
  - Current approach disables root login and password authentication
  - Migration approach: Use Ansible to configure SSH daemon with secure settings

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe
  - PostgreSQL credentials are hardcoded in the recipe
  - Migration approach: Use Ansible Vault to encrypt sensitive values

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation dynamically generates Nginx site configurations based on node attributes
  - Mitigation strategy: Use Ansible templates with loops to generate site configurations from variables

- **Redis Configuration Workaround**: 
  - Description: The current implementation includes a ruby_block to modify Redis configuration files after they're created
  - Mitigation strategy: Create proper Ansible templates for Redis configuration without needing post-processing

- **Service Orchestration**: 
  - Description: The current implementation manages service dependencies and notifications
  - Mitigation strategy: Use Ansible handlers and proper task ordering to ensure services are restarted when configurations change

### Migration Order

1. **fastapi-tutorial** (Priority 1)
   - Rationale: Application deployment is relatively straightforward with clear dependencies
   - Approach: Create roles for Python application deployment and PostgreSQL database

2. **cache** (Priority 2)
   - Rationale: Caching services are independent of other components
   - Approach: Create roles for Memcached and Redis configuration

3. **nginx-multisite** (Priority 3)
   - Rationale: Most complex component with security considerations and SSL configuration
   - Approach: Create comprehensive Nginx role with templates for site configuration and security hardening

### Assumptions

1. The target environment will continue to be Fedora-based systems (specifically Fedora 42 as indicated in the Vagrantfile)
2. The self-signed SSL certificates approach is acceptable for the migrated solution
3. The current security configurations (fail2ban, UFW, SSH hardening) are required in the migrated solution
4. The FastAPI application source will continue to be pulled from the same Git repository
5. The Redis and PostgreSQL passwords currently hardcoded will need to be secured in the Ansible implementation
6. The current directory structure for web content and application deployment will be maintained
7. The Vagrant development environment will be maintained but updated to use Ansible instead of Chef