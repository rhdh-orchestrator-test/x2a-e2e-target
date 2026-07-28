# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services (Redis and Memcached) and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- External dependencies are clearly specified in the Berksfile
- Security configurations are comprehensive and will require careful migration
- The FastAPI application deployment includes database setup that will need special attention

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site-specific configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), custom site templates

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
- `solo.json`: Contains the run list and configuration data for the Chef run
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Defines the Vagrant VM configuration (Fedora 42) with port forwarding and networking

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be a local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or use the `ansible.builtin.package` module to install Nginx and manage configuration files
- **memcached (~> 6.0)**: Use Ansible's `memcached` role or the `ansible.builtin.package` module with appropriate templates
- **redisio (~> 7.2.4)**: Use Ansible's `redis` role or the `ansible.builtin.package` module with custom templates for Redis configuration

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. In Ansible, use the `openssl_*` modules to manage certificates
- **Firewall Configuration**: Replace UFW configuration with Ansible's `ufw` module or `firewalld` module depending on the target OS
- **fail2ban Configuration**: Use Ansible's `template` module to configure fail2ban similar to the current Chef implementation
- **SSH Hardening**: Migrate SSH security configurations using Ansible's `lineinfile` or `template` modules
- **Vault/secrets management**:
  - Redis password in cache cookbook: Move to Ansible Vault
  - PostgreSQL credentials in fastapi-tutorial cookbook: Move to Ansible Vault
  - Total credentials detected: 2 (Redis password, PostgreSQL user/password)

### Technical Challenges

- **Custom Resource Migration**: The `lineinfile` custom resource in the nginx-multisite cookbook needs to be replaced with Ansible's native `lineinfile` module
- **Template Conversion**: All ERB templates need to be converted to Jinja2 format for Ansible
- **Service Management**: The systemd service configuration for FastAPI needs to be migrated to use Ansible's `systemd` module
- **PostgreSQL Configuration**: Database creation and user management needs to be migrated to Ansible's `postgresql_*` modules

### Migration Order

1. **nginx-multisite** (Priority 1): Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add SSL certificate management
   - Implement security hardening (fail2ban, ufw)
   - Configure virtual hosts

2. **cache** (Priority 2): Caching services that may be required by applications
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (Priority 3): Application deployment that depends on the infrastructure
   - Set up Python environment and dependencies
   - Configure PostgreSQL database
   - Deploy application code
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora-based systems (the Vagrantfile specifies Fedora 42)
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or other CA)
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
4. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate for the target environment
5. The Redis and PostgreSQL passwords in the current configuration are development credentials and will be replaced with proper secrets management in production
6. The current Nginx site configurations (test.cluster.local, ci.cluster.local, status.cluster.local) will remain the same in the migrated solution