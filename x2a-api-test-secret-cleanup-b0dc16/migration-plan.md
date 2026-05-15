# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web server environment with caching services and a FastAPI application. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 2-3 weeks, with moderate complexity due to the interdependencies between services and security configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site-specific configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site SSL configuration, fail2ban integration, UFW firewall setup, custom security configurations

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, service management

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4). Migration will require identifying equivalent Ansible Galaxy roles or creating custom roles.
- `Vagrantfile`: Defines the development environment using Fedora 42. Will need to be updated to use Ansible provisioner instead of Chef.
- `solo.json`: Contains the run list and configuration attributes. Will be converted to Ansible group_vars or host_vars.
- `solo.rb`: Chef configuration file. Not needed in Ansible.
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef. Will need to be replaced with Ansible provisioning script.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role from Galaxy or create a custom role
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role or equivalent
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` role or equivalent
- **PostgreSQL**: Replace with Ansible's `geerlingguy.postgresql` role or equivalent

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should maintain this functionality or improve it with Let's Encrypt integration.
- **Firewall Configuration**: UFW firewall rules need to be migrated to equivalent Ansible UFW module tasks.
- **fail2ban Configuration**: Current fail2ban setup needs to be migrated to Ansible tasks.
- **System Hardening**: sysctl security configurations need to be migrated to Ansible.
- **SSH Hardening**: SSH configuration (disabling root login, password authentication) needs to be migrated.
- **Vault/secrets management**: 
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - These should be moved to Ansible Vault

### Technical Challenges

- **Custom Resource Migration**: The `lineinfile` custom resource in nginx-multisite needs to be replaced with Ansible's native `lineinfile` module.
- **Template Conversion**: All ERB templates need to be converted to Jinja2 format for Ansible.
- **Configuration Hierarchy**: Chef's attribute precedence model differs from Ansible's variable precedence. Care must be taken to ensure configurations are applied correctly.
- **Service Dependencies**: The current setup has interdependencies between services (e.g., FastAPI depends on PostgreSQL). These dependencies need to be maintained in the Ansible playbook ordering.

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - First migrate the basic Nginx configuration
   - Then add SSL certificate generation
   - Finally add security configurations (fail2ban, UFW)

2. **cache** (low complexity, standalone service)
   - Migrate Memcached configuration
   - Migrate Redis configuration with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Migrate PostgreSQL installation and configuration
   - Migrate Python environment setup
   - Migrate application deployment and service configuration

### Assumptions

1. The target environment will continue to be Fedora 42 as specified in the Vagrantfile.
2. Self-signed certificates are acceptable for development; production would likely require a different approach.
3. The current security configurations are appropriate for the target environment.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The current Redis and PostgreSQL passwords are for development only and will be replaced with secure passwords stored in Ansible Vault for production.
6. The current directory structure in the target environment (/opt/server/*, /var/www/*) should be maintained.
7. The current port configurations (80, 443, 6379 for Redis, etc.) should be maintained.