# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx configuration with caching services and a FastAPI application. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- External dependencies on community cookbooks need to be replaced with Ansible Galaxy roles
- Security configurations and SSL certificate management require careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), custom templates

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, dependency on community cookbooks

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including external cookbooks from Chef Supermarket (nginx, memcached, redisio)
- `solo.json`: Contains node attributes and run list for Chef Solo, including site configurations and security settings
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Defines the Vagrant VM configuration (Fedora 42) with networking and provisioning settings

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be a local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role from Galaxy or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role or custom Ansible tasks
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` role or custom Ansible tasks

### Security Considerations

- **SSL Certificate Management**: The current setup generates self-signed certificates for development. Migrate to Ansible's `openssl_*` modules or `community.crypto` collection
- **Firewall Configuration**: Replace UFW configuration with Ansible's `firewalld` or `ufw` modules
- **Fail2ban Setup**: Migrate fail2ban configuration to Ansible tasks using templates
- **SSH Hardening**: Preserve SSH security settings using Ansible's `lineinfile` or templates
- **Vault/secrets management**: 
  - Redis password in cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials in fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - Consider migrating to Ansible Vault for secure credential storage

### Technical Challenges

- **Custom Resource Migration**: The `lineinfile` custom resource in nginx-multisite needs to be replaced with Ansible's native `lineinfile` module
- **Template Conversion**: All ERB templates need to be converted to Jinja2 format for Ansible
- **Service Management**: Ensure proper service management and notification handling in Ansible
- **Idempotency**: Ensure all Ansible tasks are idempotent, especially those replacing Ruby blocks and execute resources

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add SSL certificate management
   - Implement security hardening (fail2ban, firewall)
   - Configure virtual hosts

2. **cache** (Priority 2)
   - Implement Memcached configuration
   - Set up Redis with authentication
   - Ensure proper service management

3. **fastapi-tutorial** (Priority 3)
   - Set up Python environment and dependencies
   - Configure PostgreSQL database
   - Deploy application from Git
   - Create systemd service

### Assumptions

1. The target environment will continue to be Fedora-based systems
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or other CA)
3. The current security configurations (fail2ban, ufw, SSH hardening) should be preserved in the Ansible implementation
4. The directory structure for web content and SSL certificates will remain the same
5. The Vagrant development environment will be maintained but updated to use Ansible provisioner instead of Chef
