# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated complexity is moderate, with an estimated timeline of 2-3 weeks for a complete migration.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall), sysctl security settings

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Configures caching services including Memcached and Redis
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef configuration file containing the run list and node attributes
- `solo.rb`: Chef configuration file for Chef Solo execution
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration file for local development environment

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary target based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Ansible role
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or `DavidWittman.redis`

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW with specific rules for SSH, HTTP, and HTTPS. Ansible migration should use the `ansible.posix.firewalld` or `community.general.ufw` modules.
- **fail2ban Setup**: The Chef cookbook configures fail2ban for intrusion prevention. Use the `community.general.fail2ban` module in Ansible.
- **SSH Hardening**: The Chef cookbook disables root login and password authentication. Use the `ansible.posix.sshd` module for equivalent configuration.
- **SSL Certificate Management**: Self-signed certificates are generated for each site. Use the `community.crypto.openssl_*` modules for certificate generation.
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi`/`fastapi_password`)
  - No external vault integration is present in the current configuration

### Technical Challenges

- **Multi-site Nginx Configuration**: The Chef cookbook dynamically creates Nginx site configurations based on node attributes. Ansible will need to use templates and loops to achieve the same functionality.
- **SSL Certificate Generation**: The Chef cookbook generates self-signed certificates for each site. Ansible will need to use the `community.crypto` collection to generate certificates.
- **System Tuning**: The Chef cookbook configures sysctl parameters for security. Ansible will need to use the `ansible.posix.sysctl` module.
- **Service Orchestration**: The Chef cookbook manages multiple services with dependencies. Ansible will need to handle service dependencies and notifications.

### Migration Order

1. **cache** (Priority 1): Low complexity, minimal dependencies, good starting point
2. **nginx-multisite** (Priority 2): Moderate complexity, core infrastructure component
3. **fastapi-tutorial** (Priority 3): Higher complexity due to application deployment and database configuration

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions.
2. The Vagrant development environment will be maintained for testing.
3. Self-signed certificates are acceptable for development; no integration with Let's Encrypt or other certificate authorities is required.
4. The FastAPI application source will continue to be pulled from the same Git repository.
5. No CI/CD pipeline integration is currently in place and won't be required for the initial migration.
6. The current hardcoded secrets will be migrated as-is initially, with a recommendation to implement Ansible Vault in a future phase.
7. The current security configurations (fail2ban, UFW, SSH hardening) will be maintained in the Ansible roles.