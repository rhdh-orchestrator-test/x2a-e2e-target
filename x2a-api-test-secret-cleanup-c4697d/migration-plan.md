# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks, handling external dependencies, and ensuring proper security configurations are maintained.

**Scope**: 3 Chef cookbooks with external dependencies
**Complexity**: Medium
**Estimated Timeline**: 3-4 weeks

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)

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

- `Berksfile`: Dependency management for Chef cookbooks - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Chef node configuration with run list and attributes - will be replaced by Ansible inventory variables
- `solo.rb`: Chef configuration file - will be replaced by Ansible configuration
- `Vagrantfile`: Defines development VM - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisioning script for Vagrant - will be replaced by Ansible playbook

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ based on cookbook metadata
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role or redis_* modules

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration approach: Use ansible.builtin.openssl_* modules for certificate generation

- **Firewall Configuration**: 
  - UFW is configured with specific rules
  - Migration approach: Use ansible.posix.ufw module for equivalent configuration

- **Fail2ban Configuration**: 
  - Configured for SSH and web protection
  - Migration approach: Use community.general.fail2ban module

- **SSH Hardening**: 
  - Root login disabled, password authentication disabled
  - Migration approach: Use ansible.posix.sshd_config module

- **Vault/secrets management**:
  - Redis password hardcoded in attributes (`redis_secure_password_123`)
  - PostgreSQL credentials hardcoded in recipe (`fastapi:fastapi_password`)
  - Migration approach: Use Ansible Vault for all credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current setup dynamically creates multiple virtual hosts with SSL
  - Mitigation: Use Ansible loops with templates to create similar dynamic configuration

- **Redis Configuration Patching**: 
  - Description: The current setup uses a ruby_block to modify Redis configuration
  - Mitigation: Use Ansible's lineinfile or template module with proper configuration options

- **Service Orchestration**: 
  - Description: Ensuring proper service restart ordering when configurations change
  - Mitigation: Use Ansible handlers and notify system with proper dependencies

- **PostgreSQL User/Database Creation**: 
  - Description: Current implementation uses direct psql commands
  - Mitigation: Use community.postgresql modules for idempotent database management

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Relatively self-contained with clear configuration patterns

2. **cache** (Priority 2)
   - Dependent services that should be configured before application deployment
   - Moderate complexity with external dependencies

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on both web server and database
   - Most complex with multiple components (Python, Git, PostgreSQL, systemd)

### Assumptions

1. The target environment will continue to use Fedora or similar Linux distributions.
2. Self-signed certificates are acceptable for development; production would require proper certificate management.
3. The current security configurations (fail2ban, ufw, SSH hardening) are required in the migrated solution.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The current Redis and PostgreSQL password configurations are for development only and will be replaced with proper secret management in production.
6. The Nginx sites configuration in solo.json overrides the default attributes in the cookbook.
7. The current setup is designed for a single-node deployment rather than a distributed system.
8. The Vagrant development environment should be preserved with equivalent functionality.