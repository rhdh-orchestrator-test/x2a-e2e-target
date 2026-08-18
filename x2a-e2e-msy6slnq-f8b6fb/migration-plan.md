# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration scope is moderate, consisting of three primary cookbooks with external dependencies. Based on the complexity and size, the estimated timeline for migration is 2-3 weeks with 1 dedicated engineer or 1-1.5 weeks with 2 engineers working in parallel.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, including security hardening
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate management, security hardening

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database provisioning, systemd service configuration

### Infrastructure Files

- `Berksfile`: Manages cookbook dependencies, including local and external cookbooks. Migration will require mapping these dependencies to Ansible Galaxy roles or collections.
- `solo.json`: Contains the run list and configuration data for Chef Solo. This will be migrated to Ansible inventory variables and group_vars.
- `solo.rb`: Chef Solo configuration file. Will be replaced by Ansible configuration.
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef. Will need to be updated to use Ansible.
- `Vagrantfile`: Defines the development VM. Will need minor updates to use Ansible provisioner instead of Chef.

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ based on cookbook metadata
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or the official Nginx collection from Ansible Galaxy
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role or equivalent
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` role or equivalent

### Security Considerations

- **SSL Certificate Management**: The nginx-multisite cookbook manages SSL certificates. Migration should preserve the certificate paths and configurations.
  - Migration approach: Use Ansible's `openssl_*` modules for certificate management
  
- **Security Hardening**: The nginx-multisite cookbook includes security hardening via the security.rb recipe.
  - Migration approach: Use Ansible security roles like `dev-sec.nginx-hardening` or implement equivalent tasks

- **Fail2ban and UFW**: Security configurations in solo.json indicate Fail2ban and UFW are enabled.
  - Migration approach: Use Ansible's `firewalld` or `ufw` modules and appropriate Fail2ban roles

- **SSH Hardening**: SSH configuration disables root login and password authentication.
  - Migration approach: Use Ansible's `ssh` module or `dev-sec.ssh-hardening` role

- **Vault/secrets management**: 
  - Redis password in cache/recipes/default.rb: "redis_secure_password_123"
  - PostgreSQL password in fastapi-tutorial/recipes/default.rb: "fastapi_password"
  - Database connection string in .env file
  - Migration approach: Use Ansible Vault for storing these credentials securely

### Technical Challenges

- **Multi-site Nginx Configuration**: The nginx-multisite cookbook manages multiple virtual hosts with SSL. 
  - Mitigation: Use Ansible templates with loops to generate site configurations, similar to the Chef approach

- **Redis Configuration Patching**: The cache cookbook includes a ruby_block to modify Redis configuration.
  - Mitigation: Use Ansible's `lineinfile` or `replace` modules to achieve the same configuration changes

- **PostgreSQL User and Database Creation**: The fastapi-tutorial cookbook creates PostgreSQL users and databases.
  - Mitigation: Use Ansible's `postgresql_*` modules which provide more declarative management than the current shell commands

- **Python Application Deployment**: The fastapi-tutorial cookbook manages a Python virtual environment and application deployment.
  - Mitigation: Use Ansible's `pip` and `git` modules for more idempotent management

### Migration Order

1. **cache cookbook** (Priority 1, low risk): Simple configuration of Memcached and Redis services
2. **nginx-multisite cookbook** (Priority 2, moderate complexity): Core web server configuration with multiple sites
3. **fastapi-tutorial cookbook** (Priority 3, higher complexity): Application deployment with database dependencies

### Assumptions

1. The current Chef setup is functional and represents the desired end state
2. SSL certificates are managed outside this configuration (no certificate generation is present)
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git is accessible
4. The target environment will continue to be Fedora-based systems
5. No CI/CD pipeline integration is required as part of the migration
6. The Vagrant development environment should be preserved with equivalent functionality
7. No monitoring or logging solutions are configured that would need migration
8. No backup or disaster recovery processes are configured that would need migration