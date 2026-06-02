# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, configuration templates, and security settings. Based on the complexity and scope, this migration is estimated to be of medium complexity and should take approximately 3-4 weeks with 1-2 dedicated engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and custom configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall), sysctl security settings

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies with version constraints
- `solo.json`: Chef Solo configuration file containing the run list and node attributes
- `solo.rb`: Chef Solo configuration file specifying file paths and log settings
- `Vagrantfile`: Vagrant configuration for local development using Fedora 42, with port forwarding and network settings
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used for development in Vagrant
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package module
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package module with custom configuration

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW with specific rules for SSH, HTTP, and HTTPS. Ansible migration should use the `ufw` module to maintain identical rules.
- **Fail2ban Setup**: The cookbook configures fail2ban with custom jail settings. Ansible should use the `template` module to create identical jail configurations.
- **SSH Hardening**: The cookbook disables root login and password authentication. Ansible should use the `lineinfile` or `template` module to configure SSH daemon settings.
- **SSL Certificate Management**: Self-signed certificates are generated for each site. Ansible should use the `openssl_certificate` module to generate equivalent certificates.
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL database credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - No Chef Vault or encrypted data bags are used, but these credentials should be moved to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The Chef cookbook dynamically generates site configurations based on node attributes. Ansible will need to use loops with templates to achieve the same functionality.
- **Redis Configuration Patching**: The Chef cookbook uses a ruby_block to modify Redis configuration files after they're created. Ansible will need to use the `lineinfile` module or custom templates to achieve the same result.
- **Service Orchestration**: The FastAPI application depends on PostgreSQL being running. Ansible handlers and conditional checks will be needed to ensure proper service ordering.
- **SSL Certificate Generation**: The Chef cookbook generates self-signed certificates for each site. Ansible will need to use the `openssl_certificate` module with proper conditionals to avoid regenerating certificates unnecessarily.

### Migration Order

1. **nginx-multisite cookbook** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation and configuration
   - Add security hardening (fail2ban, ufw, sysctl)
   - Implement SSL certificate generation
   - Configure virtual hosts

2. **cache cookbook** (low complexity, standalone service)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper service management

3. **fastapi-tutorial cookbook** (high complexity, application deployment)
   - Set up PostgreSQL database
   - Deploy application code from Git
   - Configure Python environment
   - Set up systemd service

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS as specified in the cookbook metadata.
2. The Vagrant development environment will be maintained, requiring Ansible to work with Vagrant for local testing.
3. Self-signed certificates are acceptable for the migrated solution (no Let's Encrypt or commercial certificates required).
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The hardcoded credentials in the cookbooks are for development only and will be replaced with Ansible Vault variables.
6. The current security settings (disabled root login, disabled password authentication) are appropriate for the target environment.
7. The Redis configuration hack in the cache cookbook is necessary due to compatibility issues that will need to be addressed in Ansible.