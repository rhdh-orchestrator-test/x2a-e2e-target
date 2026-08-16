# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration scope is moderate, involving three primary cookbooks with external dependencies. Based on the complexity and number of components, we estimate a 2-3 week timeline for complete migration, with the most complex components being the multi-site Nginx configuration and the FastAPI application deployment.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site-specific configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site virtual hosts, SSL configuration, security hardening (fail2ban, firewall)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment, Git repository deployment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints.
- `solo.json`: Chef configuration file defining the run list and node attributes. Contains Nginx site configurations and security settings.
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings.
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef. Installs Chef and Berkshelf, downloads dependencies, and runs Chef Solo.
- `Vagrantfile`: Defines the Vagrant VM configuration using Fedora 42, with port forwarding and network settings.

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in the Vagrant environment.
- **Virtual Machine Technology**: Vagrant with libvirt provider.
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible `nginx` role from Ansible Galaxy or custom role
- **memcached (~> 6.0)**: Replace with Ansible `geerlingguy.memcached` role
- **redisio (~> 7.2.4)**: Replace with Ansible `geerlingguy.redis` role or custom Redis role

### Security Considerations

- **SSL Configuration**: Migration must preserve SSL certificate paths and configurations for multiple sites
  - Current paths: `/etc/ssl/certs` for certificates, `/etc/ssl/private` for private keys
  - Migration approach: Use Ansible `copy` or `template` modules with proper permissions

- **Fail2ban Configuration**: Security hardening via fail2ban must be preserved
  - Migration approach: Use Ansible `community.general.fail2ban` module or custom role

- **Firewall (UFW)**: Firewall rules must be migrated
  - Migration approach: Use Ansible `community.general.ufw` module

- **SSH Hardening**: SSH security settings (disable root login, password authentication)
  - Migration approach: Use Ansible `ansible.posix.ssh_config` module

- **Vault/secrets management**: 
  - Redis password in `cookbooks/cache/recipes/default.rb` (hardcoded as 'redis_secure_password_123')
  - PostgreSQL credentials in `cookbooks/fastapi-tutorial/recipes/default.rb` (user: 'fastapi', password: 'fastapi_password')
  - Migration approach: Use Ansible Vault for all credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: The current setup manages multiple Nginx sites with SSL. 
  - Mitigation: Create a flexible Ansible role with templates that can handle multiple site configurations from variables.

- **PostgreSQL Database Setup**: The FastAPI application requires specific database setup.
  - Mitigation: Use the `community.postgresql` collection for database and user management.

- **Python Application Deployment**: The FastAPI application requires virtual environment setup and dependency management.
  - Mitigation: Create a dedicated Ansible role for Python application deployment with proper idempotency checks.

- **Service Management**: Multiple services need to be configured and managed (Nginx, Redis, Memcached, PostgreSQL, FastAPI application).
  - Mitigation: Use Ansible's service module with proper handlers and notifications.

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation and configuration
   - Add SSL support
   - Implement multi-site configuration
   - Add security hardening

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Set up PostgreSQL database and user
   - Deploy application code from Git
   - Configure Python environment and dependencies
   - Set up systemd service

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/Fedora systems.
2. SSL certificates will be managed in the same way (self-signed or provided externally).
3. The FastAPI application repository at `https://github.com/dibanez/fastapi_tutorial.git` will remain available.
4. The current security configurations (fail2ban, UFW, SSH hardening) are sufficient and should be maintained.
5. The current directory structure for web content (`/var/www/[site_name]`) will be preserved.
6. Redis and Memcached configurations don't require significant changes beyond what's currently specified.
7. The PostgreSQL database schema is managed by the FastAPI application and doesn't require additional migration steps.
8. The Vagrant development environment will be replaced with an equivalent Ansible-based setup.