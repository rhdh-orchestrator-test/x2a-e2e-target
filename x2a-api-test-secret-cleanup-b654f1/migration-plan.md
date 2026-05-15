# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application with PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- **Total**: 5-6 weeks

**Complexity Assessment:**
- Medium complexity due to multiple services and security configurations
- Moderate dependency on external cookbooks that need Ansible equivalents
- Security configurations that require careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), sysctl security settings

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, service management

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints.
- `Vagrantfile`: Defines a Fedora 42 VM with networking and provisioning configuration for testing.
- `solo.json`: Chef Solo configuration file with run list and node attributes.
- `solo.rb`: Chef Solo configuration specifying cookbook paths and logging settings.
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef.

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or custom role
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy or custom role
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role from Galaxy or custom role

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration approach: Use Ansible's openssl_* modules for certificate generation

- **Firewall Configuration**: 
  - UFW is configured with specific rules
  - Migration approach: Use Ansible's ufw module for equivalent configuration

- **Fail2ban Configuration**: 
  - Fail2ban is installed and configured
  - Migration approach: Create Ansible tasks using the template module for fail2ban configuration

- **SSH Hardening**: 
  - Root login disabled
  - Password authentication disabled
  - Migration approach: Use Ansible's lineinfile or template module for SSH configuration

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (redis_secure_password_123)
  - PostgreSQL password is hardcoded in the recipe (fastapi_password)
  - Migration approach: Use Ansible Vault for storing sensitive credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current setup dynamically generates Nginx site configurations based on node attributes
  - Mitigation: Use Ansible templates with loops to generate site configurations from variables

- **Redis Configuration Hacks**: 
  - Description: The current setup includes a ruby_block to modify Redis configuration files after they're created
  - Mitigation: Create proper Redis configuration templates in Ansible rather than modifying files after creation

- **Service Dependencies**: 
  - Description: The FastAPI application depends on PostgreSQL being configured first
  - Mitigation: Use Ansible handlers and proper task ordering to ensure dependencies are met

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component
   - Other services depend on it
   - Contains security configurations that should be established first

2. **cache** (Priority 2)
   - Standalone service with minimal dependencies
   - Moderate complexity due to Redis configuration requirements

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on other infrastructure
   - Requires database setup and configuration

### Assumptions

1. The target environment will continue to be Fedora or similar Linux distributions.
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or other CA).
3. The same security hardening approach (fail2ban, ufw, SSH hardening) is desired in the Ansible solution.
4. The FastAPI application source will continue to be pulled from the same Git repository.
5. The current VM resource specifications (2GB RAM, 2 CPUs) will remain the same.
6. The network configuration (ports, IP addresses) will remain consistent.
7. No CI/CD pipeline integration is required for the initial migration.
8. The Redis and PostgreSQL passwords will be managed securely in the new solution.