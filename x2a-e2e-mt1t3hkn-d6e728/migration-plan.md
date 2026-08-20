# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backend. The migration to Ansible will involve converting three Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- No complex custom resources or libraries
- Standard infrastructure components (Nginx, Redis, Memcached, PostgreSQL)
- Security configurations that need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall)

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
- `solo.json`: Contains node attributes and run list for Chef Solo, including Nginx site configurations and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Defines a Fedora 42 VM with port forwarding for development and testing
- `vagrant-provision.sh`: Shell script to install Chef and run the cookbooks in the Vagrant environment

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or DavidWittman.redis

### Security Considerations

- **SSL Certificate Management**: 
  - The Chef cookbook generates self-signed certificates
  - Migration should maintain this functionality or integrate with Let's Encrypt
  - Consider using Ansible's `openssl_*` modules or the `community.crypto` collection

- **Firewall Configuration**: 
  - Current implementation uses UFW
  - Migrate to Ansible's `ufw` module or `firewalld` module depending on target OS

- **Fail2ban Configuration**: 
  - Migrate fail2ban configuration to use Ansible's `template` module for configuration files
  - Use `service` module to manage the fail2ban service

- **SSH Hardening**:
  - Current implementation disables root login and password authentication
  - Use Ansible's `lineinfile` module or templates to configure SSH

- **Vault/secrets management**:
  - Redis password is hardcoded in the Chef recipe
  - PostgreSQL credentials are hardcoded in the FastAPI recipe
  - Migrate to Ansible Vault for secure credential storage

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: The Chef cookbook dynamically creates multiple virtual hosts based on node attributes
  - Solution: Use Ansible's with_items/loop to iterate through site configurations and template generation

- **SSL Certificate Generation**:
  - Challenge: Self-signed certificates are generated with specific attributes
  - Solution: Use Ansible's `openssl_certificate` module with proper parameters

- **Service Dependencies**:
  - Challenge: Ensuring proper service startup order (PostgreSQL before FastAPI application)
  - Solution: Use Ansible's `meta: flush_handlers` and handler dependencies

- **Python Environment Management**:
  - Challenge: Setting up Python virtual environment and dependencies
  - Solution: Use Ansible's `pip` module with virtualenv parameter

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx configuration and virtual hosts
   - Add SSL and security features

2. **cache** (Priority 2)
   - Migrate Memcached configuration
   - Migrate Redis configuration with authentication

3. **fastapi-tutorial** (Priority 3)
   - Migrate PostgreSQL setup
   - Migrate Python application deployment
   - Configure systemd service

### Assumptions

1. The target environment will continue to use the same operating systems (Fedora/Ubuntu/CentOS)
2. Self-signed certificates are acceptable for development (production would likely use proper certificates)
3. The same security requirements will apply in the new environment
4. The FastAPI application repository will remain available at the specified URL
5. The directory structure for web content and application files will remain the same
6. The Vagrant development environment will be maintained for testing
7. No changes to the application configuration or behavior are required
8. Redis and Memcached versions will remain compatible with the application