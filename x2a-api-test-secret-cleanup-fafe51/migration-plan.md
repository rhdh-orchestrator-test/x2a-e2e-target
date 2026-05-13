# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- Total: 5-6 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- External dependencies on community cookbooks will need Ansible equivalents
- Security configurations and SSL certificate management require careful handling
- Credential management needs to be migrated to Ansible Vault

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)

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

- `Berksfile`: Dependency management file listing both local cookbooks and external dependencies from Chef Supermarket. Will be replaced by Ansible Galaxy requirements.yml.
- `solo.json`: Contains the Chef run list and configuration attributes. Will be replaced by Ansible inventory variables.
- `solo.rb`: Chef Solo configuration file. Will be replaced by Ansible configuration.
- `Vagrantfile`: Defines the development VM using Fedora 42. Can be adapted for Ansible testing.
- `vagrant-provision.sh`: Shell script to install Chef and run the cookbooks. Will be replaced by Ansible provisioning.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or custom Ansible role
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or DavidWittman.redis

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW. Migration should use Ansible's `ufw` module or `firewalld` module depending on target OS.
- **fail2ban Setup**: Currently configured in security.rb. Use Ansible's `fail2ban` module or a community role.
- **SSH Hardening**: The cookbook disables root login and password authentication. Use Ansible's `lineinfile` module or the `devsec.hardening.ssh_hardening` role.
- **SSL Certificate Management**: Self-signed certificates are generated in the ssl.rb recipe. Use Ansible's `openssl_certificate` module.
- **Vault/secrets management**:
  - Redis password in cache cookbook: 1 hardcoded password
  - PostgreSQL credentials in fastapi-tutorial cookbook: 2 hardcoded passwords
  - These should be migrated to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The Chef cookbook dynamically creates site configurations based on attributes. Ansible templates will need to replicate this logic.
- **SSL Certificate Generation**: The Chef cookbook generates self-signed certificates. Ansible will need to handle certificate creation and management.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL. Ansible handlers and wait_for modules will be needed to ensure proper service startup order.
- **Redis Configuration Hacks**: The Chef cookbook includes a ruby_block to modify Redis configuration files. This will need careful handling in Ansible.

### Migration Order

1. **nginx-multisite** (Priority 1): Core infrastructure component that other services depend on
2. **cache** (Priority 2): Caching services that support the application
3. **fastapi-tutorial** (Priority 3): Application deployment that depends on the other components

### Assumptions

1. The target environment will continue to be Fedora 42 or similar Linux distributions.
2. Self-signed certificates are acceptable for development; production would require proper certificate management.
3. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate for the target environment.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The current directory structure in the target environment (/opt/fastapi-tutorial, /var/www/sites) will be maintained.
6. The current Redis and PostgreSQL passwords are development passwords and will be replaced with proper secrets management.
7. The Vagrant setup is primarily for development and testing, not production deployment.