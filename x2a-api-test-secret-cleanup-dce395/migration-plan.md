# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup with three primary cookbooks: nginx-multisite, cache, and fastapi-tutorial. The migration to Ansible will involve converting Chef recipes, templates, and resources to Ansible roles, playbooks, and templates. Based on the analysis, this is a medium-complexity migration with an estimated timeline of 3-4 weeks for a small team (2-3 people).

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site SSL configuration, security hardening (fail2ban, ufw), custom site templates

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database provisioning, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints.
- `solo.json`: Chef Solo configuration file containing the run list and node attributes.
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings.
- `Vagrantfile`: Defines the development VM configuration using Vagrant with libvirt provider.
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Ansible role
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or DavidWittman.redis

### Security Considerations

- **SSL Certificate Management**: 
  - Migration approach: Use Ansible's `openssl_*` modules for certificate generation
  - Consider integrating with Ansible Vault for secure key storage

- **Redis Authentication**: 
  - Migration approach: Store Redis password in Ansible Vault
  - Update Redis configuration template to use variable from Vault

- **PostgreSQL Credentials**: 
  - Migration approach: Store database credentials in Ansible Vault
  - Use Ansible's postgresql_* modules with secure credential handling

- **Vault/secrets management**:
  - nginx-multisite: Self-signed SSL certificates (2 files per site)
  - cache: Redis password in plaintext ("redis_secure_password_123")
  - fastapi-tutorial: PostgreSQL credentials in plaintext ("fastapi_password")
  - Environment variables with sensitive data in .env file

### Technical Challenges

- **Custom Resource Migration**: 
  - Description: The `lineinfile` custom resource in nginx-multisite needs to be replaced
  - Mitigation: Use Ansible's built-in `lineinfile` module which provides similar functionality

- **Multi-site Nginx Configuration**: 
  - Description: Complex Nginx configuration with multiple SSL-enabled sites
  - Mitigation: Create Ansible templates based on existing Chef templates, use with_items/loop to iterate through site configurations

- **Service Dependencies**: 
  - Description: Ensuring proper service ordering (e.g., PostgreSQL before FastAPI)
  - Mitigation: Use Ansible handlers and meta dependencies to ensure proper service ordering

### Migration Order

1. **cache** (Priority 1 - low risk, straightforward configuration)
   - Simple configuration with well-defined external dependencies
   - Good starting point to establish patterns for the rest of the migration

2. **nginx-multisite** (Priority 2 - moderate complexity)
   - Core infrastructure component with security implications
   - More complex with multiple templates and configurations

3. **fastapi-tutorial** (Priority 3 - application deployment)
   - Application deployment that depends on other infrastructure
   - Involves database configuration and application-specific settings

### Assumptions

1. The target environment will continue to be Fedora-based systems (Fedora 42 as specified in Vagrantfile)
2. Self-signed certificates are acceptable for development; production would require proper certificate management
3. The same network configuration (ports, IP addresses) will be maintained
4. The FastAPI application source will continue to be pulled from the same Git repository
5. Security configurations (fail2ban, ufw, SSH hardening) are still required in the Ansible version
6. Redis and PostgreSQL passwords in the current configuration are for development only and will be replaced with proper secrets management
7. The current Chef Solo approach suggests a push-based deployment model, which aligns well with Ansible's architecture
8. No external Chef server is being used, simplifying the migration process