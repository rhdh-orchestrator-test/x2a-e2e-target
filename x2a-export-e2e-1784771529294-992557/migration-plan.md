# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated complexity is medium, with an estimated timeline of 2-3 weeks for a complete migration, including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database creation, systemd service configuration, Git repository cloning

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificates
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, Redis configuration patching

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints.
- `solo.json`: Configuration data for Chef Solo, containing the run list and configuration parameters for the cookbooks.
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings.
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef.
- `Vagrantfile`: Vagrant configuration file defining the VM settings (Fedora 42), network configuration, and provisioning method.

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ mentioned in cookbook metadata
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or community.general.memcached module
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or community.general.redis module

### Security Considerations

- **SSL Certificate Management**: Self-signed certificates are generated for each site. Migration should maintain this capability using Ansible's openssl_* modules.
- **Firewall Configuration**: UFW firewall rules are configured. Replace with Ansible's ufw module or firewalld for Fedora.
- **Fail2ban Configuration**: Fail2ban is configured for intrusion prevention. Use Ansible's template module to configure fail2ban.
- **SSH Hardening**: SSH configuration includes disabling root login and password authentication. Use Ansible's lineinfile or template module.
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - Database connection string in the FastAPI .env file contains credentials
  - These should be migrated to Ansible Vault

### Technical Challenges

- **Multi-site Configuration**: The nginx-multisite cookbook dynamically creates site configurations based on node attributes. This pattern needs to be replicated in Ansible using loops and templates.
- **SSL Certificate Generation**: Self-signed certificates are generated conditionally. This logic needs to be preserved in Ansible.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL. This dependency chain needs to be maintained in Ansible.
- **Redis Configuration Hack**: The cache cookbook includes a ruby_block to modify Redis configuration files after they're created. This will need a custom approach in Ansible, possibly using lineinfile or replace module.
- **Git Repository Management**: The FastAPI application is cloned from a Git repository. This will need to be managed with Ansible's git module.

### Migration Order

1. **cache** (moderate complexity): Start with the caching services as they have the fewest dependencies.
2. **nginx-multisite** (moderate complexity): Migrate the Nginx configuration next, as it's a core infrastructure component.
3. **fastapi-tutorial** (high complexity): Finally, migrate the application deployment, which depends on both Nginx and PostgreSQL.

### Assumptions

1. The target environment will continue to be Fedora 42 or similar Linux distribution.
2. The Vagrant setup will be maintained for development/testing.
3. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate for the target environment.
4. Self-signed certificates are acceptable for the target environment (not production).
5. The FastAPI application source will continue to be pulled from the same Git repository.
6. The current Redis and Memcached configurations meet performance requirements.
7. No additional monitoring or logging requirements beyond what's in the current configuration.
8. The PostgreSQL database will be installed locally on the same server as the FastAPI application.