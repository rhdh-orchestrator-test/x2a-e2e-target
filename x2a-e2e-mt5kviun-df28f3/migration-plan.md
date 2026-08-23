# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration scope is moderate, consisting of three primary Chef cookbooks with external dependencies. Based on the complexity and size, this migration is estimated to take 2-3 weeks with 1-2 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and SSL certificate management
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup, security hardening

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

- `Berksfile`: Manages Chef cookbook dependencies, including local and external cookbooks. Will be replaced by Ansible Galaxy requirements.
- `solo.json`: Contains Chef node attributes and run list. Will be replaced by Ansible inventory variables.
- `solo.rb`: Chef Solo configuration file. Will be replaced by Ansible configuration.
- `Vagrantfile`: Defines the development VM using Fedora 42. Can be adapted to use Ansible provisioner instead of Chef.
- `vagrant-provision.sh`: Shell script that installs Chef and runs the cookbooks. Will be replaced with Ansible provisioning script.

### Target Details

Based on the source configuration files:

- **Operating System**: Supports Ubuntu 18.04+ and CentOS 7+, with Fedora 42 used in Vagrant development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Ansible Galaxy
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role from Ansible Galaxy or community.general.redis module

### Security Considerations

- **SSL/TLS Configuration**: The nginx-multisite cookbook manages SSL certificates. Migration should preserve:
  - Certificate paths (/etc/ssl/certs and /etc/ssl/private)
  - Per-site SSL enablement
  - Self-signed certificates for development

- **Security Hardening**: The security.rb recipe in nginx-multisite includes:
  - fail2ban configuration
  - ufw firewall setup
  - SSH hardening (root login disabled, password authentication disabled)

- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook as 'redis_secure_password_123'
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (user: fastapi, password: fastapi_password)
  - Consider migrating these to Ansible Vault or another secrets management solution

### Technical Challenges

- **Multi-site Nginx Configuration**: The nginx-multisite cookbook manages multiple virtual hosts with SSL. Ensure the Ansible roles can handle the same level of complexity for multiple sites.
  - Mitigation: Use Ansible templates to generate site configurations similar to the Chef templates.

- **Redis Configuration Hack**: The cache cookbook includes a ruby_block to modify Redis configuration files after they're created. This will need special handling in Ansible.
  - Mitigation: Use Ansible's lineinfile or template module with proper conditionals to achieve the same result.

- **FastAPI Application Deployment**: The fastapi-tutorial cookbook clones a Git repository and sets up a Python environment with dependencies.
  - Mitigation: Use Ansible's git, pip, and template modules to replicate this functionality.

### Migration Order

1. **cache cookbook** (Priority 1, moderate complexity)
   - Simple configuration of Memcached and Redis services
   - Good starting point with well-defined scope

2. **nginx-multisite cookbook** (Priority 2, moderate complexity)
   - Core infrastructure component that other services depend on
   - Multiple configuration files and templates to migrate

3. **fastapi-tutorial cookbook** (Priority 3, higher complexity)
   - Application deployment with database setup
   - Requires coordination of multiple services (PostgreSQL, Python, systemd)

### Assumptions

1. The current Chef setup is functional and represents the desired end state.
2. The target environment will continue to be Fedora/CentOS/Ubuntu based systems.
3. The Vagrant development environment should be preserved for testing.
4. No changes to the application architecture are required during migration.
5. Self-signed certificates are acceptable for development environments.
6. The hardcoded credentials in the cookbooks are for development only and will be replaced with proper secret management in production.
7. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
8. The migration will maintain the same level of automation for deployment and configuration.