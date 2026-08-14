# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, templates, and configuration files. The complexity is moderate, with estimated timeline of 2-3 weeks for a complete migration.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and SSL certificate management
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall), custom Nginx configuration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, service management

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef Solo configuration file with node attributes and run list
- `solo.rb`: Chef Solo configuration settings
- `Vagrantfile`: Vagrant configuration for local development/testing environment
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or service module
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or service module

### Security Considerations

- **SSL Certificate Management**: The current setup generates self-signed certificates for development. Migration should:
  - Maintain the same certificate generation logic for development
  - Consider integrating with Ansible's crypto modules for production
  - Ensure proper permissions on private keys (640 with ssl-cert group ownership)

- **Firewall Configuration**: The current setup uses UFW. Migration should:
  - Use Ansible's firewalld or ufw modules based on target OS
  - Maintain the same rule set (SSH, HTTP, HTTPS)

- **SSH Hardening**: The current setup disables root login and password authentication. Migration should:
  - Use Ansible's openssh_config module to apply the same settings
  - Ensure idempotent configuration

- **Fail2ban**: The current setup installs and configures fail2ban. Migration should:
  - Use Ansible's package and template modules to install and configure fail2ban
  - Maintain the same jail configuration

- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL database credentials in fastapi-tutorial cookbook: "fastapi:fastapi_password"
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Custom Resource Migration**: The `lineinfile` custom resource in nginx-multisite needs to be replaced with Ansible's native `lineinfile` module
- **Template Conversion**: All ERB templates need to be converted to Jinja2 format for Ansible
- **Attribute Hierarchy**: Chef's node attribute hierarchy needs to be flattened into Ansible variables
- **Idempotency**: Ensure all shell commands and file operations remain idempotent in Ansible
- **Service Management**: Ensure proper service management across different OS distributions

### Migration Order

1. **nginx-multisite cookbook** (Priority 1)
   - Core infrastructure component that others depend on
   - Moderate complexity with multiple recipes and templates
   - Start with basic Nginx configuration, then add SSL and security features

2. **cache cookbook** (Priority 2)
   - Depends on external cookbooks (memcached, redisio)
   - Relatively simple with few custom configurations
   - Focus on maintaining Redis authentication security

3. **fastapi-tutorial cookbook** (Priority 3)
   - Application-specific cookbook
   - Involves database setup, Python environment, and service configuration
   - Requires careful handling of database credentials

### Assumptions

1. The target environment will continue to use Fedora or similar Linux distributions
2. Self-signed certificates are acceptable for development environments
3. The same security hardening measures should be maintained
4. The directory structure for web content will remain the same
5. PostgreSQL and Python versions will remain compatible with the FastAPI application
6. The migration will not involve changes to the application code itself
7. The Vagrant development environment should be preserved or replaced with equivalent functionality
8. No specific CI/CD pipeline integration is required beyond what's in the current setup