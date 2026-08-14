# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with FastAPI backend and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for migration is 2-3 weeks, with moderate complexity due to the security configurations and SSL certificate management.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database setup
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment, Git repository deployment, PostgreSQL database configuration, systemd service

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and SSL certificate management
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)

- **cache**:
    - Description: Caching services configuration (Memcached and Redis)
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks - will be replaced by Ansible requirements.yml
- `solo.json`: Chef node configuration - will be replaced by Ansible inventory variables
- `solo.rb`: Chef configuration file - will be replaced by ansible.cfg
- `Vagrantfile`: Vagrant configuration for development environment - can be adapted for Ansible
- `vagrant-provision.sh`: Provisioning script for Vagrant - will be replaced by Ansible playbook

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package installation

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should maintain this functionality or improve it with Let's Encrypt integration.
- **Security Hardening**: Several security measures need to be preserved:
  - fail2ban configuration for intrusion prevention
  - ufw firewall rules (SSH, HTTP, HTTPS)
  - sysctl security settings
  - SSH hardening (root login disabled, password authentication disabled)
- **Vault/secrets management**: 
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL credentials in fastapi-tutorial cookbook: User "fastapi" with password "fastapi_password"
  - These should be migrated to Ansible Vault

### Technical Challenges

- **Multi-site Configuration**: The Nginx configuration supports multiple virtual hosts with SSL. This structure needs to be preserved in Ansible templates.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL, and the web server depends on the application being available. These dependencies need to be managed in the Ansible playbook.
- **SSL Certificate Generation**: Self-signed certificate generation logic needs to be replicated or improved.
- **Idempotency**: Ensuring that commands like database creation are idempotent in Ansible as they are in Chef.

### Migration Order

1. **cache** (low complexity): Start with the cache cookbook as it has the simplest configuration and fewer dependencies.
2. **fastapi-tutorial** (medium complexity): Next, migrate the FastAPI application deployment, including PostgreSQL setup.
3. **nginx-multisite** (high complexity): Finally, migrate the Nginx configuration with its security hardening and SSL certificate management.

### Assumptions

1. The target environment will continue to be Fedora 42 or a compatible Linux distribution.
2. Self-signed certificates are acceptable for the migrated solution (not production-ready).
3. The same directory structure for web content and SSL certificates will be maintained.
4. The Vagrant development environment will be preserved but modified to use Ansible provisioning.
5. No changes to the application code or functionality are required during migration.
6. The current security settings (fail2ban, ufw, SSH hardening) are appropriate and should be maintained.
7. The Redis and Memcached configurations do not require significant changes.
8. PostgreSQL database creation and user setup should remain similar to the current implementation.