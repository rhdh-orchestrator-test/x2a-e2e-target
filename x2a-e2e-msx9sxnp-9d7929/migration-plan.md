# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration scope is moderate, consisting of three primary cookbooks with external dependencies. Based on the analysis, this migration can be completed in approximately 2-3 weeks with a single engineer or 1 week with a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL setup, security hardening

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment, Git repository deployment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Manages cookbook dependencies. Will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Contains node configuration and attributes. Will be replaced by Ansible group_vars and host_vars
- `solo.rb`: Chef configuration file. Will be replaced by ansible.cfg
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef. Will be replaced by Ansible provisioner in Vagrantfile
- `Vagrantfile`: Defines the development VM. Will need updates to use Ansible provisioner instead of Chef

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ as indicated in cookbook metadata
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or custom role
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role from Galaxy (e.g., geerlingguy.redis)
- **PostgreSQL**: Replace with Ansible PostgreSQL role from Galaxy (e.g., geerlingguy.postgresql)

### Security Considerations

- **SSL Configuration**: The nginx-multisite cookbook manages SSL certificates. Migration should preserve certificate paths and configurations
  - Migration approach: Use Ansible's copy/template modules for certificate deployment and nginx configuration
  
- **Redis Authentication**: Redis is configured with password authentication
  - Migration approach: Ensure Redis password is stored in Ansible Vault and properly templated in configuration

- **Security Hardening**: The nginx-multisite cookbook includes security configurations
  - Migration approach: Implement equivalent security configurations using Ansible templates and handlers

- **Vault/secrets management**:
  - Hardcoded credentials detected:
    - Redis password: "redis_secure_password_123" in cache/recipes/default.rb
    - PostgreSQL password: "fastapi_password" in fastapi-tutorial/recipes/default.rb
  - Migration approach: Move all credentials to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The current setup dynamically creates Nginx site configurations based on node attributes
  - Mitigation: Use Ansible templates with loops to generate site configurations from variables

- **Service Dependencies**: The FastAPI application depends on PostgreSQL being configured first
  - Mitigation: Use Ansible's dependency mechanism or explicit ordering in playbooks

- **Configuration Customization**: The Redis configuration includes custom modifications via a ruby_block
  - Mitigation: Create a custom Redis configuration template in Ansible that includes these modifications

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Create Ansible role for Nginx installation and configuration
   - Implement templates for site configurations
   - Configure SSL certificates

2. **cache** (low complexity, independent service)
   - Create Ansible roles for Memcached and Redis
   - Implement secure Redis configuration with password from Ansible Vault

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Create Ansible role for PostgreSQL setup
   - Create Ansible role for FastAPI application deployment
   - Implement systemd service configuration

### Assumptions

1. The current Chef setup is functional and represents the desired end state
2. SSL certificates are managed outside of the automation process (they are referenced but not generated)
3. The Vagrant environment is primarily for development/testing
4. No CI/CD pipeline integration is required for the migration
5. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git is accessible and contains the expected code
6. The current security configurations (fail2ban, ufw, SSH hardening) are sufficient and should be maintained
7. No monitoring or logging solutions need to be migrated
8. The migration will maintain the same directory structure for web content (/var/www/*)
9. The migration will maintain the same service configurations (ports, users, etc.)