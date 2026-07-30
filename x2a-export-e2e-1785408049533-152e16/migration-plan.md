# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server setup with FastAPI application backend and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- No custom resources or complex Chef-specific patterns
- Contains security configurations and SSL certificate management that will need careful migration
- Includes database configuration and application deployment

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), sysctl security settings

- **fastapi-tutorial**:
    - Description: FastAPI Python application deployment with PostgreSQL database setup
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks, lists external dependencies from Chef Supermarket
- `solo.json`: Chef Solo configuration with run list and node attributes
- `solo.rb`: Chef Solo configuration file with cookbook paths and log settings
- `vagrant-provision.sh`: Provisioning script for Vagrant VM setup and Chef execution
- `Vagrantfile`: Vagrant configuration for development environment using Fedora 42

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile) with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or community.general.memcached module
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or community.general.redis module

### Security Considerations

- **Firewall Configuration**: Migration of UFW rules to Ansible's ufw module
- **Fail2ban Setup**: Convert fail2ban configuration to Ansible's fail2ban module
- **SSH Hardening**: Migrate SSH security settings using Ansible's openssh_config module
- **SSL Certificate Management**: Replace self-signed certificate generation with Ansible's openssl_* modules
- **Vault/secrets management**: 
  - Redis password in cache cookbook (hardcoded as 'redis_secure_password_123')
  - PostgreSQL database credentials in fastapi-tutorial cookbook (hardcoded as 'fastapi:fastapi_password')
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Configuration**: Ensuring the dynamic generation of Nginx site configurations works correctly in Ansible
- **SSL Certificate Management**: Properly handling SSL certificate generation and permissions
- **Service Dependencies**: Maintaining proper ordering of service installations and configurations
- **Idempotency**: Ensuring all operations are idempotent, especially the database creation scripts

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Then add SSL and security features
   - Finally implement multi-site configuration

2. **cache** (Priority 2)
   - Relatively independent service
   - Simple configuration with standard components
   - Address Redis authentication security

3. **fastapi-tutorial** (Priority 3)
   - Application deployment with database dependencies
   - More complex with multiple components (Python, PostgreSQL, Git)
   - Requires careful handling of environment variables and service configuration

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or other CA)
3. The current security settings (fail2ban, ufw, SSH hardening) should be maintained in the Ansible version
4. The PostgreSQL and Redis passwords currently hardcoded will be moved to Ansible Vault
5. The directory structure for web content (/var/www/[site]) will remain the same
6. The FastAPI application will continue to be deployed from the same Git repository
7. The Vagrant development environment should be maintained but updated to use Ansible provisioner