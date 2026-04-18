# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three primary cookbooks (nginx-multisite, cache, and fastapi-tutorial) along with their dependencies. The environment appears to be a development/testing setup using Vagrant with Fedora 42.

Based on the repository analysis, this is a **medium complexity** migration that should take approximately **2-3 weeks** to complete, including testing and documentation. The migration will require careful handling of security configurations, SSL certificates, and service dependencies.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, fail2ban integration, UFW firewall configuration

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

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4)
- `Vagrantfile`: Configures a Fedora 42 VM with port forwarding (80→8080, 443→8443) and private networking
- `solo.json`: Defines the Chef run list and configuration attributes for nginx sites and security settings
- `solo.rb`: Configures Chef Solo paths and logging
- `vagrant-provision.sh`: Bash script to install Chef and Berkshelf, and run the Chef provisioning process

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified (appears to be local development environment)

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or collection (e.g., `geerlingguy.nginx`)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., `geerlingguy.memcached`)
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role (e.g., `geerlingguy.redis`)
- **PostgreSQL**: Replace with Ansible PostgreSQL role (e.g., `geerlingguy.postgresql`)

### Security Considerations

- **SSL Certificate Management**: 
  - Current implementation generates self-signed certificates
  - Migration approach: Use Ansible `community.crypto.x509_certificate` module for certificate generation
  - Consider integrating with Let's Encrypt for production environments

- **Firewall Configuration**: 
  - Current implementation uses UFW
  - Migration approach: Use Ansible `ansible.posix.firewalld` module for Fedora or maintain UFW with `community.general.ufw` module

- **Fail2ban Integration**:
  - Migration approach: Use Ansible to deploy fail2ban configuration templates

- **SSH Hardening**:
  - Current implementation disables root login and password authentication
  - Migration approach: Use Ansible `ansible.posix.sshd_config` module or dedicated SSH hardening role

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL password is hardcoded in the recipe (`fastapi_password`)
  - Migration approach: Use Ansible Vault for storing sensitive credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation dynamically generates site configurations from node attributes
  - Mitigation strategy: Use Ansible templates with variable loops to generate site configurations

- **SSL Certificate Generation**: 
  - Description: Self-signed certificates are generated for each site
  - Mitigation strategy: Use Ansible's crypto modules to generate certificates or integrate with Let's Encrypt

- **Service Dependencies**: 
  - Description: The FastAPI application depends on PostgreSQL being configured first
  - Mitigation strategy: Use Ansible handlers and proper task ordering to ensure dependencies are met

- **Redis Configuration Hack**: 
  - Description: The current implementation includes a ruby_block to modify Redis configuration
  - Mitigation strategy: Create a proper Redis configuration template in Ansible

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Configure virtual hosts
   - Implement security hardening (fail2ban, firewall, headers)

2. **cache** (low complexity, independent service)
   - Configure Memcached
   - Configure Redis with authentication
   - Ensure proper service management

3. **fastapi-tutorial** (high complexity, depends on database)
   - Set up PostgreSQL database and user
   - Deploy application from Git
   - Configure Python environment and dependencies
   - Create systemd service

### Assumptions

1. The target environment will continue to be Fedora-based systems
2. Self-signed certificates are acceptable for development (production would require proper certificates)
3. The same security hardening measures should be maintained in the Ansible implementation
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current directory structure in the target environment (/opt/fastapi-tutorial, /var/www/*, etc.) should be preserved
6. The current network configuration with multiple virtual hosts will be maintained
7. Redis and Memcached configurations will remain similar to the current setup
8. PostgreSQL database name and credentials can remain the same