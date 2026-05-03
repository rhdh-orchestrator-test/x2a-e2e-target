# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application with PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- **Total**: 5-7 weeks

**Complexity Assessment:**
- Medium complexity due to multiple services and security configurations
- Moderate dependency on external cookbooks that need Ansible equivalents
- Security configurations that require careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, dependency on external cookbooks

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment setup, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file listing both local and external cookbook dependencies. Migration will require mapping these dependencies to Ansible Galaxy roles or custom roles.
- `solo.json`: Contains the run list and node attributes. Will be converted to Ansible inventory variables and group_vars.
- `solo.rb`: Chef Solo configuration file. Will be replaced by Ansible configuration.
- `Vagrantfile`: Defines the development VM. Can be adapted for Ansible testing with minimal changes.
- `vagrant-provision.sh`: Provisioning script for Vagrant. Will be replaced by Ansible provisioning in Vagrantfile.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible community.nginx role or create a custom Nginx role
- **memcached (~> 6.0)**: Replace with geerlingguy.memcached or create a custom Memcached role
- **redisio (~> 7.2.4)**: Replace with geerlingguy.redis or create a custom Redis role

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration approach: Use Ansible's openssl_* modules for certificate generation

- **Firewall Configuration**: 
  - UFW is configured with specific rules
  - Migration approach: Use Ansible's ufw module to configure firewall rules

- **Fail2ban Configuration**: 
  - Fail2ban is installed and configured for intrusion prevention
  - Migration approach: Create an Ansible role for fail2ban configuration

- **SSH Hardening**: 
  - Root login disabled and password authentication disabled
  - Migration approach: Use Ansible's lineinfile module or template module to configure SSH

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL password is hardcoded in the FastAPI recipe (`fastapi_password`)
  - Migration approach: Use Ansible Vault to securely store and manage these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current setup dynamically creates Nginx site configurations based on node attributes
  - Mitigation: Use Ansible's template module with Jinja2 templates to achieve similar functionality

- **Redis Configuration Hacks**: 
  - Description: The cache cookbook includes a ruby_block to modify Redis configuration files after they're created
  - Mitigation: Create proper Redis configuration templates in Ansible to avoid post-configuration modifications

- **Service Orchestration**: 
  - Description: Ensuring services start in the correct order with proper dependencies
  - Mitigation: Use Ansible's handlers and meta dependencies to manage service ordering

- **SSL Certificate Generation**: 
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's openssl_* modules to generate certificates or consider integrating with Let's Encrypt for production environments

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx configuration and virtual hosts
   - Add SSL and security features

2. **cache** (Priority 2)
   - Moderate complexity with external dependencies
   - Implement Memcached and Redis configurations

3. **fastapi-tutorial** (Priority 3)
   - Application deployment with database dependencies
   - Requires PostgreSQL configuration and Python environment setup

### Assumptions

1. The target environment will continue to be Fedora-based systems (specifically Fedora 42 as indicated in the Vagrantfile)
2. Self-signed certificates are acceptable for development environments
3. The same security hardening measures will be maintained in the Ansible implementation
4. The FastAPI application source will continue to be pulled from the same Git repository
5. Redis and PostgreSQL passwords in the current implementation are for development purposes and will be replaced with more secure credentials in production
6. The current Vagrant setup is primarily for development and testing, not production deployment
7. No specific CI/CD integration is currently implemented and will need to be addressed separately if required
8. The current implementation does not include backup or monitoring solutions
9. The multi-site configuration is for development/testing purposes as indicated by the .cluster.local domain names
10. The current implementation assumes single-server deployment (all services on one host)