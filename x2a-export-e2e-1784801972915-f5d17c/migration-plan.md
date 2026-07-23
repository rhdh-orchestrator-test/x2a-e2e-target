# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with FastAPI application backend and caching services (Redis and Memcached). The migration to Ansible is estimated to be of medium complexity, with approximately 2-3 weeks of effort required for a complete migration.

The repository uses Chef Solo with Berkshelf for dependency management and contains three local cookbooks with several external dependencies. The infrastructure is designed to run on Fedora 42 (based on Vagrant configuration) and includes security hardening, SSL certificate management, and multiple virtual hosts configuration.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and configuration management
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall)

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Manages cookbook dependencies, including local and external cookbooks from the Chef Supermarket. Migration will require mapping these dependencies to Ansible Galaxy roles or collections.
- `solo.json`: Contains the run list and configuration data for Chef Solo. This will be migrated to Ansible inventory variables and group_vars.
- `solo.rb`: Chef Solo configuration file. Will be replaced by Ansible configuration.
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef. Will need to be updated to use Ansible provisioner.
- `Vagrantfile`: Defines the development VM configuration using Fedora 42. Will need updates to use Ansible provisioner instead of Chef.

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary, from Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Libvirt (from Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or the `ansible.posix.nginx` collection
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role or custom tasks
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` role or the `community.general.redis` module

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW with specific rules. Migrate to Ansible's `ansible.posix.firewalld` or `community.general.ufw` modules.
- **Fail2ban Setup**: Migrate fail2ban configuration to Ansible using the `community.general.fail2ban` module.
- **SSH Hardening**: The cookbook disables root login and password authentication. Implement using Ansible's `ansible.posix.ssh_config` module.
- **SSL Certificate Management**: Self-signed certificates are generated for each site. Use Ansible's `community.crypto` collection for certificate management.
- **Vault/secrets management**: 
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - These should be migrated to Ansible Vault or an external secrets management solution

### Technical Challenges

- **Multi-site Nginx Configuration**: The Chef cookbook dynamically creates Nginx site configurations based on attributes. This will require careful templating in Ansible.
- **SSL Certificate Generation**: Self-signed certificates are generated for each site. This logic needs to be replicated in Ansible using the `community.crypto` collection.
- **Service Orchestration**: The Chef recipes manage service dependencies (e.g., PostgreSQL before FastAPI). Ansible's handlers and meta dependencies will need to be used to maintain this ordering.
- **Idempotent Execution**: Some Chef resources use `not_if` guards to ensure idempotence. These will need to be translated to Ansible's `when` conditions and `changed_when` directives.

### Migration Order

1. **cache cookbook** (low complexity): Simple configuration of Memcached and Redis services
2. **nginx-multisite cookbook** (medium complexity): Nginx configuration with multiple sites and SSL
3. **fastapi-tutorial cookbook** (medium complexity): Application deployment with database dependencies

### Assumptions

1. The current deployment is using Chef Solo, not Chef Server, making the migration to Ansible more straightforward.
2. The target environment will continue to be Fedora 42 or a similar Linux distribution.
3. Self-signed certificates are acceptable for the migrated solution (production environments might require Let's Encrypt integration).
4. The FastAPI application source will continue to be pulled from the same Git repository.
5. The current security configurations (fail2ban, ufw, SSH hardening) are required in the Ansible solution.
6. The PostgreSQL database will be installed locally as it is in the current configuration.
7. The Redis password and PostgreSQL credentials will need to be secured in the Ansible solution.