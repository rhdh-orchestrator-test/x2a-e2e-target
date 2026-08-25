# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with FastAPI backend and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated complexity is moderate, with an estimated timeline of 2-3 weeks for a complete migration, including testing and documentation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and SSL certificate management
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), custom Nginx configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Configures caching services (Memcached and Redis) with security settings
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (both local and external from Chef Supermarket)
- `solo.json`: Contains node configuration data including site configurations and security settings
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Defines the development VM configuration using Vagrant

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or collection (e.g., `ansible.posix.nginx`)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., `geerlingguy.memcached`)
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role (e.g., `geerlingguy.redis`)

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should maintain this capability while allowing for integration with Let's Encrypt or other certificate providers.
- **Security Hardening**: The current implementation includes:
  - fail2ban configuration
  - UFW firewall rules
  - SSH hardening (disabling root login, password authentication)
  - System hardening via sysctl
- **Vault/secrets management**:
  - Redis password in plaintext in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL database credentials in plaintext in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Custom Resource Migration**: The `lineinfile` custom resource in the nginx-multisite cookbook needs to be replaced with Ansible's built-in `lineinfile` module.
- **Template Conversion**: All ERB templates need to be converted to Jinja2 format for Ansible.
- **Idempotency**: Ensure all shell commands and file operations remain idempotent when converted to Ansible tasks.
- **Service Management**: Ensure proper service management and notification handling for configuration changes.

### Migration Order

1. **nginx-multisite** (Priority 1): This is the foundation for the web infrastructure and should be migrated first.
   - Start with basic Nginx installation and configuration
   - Add virtual host configuration
   - Add SSL certificate generation
   - Add security hardening features

2. **cache** (Priority 2): This has fewer dependencies and is relatively self-contained.
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (Priority 3): This depends on a working web server and database.
   - Implement Python environment setup
   - Implement PostgreSQL configuration
   - Implement application deployment and service configuration

### Assumptions

1. The target environment will continue to be Fedora/RHEL-based systems, with potential support for Ubuntu/Debian.
2. Self-signed certificates are acceptable for development, but production environments may require integration with a certificate authority.
3. The current security configurations are appropriate for the target environment and should be maintained.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The current directory structure for web content and configuration files will be maintained.
6. The migration will not involve significant architectural changes to the application stack.
7. The Vagrant development environment will be maintained, but converted to use Ansible provisioning instead of Chef.