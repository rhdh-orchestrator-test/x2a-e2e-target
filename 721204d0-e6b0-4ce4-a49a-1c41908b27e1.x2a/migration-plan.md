# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure for deploying a multi-site Nginx web server with SSL, security hardening, caching services (Redis and Memcached), and a FastAPI application with PostgreSQL. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline**: 2-3 weeks for a complete migration
**Complexity**: Medium
**Team Size Recommendation**: 1-2 DevOps engineers

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening (fail2ban, ufw), and SSL certificate management
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup, security hardening (fail2ban, ufw, sysctl)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Configuration data for Chef Solo, contains site configurations and security settings
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration for local development/testing environment

### Target Details

Based on the source repository analysis:

- **Operating System**: Fedora 42 (primary), with support for Ubuntu 18.04+ and CentOS 7+ mentioned in cookbook metadata
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks

### Security Considerations

- **SSL/TLS Configuration**: The nginx-multisite cookbook manages SSL certificates and security headers
  - Migration approach: Use Ansible's community.crypto modules for certificate generation
  - Ensure proper file permissions for private keys (0640) and certificate files

- **Firewall Configuration**: UFW is configured in security.rb
  - Migration approach: Use Ansible's community.general.ufw module

- **Fail2ban Configuration**: Configured in security.rb with a template
  - Migration approach: Use Ansible's community.general.fail2ban module

- **System Hardening**: sysctl security settings in sysctl-security.conf.erb
  - Migration approach: Use Ansible's posix.sysctl module

- **SSH Hardening**: Disables root login and password authentication
  - Migration approach: Use Ansible's openssh_config module

- **Vault/secrets management**:
  - Redis password in cache/recipes/default.rb: "redis_secure_password_123"
  - PostgreSQL credentials in fastapi-tutorial/recipes/default.rb: User "fastapi" with password "fastapi_password"
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: The nginx-multisite cookbook dynamically creates virtual hosts based on attributes
  - Mitigation: Use Ansible templates with loops to generate site configurations
  - Ensure proper SSL certificate handling for each site

- **Redis Configuration Hack**: The cache cookbook includes a ruby_block to modify Redis configuration
  - Mitigation: Create a custom Redis configuration template in Ansible that addresses these issues directly

- **PostgreSQL User/Database Setup**: The fastapi-tutorial cookbook uses inline SQL commands
  - Mitigation: Use Ansible's postgresql_* modules for cleaner database management

- **Service Dependencies**: Ensuring proper service startup order (e.g., PostgreSQL before FastAPI)
  - Mitigation: Use Ansible handlers and meta dependencies to manage service ordering

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add SSL certificate management
   - Add security hardening features

2. **cache** (Priority 2)
   - Relatively independent service
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (Priority 3)
   - Depends on PostgreSQL being configured
   - Implement database setup
   - Implement application deployment and service configuration

### Assumptions

1. The target environment will continue to use Fedora or a similar Linux distribution
2. Self-signed certificates are acceptable for development (production would likely use Let's Encrypt or other CA)
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
4. The security requirements (disabled root SSH, password authentication, etc.) will remain the same
5. The current directory structure in the target environment (/opt/fastapi-tutorial, /var/www/sites) will be maintained
6. The current Redis password and PostgreSQL credentials can be reused (though they should be stored securely)
7. The Vagrant development environment will continue to be used for testing