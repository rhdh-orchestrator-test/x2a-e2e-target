# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated complexity is moderate, with an estimated timeline of 2-3 weeks for a complete migration.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies from Chef Supermarket and local paths. Migration will require mapping these dependencies to Ansible Galaxy roles or creating custom roles.
- `solo.json`: Contains the run list and configuration data that will need to be converted to Ansible variables.
- `solo.rb`: Chef configuration file that won't be needed in Ansible.
- `Vagrantfile`: Defines the development VM environment, which can be adapted for Ansible testing.
- `vagrant-provision.sh`: Chef provisioning script that will be replaced with Ansible provisioning.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting local VMs

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or create a custom role based on the current configuration
- **memcached (~> 6.0)**: Replace with Ansible Galaxy's `geerlingguy.memcached` role or equivalent
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy's `geerlingguy.redis` role or equivalent

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. In Ansible, use the `openssl_*` modules or consider integrating with Let's Encrypt via `geerlingguy.certbot`.
- **Firewall Configuration**: The current implementation uses UFW. In Ansible, use the `ufw` module or `firewalld` module depending on the target OS.
- **Fail2ban Configuration**: Migrate the fail2ban configuration using Ansible's `template` module and service management.
- **SSH Hardening**: Current implementation disables root login and password authentication. Use Ansible's `lineinfile` or `template` module to configure SSH.
- **Vault/secrets management**:
  - Redis password is hardcoded in the `cache` cookbook
  - PostgreSQL credentials are hardcoded in the `fastapi-tutorial` cookbook
  - Consider using Ansible Vault for these secrets

### Technical Challenges

- **Multi-site Nginx Configuration**: The current implementation uses templates to generate site configurations. Ansible will need to replicate this dynamic site generation using templates and loops.
- **SSL Certificate Generation**: The current implementation generates self-signed certificates. Ansible will need to handle certificate generation or integration with certificate authorities.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL and potentially the cache services. Ansible playbooks will need to respect these dependencies.
- **Python Environment Management**: The current implementation creates and manages Python virtual environments. Ansible will need to replicate this using the `pip` module with the `virtualenv` parameter.

### Migration Order

1. **cache** (low complexity): Start with the cache cookbook as it has the simplest configuration and fewer dependencies.
2. **nginx-multisite** (moderate complexity): Migrate the Nginx configuration next, as it's a core component but doesn't depend on the application.
3. **fastapi-tutorial** (moderate complexity): Finally, migrate the application deployment, which depends on the other components.

### Assumptions

1. The target environment will continue to be Fedora or a similar Linux distribution.
2. Self-signed certificates are acceptable for the migrated solution, or a proper certificate authority will be specified.
3. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate for the target environment.
4. The FastAPI application source will continue to be available at the specified Git repository.
5. The PostgreSQL database will be installed locally as in the current configuration.
6. The current Redis and Memcached configurations meet the application requirements.
7. The Nginx site configurations (test.cluster.local, ci.cluster.local, status.cluster.local) will remain the same.
8. The current VM resource allocations (2GB RAM, 2 CPUs) are sufficient for the application.