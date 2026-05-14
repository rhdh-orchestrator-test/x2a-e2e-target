# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 3 weeks
- Testing and Validation: 2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 7 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- External dependencies on community cookbooks will need Ansible equivalents
- Security configurations are present and must be carefully migrated

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and fail2ban integration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, firewall configuration

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks - will be replaced by Ansible Galaxy requirements.yml
- `Vagrantfile`: VM configuration for development/testing - can be adapted for Ansible testing
- `solo.json`: Chef node attributes and run list - will be converted to Ansible group_vars and inventory
- `solo.rb`: Chef configuration - will be replaced by ansible.cfg
- `vagrant-provision.sh`: Provisioning script for Vagrant - will be replaced by Ansible playbook

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)

### Security Considerations

- **SSL Certificate Management**: 
  - Current implementation generates self-signed certificates
  - Migration approach: Use Ansible's openssl_* modules for certificate generation

- **Firewall Configuration**: 
  - Current implementation uses UFW
  - Migration approach: Use Ansible's ufw module or firewalld module (more appropriate for Fedora)

- **Fail2ban Integration**: 
  - Current implementation installs and configures fail2ban
  - Migration approach: Use Ansible to install and configure fail2ban with templates

- **SSH Hardening**: 
  - Current implementation disables root login and password authentication
  - Migration approach: Use Ansible's lineinfile or template module for sshd_config

- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook
  - Migration approach: Use Ansible Vault for storing sensitive information

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Preserving the dynamic site configuration capability
  - Mitigation: Use Ansible with_items/loop constructs and templates to generate site configurations

- **Service Dependencies**: 
  - Challenge: Ensuring proper service startup order (PostgreSQL before FastAPI app)
  - Mitigation: Use Ansible handlers and meta dependencies between roles

- **SSL Certificate Generation**: 
  - Challenge: Maintaining the same level of security while generating certificates
  - Mitigation: Use Ansible's openssl_* modules with appropriate parameters

- **Python Environment Management**: 
  - Challenge: Setting up virtual environments and dependencies
  - Mitigation: Use Ansible's pip module with virtualenv parameter

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Relatively self-contained with clear configuration templates

2. **cache** (Priority 2)
   - Dependent services that support the application
   - Requires external role dependencies

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on both nginx and database
   - Most complex with database setup, application deployment, and service configuration

### Assumptions

1. The target environment will continue to be Fedora-based systems
2. Self-signed certificates are acceptable for the migrated solution
3. The same security policies should be applied in the Ansible implementation
4. The FastAPI application source will continue to be pulled from the same Git repository
5. The current directory structure in the target system should be preserved
6. No changes to application configuration or behavior are required
7. The Vagrant development environment should be preserved for testing