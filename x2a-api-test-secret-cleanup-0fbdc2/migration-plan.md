# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to Ansible roles and playbooks. The estimated timeline for this migration is 3-4 weeks, with moderate complexity due to the interdependencies between components and security configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), custom Nginx configurations

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, service management

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints.
- `solo.json`: Chef configuration file defining the run list and node attributes. Contains site configurations and security settings.
- `solo.rb`: Chef configuration file specifying file paths and log settings.
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef.
- `Vagrantfile`: Defines the Vagrant VM configuration using Fedora 42 as the base box with port forwarding and networking setup.

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), but the Vagrantfile specifies Fedora 42 as the development environment.
- **Virtual Machine Technology**: Vagrant with libvirt provider (based on Vagrantfile configuration).
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package installation and configuration

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should maintain this capability while allowing for integration with Let's Encrypt or other certificate providers.
  - Migration approach: Use Ansible's openssl_* modules or community.crypto collection

- **Firewall Configuration (UFW)**: The current implementation configures UFW with specific rules.
  - Migration approach: Use Ansible's ufw module to configure firewall rules

- **Fail2ban Configuration**: The current implementation installs and configures fail2ban.
  - Migration approach: Use Ansible's template module to configure fail2ban

- **SSH Hardening**: The current implementation disables root login and password authentication.
  - Migration approach: Use Ansible's lineinfile module or ssh_config module from community.general collection

- **Vault/secrets management**:
  - Redis password in cache cookbook (hardcoded as 'redis_secure_password_123')
  - PostgreSQL user password in fastapi-tutorial cookbook (hardcoded as 'fastapi_password')
  - Database connection string in .env file for FastAPI application
  - Count: 3 hardcoded credentials detected

### Technical Challenges

- **Multi-site Nginx Configuration**: The current implementation dynamically generates site configurations based on node attributes. The Ansible implementation will need to maintain this flexibility.
  - Mitigation: Use Ansible templates with variable loops to generate site configurations

- **Service Interdependencies**: The FastAPI application depends on PostgreSQL, and the web server depends on the application being available.
  - Mitigation: Use Ansible handlers and wait_for modules to ensure services are available before proceeding

- **SSL Certificate Generation**: The current implementation generates self-signed certificates for each site.
  - Mitigation: Use Ansible's openssl_* modules to generate certificates or integrate with certbot for Let's Encrypt certificates

- **Redis Configuration Hack**: The current implementation includes a ruby_block to modify Redis configuration files after they're created.
  - Mitigation: Create a proper Redis configuration template in Ansible rather than modifying files after creation

### Migration Order

1. **cache** (Priority 1): Relatively simple configuration for Memcached and Redis services
2. **nginx-multisite** (Priority 2): More complex with multiple templates and security configurations
3. **fastapi-tutorial** (Priority 3): Most complex with application deployment, database setup, and service configuration

### Assumptions

1. The target environment will continue to be either Ubuntu (>= 18.04) or CentOS (>= 7.0), with Fedora 42 as the development environment.
2. The self-signed SSL certificates are for development only, and production would use proper certificates.
3. The hardcoded passwords in the Chef recipes are for development only and would be replaced with Ansible Vault secrets in production.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate for the target environment.
6. The current Nginx site configurations (test.cluster.local, ci.cluster.local, status.cluster.local) will remain the same.
7. The PostgreSQL database configuration for the FastAPI application will remain the same.
8. The Redis configuration with authentication will remain the same.
9. The Vagrant development environment will continue to be used for testing.