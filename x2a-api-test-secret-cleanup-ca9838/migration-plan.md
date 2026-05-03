# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, security configurations, and service deployments. Based on the complexity and scope, this migration is estimated to require 3-4 weeks with 1-2 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and fail2ban integration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup, security hardening (fail2ban, UFW firewall), sysctl security settings

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file listing cookbook dependencies (nginx, memcached, redisio). Migration will require mapping these to Ansible Galaxy roles or collections.
- `Vagrantfile`: VM configuration for development/testing. Can be preserved with minimal changes to use Ansible provisioner instead of Chef.
- `solo.json`: Chef node attributes and run list. Will need to be converted to Ansible inventory variables.
- `solo.rb`: Chef configuration file. Will be replaced by Ansible configuration.
- `vagrant-provision.sh`: Provisioning script for Vagrant. Will need to be updated to install and run Ansible instead of Chef.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible community.nginx collection or geerlingguy.nginx role
- **memcached (~> 6.0)**: Replace with geerlingguy.memcached role
- **redisio (~> 7.2.4)**: Replace with geerlingguy.redis role or community.redis collection

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the strong TLS configuration (TLSv1.2/1.3 only, secure ciphers)
- **fail2ban Integration**: Convert fail2ban configuration to Ansible tasks or use a dedicated role like geerlingguy.security
- **UFW Firewall Rules**: Migrate firewall rules to Ansible UFW module or firewalld for Fedora
- **System Hardening**: Convert sysctl security settings to Ansible sysctl module tasks
- **Vault/secrets management**:
  - Redis password in cache cookbook (hardcoded as 'redis_secure_password_123')
  - PostgreSQL database credentials in fastapi-tutorial cookbook (hardcoded as 'fastapi_password')
  - SSL/TLS certificate and key management for nginx-multisite
  - Total credentials detected: 2 hardcoded passwords, plus SSL certificate generation

### Technical Challenges

- **Multi-site Nginx Configuration**: The current setup dynamically generates site configurations based on node attributes. This pattern needs to be preserved using Ansible templates and variables.
- **SSL Certificate Generation**: Self-signed certificates are currently generated using OpenSSL commands. This should be migrated to Ansible's openssl_* modules.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL. This dependency chain needs to be maintained in Ansible with proper handlers and notifications.
- **Configuration File Modifications**: The Redis configuration has a hack to modify the config file after installation. This will need a cleaner approach in Ansible.

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - First migrate the basic Nginx installation and configuration
   - Then add the security hardening components (fail2ban, UFW, sysctl)
   - Finally implement the SSL and multi-site configuration

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Set up PostgreSQL database and user
   - Deploy the FastAPI application from Git
   - Configure the Python environment and dependencies
   - Create and enable the systemd service

### Assumptions

1. The target environment will continue to be Fedora 42 with libvirt, as specified in the Vagrantfile.
2. The current security configurations (TLS settings, fail2ban, UFW, sysctl) are appropriate for the target environment.
3. Self-signed certificates are acceptable for the migration (production would likely use Let's Encrypt or other CA).
4. The hardcoded passwords in the Chef recipes will be replaced with Ansible Vault encrypted variables.
5. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
6. The current directory structure for deployed applications (/opt/server/*, /opt/fastapi-tutorial) will be maintained.
7. The nginx site configurations will continue to use the same virtual host names (test.cluster.local, ci.cluster.local, status.cluster.local).
8. The PostgreSQL database name and user will remain the same (fastapi_db, fastapi).