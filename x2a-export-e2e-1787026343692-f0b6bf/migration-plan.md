# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 2-3 weeks, with moderate complexity due to the interdependencies between services and security configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw)
    - Verification: Contains recipes/default.rb at cookbooks/nginx-multisite/recipes/default.rb

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database configuration, systemd service management
    - Verification: Contains recipes/default.rb at cookbooks/fastapi-tutorial/recipes/default.rb

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration
    - Verification: Contains recipes/default.rb at cookbooks/cache/recipes/default.rb

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies.
- `solo.json`: Chef configuration data with run list and node attributes for Nginx sites, SSL, and security settings.
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings.
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef.
- `Vagrantfile`: Defines the Vagrant VM configuration using Fedora 42 with port forwarding and networking.

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in the Vagrant environment.
- **Virtual Machine Technology**: Vagrant with libvirt provider (based on Vagrantfile configuration).
- **Cloud Platform**: Not specified, appears to be designed for local development/testing.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks with custom configuration

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW with specific rules for SSH, HTTP, and HTTPS. Migration should use Ansible's `ufw` module to maintain identical rules.
- **fail2ban Setup**: The cookbook configures fail2ban for intrusion prevention. Use Ansible's `template` module to create equivalent configuration.
- **SSH Hardening**: The cookbook disables root login and password authentication. Use Ansible's `lineinfile` module to make these changes.
- **SSL Certificate Management**: Self-signed certificates are generated for each site. Use Ansible's `openssl_*` modules to generate equivalent certificates.
- **Vault/secrets management**: 
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi`/`fastapi_password`)
  - These should be migrated to Ansible Vault or another secrets management solution

### Technical Challenges

- **Multi-site Configuration**: The nginx-multisite cookbook dynamically creates site configurations based on attributes. This will require careful templating in Ansible to maintain the same flexibility.
- **Service Interdependencies**: The FastAPI application depends on PostgreSQL, and the Nginx configuration depends on the SSL certificates. These dependencies need to be carefully managed in the Ansible playbook.
- **Custom Security Configurations**: The security hardening includes custom sysctl settings and SSH configurations that need to be preserved in the Ansible roles.
- **Redis Configuration Hack**: The cache cookbook includes a Ruby block to modify Redis configuration files after they're created. This will need a custom approach in Ansible.

### Migration Order

1. **cache** (Priority 1): Relatively simple cookbook with standard Memcached and Redis configurations.
2. **nginx-multisite** (Priority 2): Core infrastructure component with security configurations that other services depend on.
3. **fastapi-tutorial** (Priority 3): Application deployment that depends on PostgreSQL and should be configured after the infrastructure components.

### Assumptions

1. The target environment will continue to use the same operating systems (Ubuntu/CentOS/Fedora).
2. The self-signed SSL certificates approach is acceptable for the migrated solution.
3. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate for the target environment.
4. The Vagrant development environment will be maintained, but Chef provisioning will be replaced with Ansible.
5. The current hardcoded credentials will be replaced with a more secure approach in the Ansible implementation.
6. The FastAPI application source code will continue to be pulled from the same Git repository.
7. The current directory structure for web content and application code will be maintained.