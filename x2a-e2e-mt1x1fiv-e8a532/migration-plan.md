# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration scope is moderate, consisting of three primary cookbooks with external dependencies. Based on the complexity and number of components, a timeline of 2-3 weeks is estimated for a complete migration to Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL setup, security hardening (fail2ban, firewall)

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

- `Berksfile`: Manages Chef cookbook dependencies - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Contains Chef node attributes and run list - will be replaced by Ansible group_vars and inventory
- `solo.rb`: Chef configuration file - will be replaced by ansible.cfg
- `Vagrantfile`: Defines the development VM - can be adapted for Ansible by changing the provisioner
- `vagrant-provision.sh`: Shell script for Chef provisioning - will be replaced by Ansible playbook calls

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ mentioned in cookbook metadata
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role (e.g., geerlingguy.redis)

### Security Considerations

- **SSL/TLS Configuration**: Migration must preserve SSL certificate paths and configurations
  - Current paths: /etc/ssl/certs (certificates), /etc/ssl/private (private keys)
  - Migration approach: Use ansible.builtin.copy or ansible.builtin.template modules with proper permissions

- **Redis Authentication**: Redis is configured with password authentication
  - Current implementation: Hard-coded password in Chef recipe
  - Migration approach: Move password to Ansible Vault

- **PostgreSQL Authentication**: Database credentials for FastAPI application
  - Current implementation: Hard-coded in Chef recipe
  - Migration approach: Move credentials to Ansible Vault

- **Fail2ban and UFW**: Security hardening is enabled
  - Migration approach: Use dedicated Ansible roles for fail2ban and UFW configuration

- **Vault/secrets management**:
  - 1 Redis password hardcoded in cache/recipes/default.rb
  - 1 PostgreSQL password hardcoded in fastapi-tutorial/recipes/default.rb
  - Environment variables with sensitive data in fastapi-tutorial/.env file

### Technical Challenges

- **Multi-site Nginx Configuration**: The current setup dynamically creates Nginx site configurations based on node attributes
  - Challenge: Preserving the dynamic nature of site creation
  - Mitigation: Use Ansible with_items/loop constructs and templates to achieve similar functionality

- **Redis Configuration Patching**: The Chef recipe includes a ruby_block that modifies Redis configuration files after they're created
  - Challenge: Replicating this behavior in Ansible
  - Mitigation: Use Ansible's lineinfile module or create a complete template that doesn't require post-processing

- **FastAPI Application Deployment**: The current setup clones a Git repository and sets up a Python environment
  - Challenge: Ensuring idempotent deployment with Ansible
  - Mitigation: Use Ansible's git module with version pinning and the pip module with virtualenv support

### Migration Order

1. **nginx-multisite** (Priority 1): Foundation for web services, relatively self-contained
2. **cache** (Priority 2): Supports application performance, depends on external cookbooks
3. **fastapi-tutorial** (Priority 3): Application deployment, depends on PostgreSQL and potentially cache services

### Assumptions

1. The current Chef setup is functional and represents the desired end state
2. Self-signed SSL certificates are acceptable for the migrated solution
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git is accessible and stable
4. The target environment will continue to be Fedora-based systems
5. The Vagrant development environment should be preserved with Ansible provisioning
6. No CI/CD pipeline integration is required as part of the migration
7. The current security configurations (fail2ban, UFW, SSH hardening) should be maintained
8. The current multi-site configuration with three sites (test, ci, status) should be preserved