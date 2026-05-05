# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks, handling external dependencies, and ensuring proper security configurations are maintained.

**Scope**: 3 Chef cookbooks with dependencies on external cookbooks
**Complexity**: Medium (standard web stack with some security hardening)
**Estimated Timeline**: 3-4 weeks (1 week per cookbook + testing)

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and fail2ban/ufw firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site SSL configuration, security headers, fail2ban integration, UFW firewall rules

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file listing external cookbook dependencies (nginx, memcached, redisio)
- `solo.json`: Node configuration with run list and attributes for the Chef run
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Provisioning script for Vagrant environment
- `Vagrantfile`: Vagrant configuration for development environment using Fedora 42

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or local development

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)

### Security Considerations

- **SSL/TLS Configuration**: The nginx-multisite cookbook generates self-signed certificates for development. In Ansible, use either ansible.posix.openssl_* modules or community.crypto collection for certificate management.
- **Firewall Rules**: UFW firewall rules need to be migrated using ansible.posix.ufw module.
- **fail2ban**: Configuration needs to be migrated using templates and service management.
- **SSH Hardening**: SSH configuration hardening (disabling root login, password authentication) should be migrated using templates or lineinfile modules.
- **Vault/secrets management**:
  - Redis password in cache cookbook (hardcoded as 'redis_secure_password_123')
  - PostgreSQL database credentials in fastapi-tutorial cookbook (hardcoded as 'fastapi_password')
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple virtual hosts with SSL will require careful template design in Ansible.
- **Self-signed Certificate Generation**: The current implementation uses inline shell commands for certificate generation, which will need to be replaced with Ansible's crypto modules.
- **PostgreSQL User/Database Creation**: The current implementation uses inline shell commands, which should be replaced with Ansible's postgresql_* modules.
- **Python Application Deployment**: The virtual environment and dependency management will need to be handled with Ansible's pip and git modules.

### Migration Order

1. **nginx-multisite** (Priority 1): Core infrastructure component that other services depend on
2. **cache** (Priority 2): Supporting service with external dependencies
3. **fastapi-tutorial** (Priority 3): Application layer that depends on infrastructure being in place

### Assumptions

1. The target environment will continue to be Fedora 42 or a compatible Linux distribution.
2. Self-signed certificates are acceptable for development, but production would require proper certificate management.
3. The current security configurations (fail2ban, ufw, SSH hardening) are required in the migrated solution.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The current Redis and PostgreSQL passwords are development credentials and will be replaced with proper secrets management in production.
6. The current directory structure in /opt/ and /var/ will be maintained in the migrated solution.
7. The systemd service configurations will remain similar.