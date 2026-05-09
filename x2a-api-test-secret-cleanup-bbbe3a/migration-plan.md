# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup with three main cookbooks: nginx-multisite, cache, and fastapi-tutorial. The migration to Ansible will involve converting Chef recipes, templates, and attributes to Ansible roles, tasks, templates, and variables. Based on the complexity and number of cookbooks, this migration is estimated to be of medium complexity and should take approximately 2-3 weeks for a skilled Ansible developer.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), custom Nginx configurations

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (both local and external from Chef Supermarket). Migration will require mapping these dependencies to Ansible Galaxy roles or custom roles.
- `solo.json`: Contains the Chef run list and configuration data. This will be converted to Ansible inventory variables.
- `solo.rb`: Chef configuration file that sets paths and log levels. Will be replaced by Ansible configuration.
- `Vagrantfile`: Defines the development VM configuration. Can be adapted to use Ansible provisioner instead of Chef.
- `vagrant-provision.sh`: Shell script that installs Chef and runs the cookbooks. Will be replaced with Ansible provisioning.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible community.general.nginx or geerlingguy.nginx role
- **memcached (~> 6.0)**: Replace with geerlingguy.memcached role
- **redisio (~> 7.2.4)**: Replace with geerlingguy.redis role

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should maintain this capability or integrate with Ansible's crypto modules.
  - Migration approach: Use Ansible's `openssl_*` modules for certificate generation and management.

- **Firewall Configuration**: The current setup uses UFW for firewall management.
  - Migration approach: Use Ansible's `ufw` module or `firewalld` module depending on target OS.

- **SSH Hardening**: SSH configuration is modified to disable root login and password authentication.
  - Migration approach: Use Ansible's `lineinfile` module or the `ansible-hardening` role.

- **Fail2ban Configuration**: Fail2ban is installed and configured for intrusion prevention.
  - Migration approach: Create Ansible tasks using the `template` module for fail2ban configuration.

- **Vault/secrets management**: 
  - Redis password is hardcoded in the cache cookbook
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook
  - Migration approach: Use Ansible Vault to encrypt sensitive values

### Technical Challenges

- **Multi-site Nginx Configuration**: The current implementation dynamically creates Nginx site configurations based on attributes. 
  - Mitigation: Use Ansible loops with templates to achieve similar functionality.

- **Redis Configuration Hack**: The cache cookbook includes a ruby_block to modify Redis configuration files after they're created.
  - Mitigation: Create a custom Redis configuration template in Ansible that doesn't require post-processing.

- **PostgreSQL User/Database Creation**: The current implementation uses shell commands to create PostgreSQL users and databases.
  - Mitigation: Use Ansible's `postgresql_*` modules for more idiomatic database management.

- **Service Management**: Different approaches are used for managing services across the cookbooks.
  - Mitigation: Standardize on Ansible's `systemd` module for service management.

### Migration Order

1. **nginx-multisite** (Priority 1): This is the foundation for the web infrastructure and should be migrated first.
2. **cache** (Priority 2): The caching layer depends on properly configured web servers.
3. **fastapi-tutorial** (Priority 3): The application deployment depends on both web and cache layers.

### Assumptions

1. The target environment will continue to be Fedora-based systems (the Vagrantfile specifies Fedora 42).
2. Self-signed SSL certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or similar).
3. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate for the target environment.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The current Redis and PostgreSQL password values are development credentials and will be replaced with proper secrets management in production.
6. The Nginx sites configuration in solo.json overrides the default attributes in the cookbook.
7. The current implementation assumes the www-data user exists, which may need adjustment for Fedora (which typically uses apache or nginx users).