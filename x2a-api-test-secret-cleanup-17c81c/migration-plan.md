# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, configuration templates, and security settings.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- **Total**: 5-6 weeks

**Complexity Assessment:** Medium
- Well-structured Chef cookbooks with clear separation of concerns
- Standard web server, caching, and application deployment patterns
- Some security configurations that need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and proper SSL configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)

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

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4)
- `solo.json`: Contains the run list and configuration data for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Defines the Vagrant VM configuration (Fedora 42, port forwarding, etc.)

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development/testing

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` module and custom templates
- **memcached (~> 6.0)**: Use Ansible's package management to install and configure memcached
- **redisio (~> 7.2.4)**: Use Ansible's package management to install Redis and configure with templates

### Security Considerations

- **SSL Certificate Management**: 
  - Chef cookbook generates self-signed certificates
  - Migration approach: Use Ansible's `openssl_*` modules for certificate generation

- **Firewall Configuration**: 
  - Chef cookbook configures UFW with specific rules
  - Migration approach: Use Ansible's `ufw` module to configure identical rules

- **Fail2ban Configuration**: 
  - Chef cookbook installs and configures fail2ban
  - Migration approach: Use Ansible's package management and templates for fail2ban configuration

- **System Hardening**: 
  - Chef cookbook applies sysctl security settings
  - Migration approach: Use Ansible's `sysctl` module to apply the same settings

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL password is hardcoded in the recipe (`fastapi_password`)
  - Migration approach: Use Ansible Vault to securely store these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Replicating the dynamic site configuration from Chef
  - Mitigation: Use Ansible's template module with Jinja2 templates to generate site configurations

- **SSL Certificate Generation**: 
  - Challenge: Ensuring proper permissions and security for SSL certificates
  - Mitigation: Use Ansible's `openssl_*` modules with appropriate file permissions

- **Service Dependencies**: 
  - Challenge: Ensuring proper service startup order (PostgreSQL before FastAPI)
  - Mitigation: Use Ansible's handlers and meta dependencies to manage service order

- **Redis Configuration Hack**: 
  - Challenge: The Chef cookbook uses a ruby_block to modify Redis configuration
  - Mitigation: Create a proper Redis configuration template in Ansible

### Migration Order

1. **cache cookbook** (low complexity)
   - Simple installation and configuration of Memcached and Redis
   - Good starting point to establish patterns for service management

2. **nginx-multisite cookbook** (medium complexity)
   - Core web server configuration with multiple sites
   - Security hardening components

3. **fastapi-tutorial cookbook** (high complexity)
   - Application deployment with database dependencies
   - Requires coordination with the other components

### Assumptions

1. The target environment will continue to be Fedora-based systems
2. Self-signed certificates are acceptable for the migrated solution
3. The same security hardening measures should be applied
4. The FastAPI application repository will remain available at the specified URL
5. The directory structure for web content and application code will remain the same
6. No changes to the application configuration or database schema are required
7. The migration will not involve changes to the application code itself
8. The current Chef-managed infrastructure is functioning correctly
9. No additional monitoring or logging requirements beyond what's in the current Chef code
10. The Ansible roles will be used in a similar Vagrant development environment