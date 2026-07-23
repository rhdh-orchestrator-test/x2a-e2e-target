# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a web application stack consisting of a FastAPI Python application, Nginx web server with multi-site support, and caching services (Memcached and Redis). The migration to Ansible is estimated to be of medium complexity with approximately 2-3 weeks of effort required for a complete migration.

The repository contains 3 Chef cookbooks with clear responsibilities and moderate complexity. The migration will require converting Chef resources to Ansible modules, addressing security configurations, and maintaining the multi-environment support currently implemented.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **fastapi-tutorial**:
    - Description: Deploys a Python FastAPI application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database creation, systemd service configuration, Git repository deployment

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple virtual hosts, SSL support, and security hardening
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multiple site configurations, SSL certificate generation, security hardening (fail2ban, UFW firewall), custom Nginx configuration templates

- **cache**:
    - Description: Sets up caching services including Memcached and Redis
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Memcached configuration, Redis installation and configuration, service management

### Infrastructure Files

- `Berksfile`: Chef Berkshelf dependency manager file listing cookbook dependencies (nginx, memcached, redisio). Migration will require mapping these to Ansible Galaxy roles or collections.
- `solo.json`: Chef Solo configuration file defining the run list and attributes. Will be replaced by Ansible inventory and group_vars.
- `solo.rb`: Chef Solo Ruby configuration file. Will be replaced by ansible.cfg.
- `Vagrantfile`: Vagrant configuration for local development. Can be preserved with modifications to use Ansible provisioner instead of Chef.
- `vagrant-provision.sh`: Shell script for initial Vagrant VM provisioning. Will need updates to install Ansible instead of Chef.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu (inferred from apt package manager usage in recipes and UFW firewall configuration)
- **Virtual Machine Technology**: VirtualBox (based on Vagrant configuration)
- **Cloud Platform**: Not specified (appears to be targeting on-premises or generic cloud VMs)

## Migration Approach

### Key Dependencies to Address

- **nginx (cookbook)**: Replace with Ansible `nginx` role from Galaxy or use the `ansible.builtin.package` and `ansible.builtin.template` modules to install and configure Nginx
- **memcached (cookbook)**: Replace with Ansible `geerlingguy.memcached` role or use `ansible.builtin.package` and `ansible.builtin.template` modules
- **redisio (cookbook)**: Replace with Ansible `geerlingguy.redis` role or use `ansible.builtin.package` and `ansible.builtin.template` modules
- **PostgreSQL**: Replace with Ansible `geerlingguy.postgresql` role or use `ansible.builtin.package` and `ansible.postgresql_*` modules

### Security Considerations

- **SSL Certificates**: The nginx-multisite cookbook generates self-signed SSL certificates. Migrate to using Ansible's `community.crypto.openssl_*` modules or consider integrating with Let's Encrypt using `community.crypto.acme_*` modules.
- **UFW Firewall Rules**: Convert UFW firewall rules to use Ansible's `community.general.ufw` module.
- **fail2ban Configuration**: Migrate fail2ban configuration to use Ansible's `community.general.fail2ban` module.
- **SSH Hardening**: Preserve SSH security configurations using Ansible's `ansible.posix.authorized_key` and `ansible.builtin.template` modules for sshd_config.
- **Vault/secrets management**: 
  - PostgreSQL credentials in fastapi-tutorial cookbook (username: fastapi, password: fastapi_password)
  - Redis password in cache cookbook
  - Recommend migrating to Ansible Vault for secure credential storage

### Technical Challenges

- **Multi-site Nginx Configuration**: The nginx-multisite cookbook uses a complex template system for managing multiple virtual hosts. This will require careful migration to Ansible templates while preserving the dynamic site configuration capability.
- **Service Orchestration**: The FastAPI application depends on PostgreSQL being configured first. Ensure proper dependency handling in Ansible playbooks using tags, handlers, and proper task ordering.
- **Python Environment Management**: The fastapi-tutorial cookbook sets up Python virtual environments. Use Ansible's `ansible.builtin.pip` module with the `virtualenv` parameter to maintain this functionality.
- **Dynamic Configuration**: Several cookbooks use attributes for configuration. Map these to Ansible variables in group_vars, host_vars, or role defaults.

### Migration Order

1. **cache cookbook** (Priority 1): Low complexity, minimal dependencies, good starting point
2. **fastapi-tutorial cookbook** (Priority 2): Moderate complexity with database dependencies
3. **nginx-multisite cookbook** (Priority 3): Highest complexity due to templates and security configurations

### Assumptions

1. The target environment will continue to be Ubuntu-based systems
2. PostgreSQL will remain the database of choice for the FastAPI application
3. The multi-site configuration for Nginx is required in the migrated solution
4. Development workflow will continue to use Vagrant for local testing
5. Self-signed SSL certificates are acceptable (no requirement for Let's Encrypt integration)
6. The current security measures (UFW, fail2ban, SSH hardening) are required in the migrated solution