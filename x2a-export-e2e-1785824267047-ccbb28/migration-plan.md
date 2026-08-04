# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated complexity is moderate, with an estimated timeline of 2-3 weeks for a complete migration.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW, custom Nginx configuration templates

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database setup
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external dependencies with version constraints.
- `solo.json`: Chef Solo configuration file defining the run list and node attributes.
- `solo.rb`: Chef Solo configuration file for cookbook paths and other settings.
- `Vagrantfile`: Defines the development environment using Vagrant with Fedora 42.
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef.

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` module and templates
- **memcached (~> 6.0)**: Replace with Ansible's `memcached` module or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible's `redis` module or direct package installation and configuration

### Security Considerations

- **SSL Certificate Management**: The current setup generates self-signed certificates. Migration should maintain this capability or integrate with Let's Encrypt.
  - Migration approach: Use Ansible's `openssl_*` modules for certificate generation or `community.crypto.acme_certificate` for Let's Encrypt integration.

- **Firewall Configuration**: UFW is configured with specific rules for HTTP, HTTPS, and SSH.
  - Migration approach: Use Ansible's `ufw` module to maintain identical firewall rules.

- **Fail2ban Setup**: Configured for brute force protection.
  - Migration approach: Use Ansible's `template` module to configure fail2ban with identical settings.

- **SSH Hardening**: Root login disabled and password authentication disabled.
  - Migration approach: Use Ansible's `lineinfile` or `template` module to configure SSH settings.

- **Vault/secrets management**: 
  - Redis password in `cache/recipes/default.rb`
  - PostgreSQL credentials in `fastapi-tutorial/recipes/default.rb`
  - Migration approach: Use Ansible Vault to store these credentials securely.

### Technical Challenges

- **Multi-site Nginx Configuration**: The current setup uses Chef attributes and templates to configure multiple Nginx sites dynamically.
  - Mitigation: Create Ansible templates that can iterate through site configurations defined in variables.

- **Service Dependencies**: The FastAPI application depends on PostgreSQL, and Nginx depends on the FastAPI service being available.
  - Mitigation: Use Ansible handlers and conditional checks to ensure services are started in the correct order.

- **SSL Certificate Generation**: The current setup generates self-signed certificates for each site.
  - Mitigation: Create an Ansible role specifically for certificate management that can be reused across sites.

### Migration Order

1. **cache** (low risk, moderate value): Start with the caching services as they have the fewest dependencies and are relatively self-contained.
2. **fastapi-tutorial** (moderate complexity): Next, migrate the FastAPI application deployment as it depends on PostgreSQL but not on other services.
3. **nginx-multisite** (high complexity, dependencies): Finally, migrate the Nginx configuration as it depends on the FastAPI application being available and has the most complex configuration.

### Assumptions

1. The target environment will continue to be Fedora 42 or a compatible Linux distribution.
2. The current network configuration and port mappings will remain the same.
3. Self-signed certificates are acceptable for the migrated solution (rather than requiring Let's Encrypt or other CA-signed certificates).
4. The FastAPI application source code will remain available at the same Git repository.
5. The PostgreSQL database schema and user requirements will remain unchanged.
6. The Redis password and PostgreSQL credentials will need to be stored securely in Ansible Vault.
7. The current directory structure for web content (`/var/www/[site]`) will be maintained.