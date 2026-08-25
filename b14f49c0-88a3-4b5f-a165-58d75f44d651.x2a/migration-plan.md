# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-service web application environment. The migration scope includes three Chef cookbooks that manage:

1. A multi-site Nginx web server with SSL configuration
2. Caching services (Memcached and Redis)
3. A FastAPI Python application with PostgreSQL database

The overall complexity is **moderate**, with an estimated timeline of 2-3 weeks for complete migration. The repository has a clear structure with well-defined cookbooks and minimal custom resources, making it suitable for a straightforward migration to Ansible roles.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall)

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

- `Berksfile`: Manages cookbook dependencies, including external cookbooks from Chef Supermarket (nginx, memcached, redisio)
- `solo.json`: Contains node configuration data including site definitions, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file defining cookbook paths and log settings
- `Vagrantfile`: Likely contains VM configuration for local development (not analyzed in detail)
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04 or newer / CentOS 7 or newer (both supported in metadata.rb files)
- **Virtual Machine Technology**: VirtualBox (inferred from Vagrant usage)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role or direct package management
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` role or direct package management

### Security Considerations

- **Firewall Configuration**: The `nginx-multisite` cookbook configures UFW firewall rules that need to be migrated to Ansible's `ufw` module
- **Fail2ban Setup**: Fail2ban configuration in the security.rb recipe needs to be migrated to Ansible tasks
- **SSL Certificate Management**: Self-signed certificates are generated in the ssl.rb recipe; consider using Ansible's `openssl_*` modules
- **SSH Hardening**: SSH security configurations (disabling root login, password authentication) should be migrated to Ansible's `lineinfile` or templates
- **Vault/secrets management**:
  - Redis password in cache cookbook: `redis_secure_password_123` (hardcoded)
  - PostgreSQL credentials in fastapi-tutorial cookbook: username `fastapi` with password `fastapi_password` (hardcoded)
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of Nginx site configurations based on node attributes will need careful translation to Ansible templates and variables
- **SSL Certificate Management**: Self-signed certificate generation logic needs to be replicated or replaced with Let's Encrypt integration
- **Service Dependencies**: Ensuring proper ordering of service deployments (e.g., PostgreSQL before FastAPI application)
- **Template Conversion**: Chef templates (.erb) will need to be converted to Jinja2 format for Ansible

### Migration Order

1. **cache cookbook** (low complexity, foundational services)
   - Implement Memcached configuration
   - Implement Redis with authentication

2. **nginx-multisite cookbook** (moderate complexity)
   - Implement base Nginx configuration
   - Implement security hardening (fail2ban, firewall)
   - Implement SSL certificate management
   - Implement virtual host configuration

3. **fastapi-tutorial cookbook** (moderate complexity, depends on PostgreSQL)
   - Implement PostgreSQL database setup
   - Implement Python application deployment
   - Implement systemd service configuration

### Assumptions

1. The target environment will continue to be Ubuntu/CentOS based systems
2. Self-signed certificates are acceptable for the migrated solution (or alternative certificate management will be provided)
3. The same security hardening measures are required in the Ansible implementation
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current Redis and PostgreSQL passwords are development passwords that will be replaced with proper secrets management in production
6. The Nginx sites configuration in solo.json will be maintained in the Ansible inventory or group variables