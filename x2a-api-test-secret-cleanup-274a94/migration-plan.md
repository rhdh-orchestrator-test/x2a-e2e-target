# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup with three primary cookbooks: nginx-multisite, cache, and fastapi-tutorial. The migration to Ansible will involve converting Chef recipes, templates, and attributes to Ansible roles, tasks, templates, and variables. Based on the complexity and interdependencies of the modules, this migration is estimated to be of medium complexity and should take approximately 2-3 weeks to complete with a team of 2 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, fail2ban integration, UFW firewall configuration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4). These will need to be replaced with Ansible Galaxy roles or custom roles.
- `Vagrantfile`: Configures a Fedora 42 VM for development/testing with port forwarding and resource allocation. Will need to be updated to use Ansible provisioner instead of Chef.
- `solo.json`: Defines the Chef run list and configuration attributes. Will be replaced by Ansible inventory and group/host variables.
- `solo.rb`: Chef configuration file that will be replaced by Ansible configuration.
- `vagrant-provision.sh`: Shell script that installs Chef and runs the cookbooks. Will be replaced with Ansible installation and playbook execution.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy `geerlingguy.nginx` role or create a custom Nginx role
- **memcached (~> 6.0)**: Replace with Ansible Galaxy `geerlingguy.memcached` role
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy `geerlingguy.redis` or DavidWittman.redis role
- **PostgreSQL**: Replace with Ansible Galaxy `geerlingguy.postgresql` role

### Security Considerations

- **SSL Certificate Management**: 
  - The current implementation generates self-signed certificates using OpenSSL
  - Migration approach: Use Ansible's `openssl_*` modules for certificate generation or consider integrating with Let's Encrypt using `geerlingguy.certbot`

- **Firewall Configuration**: 
  - Current implementation uses UFW with specific rules
  - Migration approach: Use Ansible's `ufw` module to maintain the same firewall rules

- **fail2ban Integration**: 
  - Current implementation installs and configures fail2ban
  - Migration approach: Create an Ansible role for fail2ban configuration or use an existing Galaxy role

- **SSH Hardening**: 
  - Current implementation disables root login and password authentication
  - Migration approach: Use Ansible's `lineinfile` module or the `devsec.hardening.ssh_hardening` Galaxy role

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL password is hardcoded in the recipe (`fastapi_password`)
  - Migration approach: Move these credentials to Ansible Vault and use `ansible-vault` to manage secrets

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: The current implementation dynamically creates multiple virtual hosts based on node attributes
  - Mitigation: Use Ansible's with_items/loop to iterate through a list of sites defined in variables

- **SSL Certificate Generation**: 
  - Challenge: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's openssl_* modules to generate certificates or integrate with Let's Encrypt

- **Redis Configuration Hack**: 
  - Challenge: The current implementation includes a ruby_block to modify Redis configuration
  - Mitigation: Create a proper Redis configuration template in Ansible or use lineinfile module for specific changes

- **PostgreSQL User and Database Creation**: 
  - Challenge: Current implementation uses inline shell commands
  - Mitigation: Use Ansible's postgresql_* modules for proper idempotent database management

### Migration Order

1. **cache** (Priority 1 - low risk, foundational service)
   - Simple configuration of Memcached and Redis
   - Few dependencies on other modules

2. **nginx-multisite** (Priority 2 - moderate complexity)
   - Core web server configuration
   - Security hardening components
   - Multiple templates and configurations

3. **fastapi-tutorial** (Priority 3 - highest complexity)
   - Depends on PostgreSQL
   - Involves application deployment, virtual environment setup
   - Systemd service configuration

### Assumptions

1. The target environment will continue to be Fedora 42 or a compatible Linux distribution that supports the same packages.
2. Self-signed certificates are acceptable for the migrated solution, or a proper certificate authority will be specified.
3. The same security hardening measures (fail2ban, UFW, SSH hardening) are required in the Ansible implementation.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The current Redis and PostgreSQL passwords are for development only and will be replaced with proper secrets management in production.
6. The Vagrant development environment will be maintained, but switched to use Ansible provisioning instead of Chef.
7. The current directory structure in the target system (/opt/fastapi-tutorial, /var/www/sites, etc.) should be preserved.
8. The current security headers and SSL configuration in Nginx should be maintained in the Ansible implementation.