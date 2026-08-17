# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration scope is moderate, consisting of three primary cookbooks with external dependencies. Based on the complexity and size, this migration is estimated to take 2-3 weeks with 1-2 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, including security hardening
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate management, security hardening (fail2ban, ufw)

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

- `Berksfile`: Manages cookbook dependencies, including external cookbooks from Chef Supermarket (nginx, memcached, redisio). Will need to be replaced with Ansible Galaxy requirements.
- `solo.json`: Contains node configuration including the run list and attributes for Nginx sites and security settings. Will be migrated to Ansible group_vars or host_vars.
- `solo.rb`: Chef Solo configuration file. Will be replaced with ansible.cfg.
- `Vagrantfile`: Defines the development VM environment using Vagrant with libvirt provider. Can be adapted to use Ansible provisioner instead of Chef.
- `vagrant-provision.sh`: Shell script that installs Chef and runs the cookbooks. Will be replaced with Ansible playbook execution.

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: libvirt (from Vagrantfile)
- **Cloud Platform**: Not specified, appears to be targeting on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or create a custom role
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role from Galaxy

### Security Considerations

- **SSL Certificate Management**: The nginx-multisite cookbook manages SSL certificates. Migration should include proper certificate handling in Ansible.
  - Migration approach: Use Ansible's `copy` module for certificates or integrate with `community.crypto` collection for certificate generation.

- **Firewall Configuration**: The security recipe in nginx-multisite configures UFW.
  - Migration approach: Use Ansible's `ufw` module or `firewalld` module depending on target OS.

- **fail2ban Configuration**: Security hardening includes fail2ban setup.
  - Migration approach: Use Ansible's `community.general.fail2ban` module.

- **SSH Hardening**: SSH configuration includes disabling root login and password authentication.
  - Migration approach: Use Ansible's `template` module with secure SSH configuration.

- **Vault/secrets management**:
  - Redis password in cache/recipes/default.rb: "redis_secure_password_123"
  - PostgreSQL password in fastapi-tutorial/recipes/default.rb: "fastapi_password"
  - Database connection string in .env file
  - Migration approach: Use Ansible Vault for all credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: The nginx-multisite cookbook manages multiple virtual hosts with SSL. This will require careful template migration.
  - Mitigation: Create flexible Ansible templates that can handle the same site configuration structure.

- **Redis Configuration Patching**: The cache cookbook includes a ruby_block that modifies Redis configuration files after they're created.
  - Mitigation: Create a complete Redis configuration template in Ansible rather than patching existing files.

- **FastAPI Application Deployment**: The fastapi-tutorial cookbook clones a Git repository and sets up a Python environment.
  - Mitigation: Use Ansible's git, pip, and template modules to replicate this functionality.

### Migration Order

1. **cache cookbook** (Priority 1): Relatively simple configuration for Memcached and Redis services.
2. **nginx-multisite cookbook** (Priority 2): Core web server configuration with multiple sites and SSL.
3. **fastapi-tutorial cookbook** (Priority 3): Application deployment with database dependencies.

### Assumptions

1. The target environment will continue to use the same operating systems (Fedora/Ubuntu/CentOS).
2. The Vagrant development environment will be maintained for testing.
3. The same SSL certificate management approach will be used (self-signed certificates for development).
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. PostgreSQL will continue to be the database for the FastAPI application.
6. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate for the target environment.
7. The Redis configuration patching is necessary due to compatibility issues that may need to be addressed differently in Ansible.