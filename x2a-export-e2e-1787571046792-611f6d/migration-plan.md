# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration scope includes 3 Chef cookbooks with moderate complexity. Based on the repository analysis, we estimate a 2-3 week timeline for complete migration, with the most complex components being the Nginx multi-site configuration and security hardening.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site-specific configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), custom Nginx configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Manages cookbook dependencies, including external dependencies from Chef Supermarket (nginx, memcached, redisio)
- `solo.json`: Contains node configuration data including Nginx site definitions and security settings
- `solo.rb`: Chef Solo configuration file defining cookbook paths and log settings
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Defines the Vagrant VM configuration (Fedora 42) with port forwarding and networking

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in Vagrant development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW with specific rules for SSH, HTTP, and HTTPS. Migration should maintain these security controls using Ansible's ufw module.
- **fail2ban Integration**: The Chef cookbook configures fail2ban for brute force protection. This should be migrated using Ansible's fail2ban modules.
- **SSH Hardening**: The Chef cookbook disables root login and password authentication. These settings should be preserved in the Ansible playbooks.
- **SSL Certificate Management**: Self-signed certificates are generated for each site. Consider using Ansible's openssl modules or certbot for Let's Encrypt integration.
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - No external vault integration is present in the current implementation

### Technical Challenges

- **Multi-site Nginx Configuration**: The Chef cookbook dynamically creates site configurations based on attributes. Ansible will need to replicate this dynamic configuration using templates and variables.
- **SSL Certificate Generation**: The Chef cookbook generates self-signed certificates for each site. Ansible will need to handle certificate generation and management.
- **System Hardening**: The Chef cookbook applies various security hardening measures. Ansible will need to replicate these using appropriate modules.
- **Service Orchestration**: The Chef cookbook manages service dependencies (e.g., FastAPI depends on PostgreSQL). Ansible will need to handle these dependencies correctly.

### Migration Order

1. **cache cookbook** (low risk, standalone): Migrate Memcached and Redis configuration
2. **nginx-multisite cookbook** (moderate complexity): Migrate Nginx configuration, SSL certificate generation, and security hardening
3. **fastapi-tutorial cookbook** (high complexity): Migrate Python application deployment, PostgreSQL configuration, and systemd service management

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/Fedora systems
2. Self-signed certificates are acceptable for development/testing (production would likely use proper certificates)
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
4. The current security settings (firewall rules, SSH hardening) are appropriate for the target environment
5. The current Redis and PostgreSQL passwords are for development only and will be replaced with proper secrets management in production
6. The Vagrant development environment will be maintained for testing
7. No CI/CD pipeline integration is required for the initial migration