# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration scope is moderate, involving three primary cookbooks with external dependencies. Based on the complexity and number of components, the estimated timeline for migration is 2-3 weeks with 1 dedicated engineer.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL setup, security hardening (fail2ban, firewall)

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
- `solo.json`: Contains Chef run list and configuration data for Nginx sites and security settings
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `Vagrantfile`: Defines a Fedora 42 VM for local development with port forwarding and network configuration
- `vagrant-provision.sh`: Shell script that installs Chef and runs the cookbooks in the Vagrant environment

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) as specified in cookbook metadata. The Vagrantfile uses Fedora 42.
- **Virtual Machine Technology**: Vagrant with libvirt provider as indicated in the Vagrantfile
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)

### Security Considerations

- **SSL Configuration**: Migration must preserve SSL certificate paths and configuration
  - Current paths: /etc/ssl/certs (certificates) and /etc/ssl/private (private keys)
  - Migration approach: Use ansible.builtin.copy or ansible.builtin.template modules with proper permissions

- **Fail2ban Configuration**: Security hardening must be maintained
  - Migration approach: Use community.general.fail2ban module or dedicated role

- **Firewall (UFW)**: Firewall rules must be preserved
  - Migration approach: Use community.general.ufw module

- **SSH Hardening**: SSH configuration must maintain security settings
  - Current settings: Root login disabled, password authentication disabled
  - Migration approach: Use ansible.posix.ssh_config module

- **Vault/secrets management**:
  - Redis password hardcoded in recipe: "redis_secure_password_123"
  - PostgreSQL credentials hardcoded in recipe: "fastapi:fastapi_password"
  - Environment variables in .env file for FastAPI application
  - Migration approach: Use Ansible Vault for all credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: The current setup dynamically creates Nginx site configurations based on node attributes
  - Mitigation: Use Ansible templates with variable loops to achieve similar functionality

- **Redis Configuration Hack**: The current setup includes a ruby_block to modify Redis configuration files after they're created
  - Mitigation: Create a custom Redis configuration template in Ansible rather than modifying files after creation

- **FastAPI Application Deployment**: The current setup clones a Git repository and sets up a Python environment
  - Mitigation: Use Ansible's git module and pip module to achieve similar functionality

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation and configuration
   - Add SSL configuration
   - Add security hardening
   - Add multi-site configuration

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis configuration with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Set up PostgreSQL database
   - Deploy FastAPI application
   - Configure systemd service

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/Fedora systems
2. SSL certificates will be managed in the same way (self-signed or provided externally)
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
4. The current security configurations (fail2ban, UFW, SSH hardening) are sufficient and should be maintained
5. The current directory structure for web content (/var/www/[site]) will be maintained
6. Redis and Memcached configurations don't require significant tuning beyond what's in the current recipes
7. The PostgreSQL database schema is managed by the FastAPI application and doesn't require additional migration steps