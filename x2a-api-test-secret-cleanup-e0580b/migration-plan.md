# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 3 weeks
- Testing and Validation: 2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 7 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- External dependencies on community cookbooks will need Ansible equivalents
- Security configurations are present and need careful migration
- Secrets management needs improvement in the Ansible implementation

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks. Will be replaced by Ansible Galaxy requirements.yml
- `Vagrantfile`: VM configuration for development/testing. Can be adapted for Ansible testing with minimal changes.
- `solo.json`: Chef node attributes and run list. Will be converted to Ansible group_vars and inventory.
- `solo.rb`: Chef configuration file. No direct Ansible equivalent needed.
- `vagrant-provision.sh`: Provisioning script for Vagrant. Will be replaced by Ansible playbook calls.

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ mentioned in cookbook metadata
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible memcached role (geerlingguy.memcached or equivalent)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (geerlingguy.redis or equivalent)

### Security Considerations

- **SSL Certificate Management**: 
  - Current implementation generates self-signed certificates
  - Migration approach: Use Ansible crypto modules for certificate generation or integrate with Let's Encrypt

- **Firewall Configuration (UFW)**:
  - Migration approach: Use Ansible ufw module or firewalld module depending on target OS

- **Fail2ban Configuration**:
  - Migration approach: Use Ansible to deploy fail2ban configuration templates

- **SSH Hardening**:
  - Migration approach: Use Ansible ssh_config module or templates to configure SSH security settings

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL password is hardcoded in the recipe (`fastapi_password`)
  - Migration approach: Use Ansible Vault for storing sensitive credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation dynamically generates site configurations based on node attributes
  - Mitigation: Use Ansible templates with variable substitution and loops to achieve similar functionality

- **Redis Configuration Workaround**:
  - Description: The current implementation includes a hack to fix Redis configuration
  - Mitigation: Create proper Ansible templates for Redis configuration without requiring post-processing

- **Service Orchestration**:
  - Description: Ensuring proper service start order and dependencies
  - Mitigation: Use Ansible handlers and meta dependencies to ensure proper service ordering

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Relatively self-contained with clear configuration templates

2. **cache** (Priority 2)
   - Depends on external cookbooks that need Ansible equivalents
   - Moderate complexity with Redis configuration requiring special attention

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on PostgreSQL
   - Involves multiple components (database, application code, service configuration)

### Assumptions

1. The target environment will continue to be Fedora-based systems, with potential support for Ubuntu and CentOS as mentioned in the cookbook metadata.
2. Self-signed certificates are acceptable for the migrated solution, but the Ansible roles should be designed to allow for easy integration with proper certificates.
3. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate and should be maintained in the Ansible implementation.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available and compatible.
5. The current Redis and Memcached configurations meet performance requirements and don't need optimization during migration.
6. The Vagrant development environment should be preserved with equivalent functionality.
7. No CI/CD pipeline integration is required as part of the migration (none was present in the original).