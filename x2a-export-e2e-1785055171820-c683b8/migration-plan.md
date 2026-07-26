# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated complexity is moderate, with security configurations and SSL certificate management requiring special attention. Based on the repository analysis, a 2-3 week timeline is recommended for a complete migration.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificate generation
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup, fail2ban integration, UFW firewall configuration, security hardening

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment setup, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef run list and node attributes configuration
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Defines development VM using Fedora 42, with port forwarding and network configuration
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ mentioned in cookbook metadata
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks with custom configuration

### Security Considerations

- **SSL Certificate Management**: Self-signed certificates are generated for development. Migration should maintain this capability while allowing for production certificates.
  - Migration approach: Use Ansible's openssl_* modules for certificate generation and management

- **Firewall Configuration**: UFW is configured with specific rules for web and SSH access.
  - Migration approach: Use Ansible's community.general.ufw module to configure firewall rules

- **fail2ban Integration**: Configured to protect against brute force attacks.
  - Migration approach: Use Ansible's community.general.fail2ban module or custom configuration templates

- **SSH Hardening**: Root login disabled and password authentication disabled.
  - Migration approach: Use Ansible's openssh_* modules or lineinfile to configure SSH settings

- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL database credentials in fastapi-tutorial cookbook: "fastapi:fastapi_password"
  - Consider using Ansible Vault for these credentials in the migrated solution

### Technical Challenges

- **Multi-site Nginx Configuration**: The current setup uses Chef templates to generate site configurations dynamically based on attributes. Ansible will need equivalent templating.
  - Mitigation: Use Ansible templates with similar variable structures to generate site configurations

- **Service Orchestration**: The current setup has interdependent services (Nginx, PostgreSQL, FastAPI application).
  - Mitigation: Use Ansible handlers and proper task ordering to ensure services are configured and restarted in the correct sequence

- **SSL Certificate Generation**: Self-signed certificates are generated conditionally.
  - Mitigation: Use Ansible's openssl_* modules with conditional execution based on variables

- **System Tuning**: Security-related sysctl parameters are configured.
  - Mitigation: Use Ansible's sysctl module to apply the same parameters

### Migration Order

1. **cache** (Priority 1): Lowest complexity, handles Redis and Memcached configuration
2. **nginx-multisite** (Priority 2): Moderate complexity, handles web server and security configurations
3. **fastapi-tutorial** (Priority 3): Highest complexity, involves application deployment, database setup, and service configuration

### Assumptions

1. The target environment will continue to be Fedora-based, with potential support for Ubuntu and CentOS as mentioned in the cookbook metadata.
2. Self-signed certificates are acceptable for development, but the Ansible solution should allow for easy substitution with production certificates.
3. The current security configurations (fail2ban, UFW, SSH hardening) are appropriate and should be maintained in the Ansible solution.
4. The FastAPI application source will continue to be pulled from the same Git repository.
5. The PostgreSQL database configuration will remain similar, with local database and user creation.
6. The Redis and Memcached configurations will maintain the same basic settings, including Redis password authentication.
7. The multi-site Nginx configuration pattern will be preserved, with the same site names and document roots.