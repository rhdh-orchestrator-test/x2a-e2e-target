# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx server with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated complexity is moderate, with security configurations and SSL certificate management requiring special attention. The estimated timeline for migration is 2-3 weeks for a single developer, or 1-2 weeks with a team of 2-3 developers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, fail2ban integration, UFW firewall rules

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment, Git repository deployment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints.
- `solo.json`: Chef run list and node attribute configuration. Defines which recipes to run and their configuration parameters.
- `solo.rb`: Chef Solo configuration file. Defines cookbook paths and logging settings.
- `Vagrantfile`: Defines the development VM configuration using Vagrant. Uses Fedora 42 as the base box with port forwarding.
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef. Installs Chef and Berkshelf, then runs Chef Solo.

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or local development

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` module or community.general collection
- **memcached (~> 6.0)**: Replace with Ansible's `memcached` module or community.general collection
- **redisio (~> 7.2.4)**: Replace with Ansible's `redis` module or community.general collection

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should maintain this capability while allowing for easy integration with Let's Encrypt or other certificate providers.
- **Firewall Configuration**: UFW rules need to be migrated to equivalent Ansible UFW module tasks.
- **fail2ban Configuration**: Configuration needs to be migrated to Ansible tasks.
- **SSH Hardening**: SSH configuration hardening (disabling root login, password authentication) needs to be migrated.
- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL database credentials in fastapi-tutorial cookbook: "fastapi:fastapi_password"
  - No external vault integration detected, passwords are hardcoded in recipes

### Technical Challenges

- **Multi-site Configuration**: The nginx-multisite cookbook uses a data-driven approach to configure multiple sites. This pattern needs to be replicated in Ansible using loops and templates.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL, and the web server depends on the application being available. These dependencies need to be properly managed in Ansible.
- **SSL Certificate Generation**: Self-signed certificate generation logic needs to be migrated to Ansible tasks.
- **System Hardening**: Security configurations need to be carefully migrated to ensure no security gaps are introduced.

### Migration Order

1. **cache** (Priority 1): Lowest complexity, minimal dependencies
2. **fastapi-tutorial** (Priority 2): Moderate complexity, depends on PostgreSQL
3. **nginx-multisite** (Priority 3): Highest complexity, depends on the application being available

### Assumptions

1. The target environment will continue to be Fedora-based, with support for Ubuntu and CentOS.
2. The current self-signed certificate approach is acceptable for the migrated solution.
3. The current hardcoded passwords will be migrated to Ansible Vault for improved security.
4. The Vagrant development environment will be maintained but updated to use Ansible provisioning.
5. The current directory structure for web content (/var/www/[site]) will be maintained.
6. The PostgreSQL database structure and user permissions will remain the same.
7. The Redis and Memcached configurations will remain functionally equivalent.
8. The security hardening measures (fail2ban, UFW, SSH hardening) will be maintained.