# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration scope is moderate, involving three primary cookbooks with external dependencies. Based on the complexity and number of components, the estimated timeline for migration is 2-3 weeks with 1-2 engineers.

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
    - Key Features: Python virtual environment, Git repository deployment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Manages cookbook dependencies - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Contains node configuration and attributes - will be replaced by Ansible group_vars and host_vars
- `solo.rb`: Chef configuration file - will be replaced by ansible.cfg
- `Vagrantfile`: Defines development VM - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisioning script for Vagrant - will be replaced by Ansible playbooks

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)

### Security Considerations

- **SSL Configuration**: Migration must preserve SSL certificate paths and configurations
  - Certificate path: /etc/ssl/certs
  - Private key path: /etc/ssl/private
  - Self-signed certificates are currently used

- **Redis Authentication**: Redis is configured with password authentication
  - Password: "redis_secure_password_123" (should be moved to Ansible Vault)

- **PostgreSQL Authentication**: Database credentials need secure handling
  - Username: fastapi
  - Password: fastapi_password (should be moved to Ansible Vault)

- **Security Hardening**: The following security measures need to be maintained:
  - fail2ban configuration
  - UFW (Uncomplicated Firewall) setup
  - SSH hardening (root login disabled, password authentication disabled)
  - Nginx security headers and configurations

- **Vault/secrets management**:
  - 2 hardcoded database credentials in fastapi-tutorial/default.rb
  - 1 hardcoded Redis password in cache/default.rb
  - No Chef Vault or encrypted data bags detected

### Technical Challenges

- **Multi-site Nginx Configuration**: The current setup dynamically creates Nginx site configurations based on node attributes. Ansible templates will need to replicate this dynamic behavior.

- **FastAPI Application Deployment**: The current setup clones a Git repository and sets up a Python virtual environment. Ansible's git and pip modules will need to be configured to handle this workflow.

- **Service Dependencies**: The current setup manages service dependencies (e.g., FastAPI depends on PostgreSQL). Ansible handlers and meta dependencies will need to be configured to maintain these relationships.

- **Configuration File Modifications**: The Redis configuration has custom modifications applied via a ruby_block. This will need to be replicated using Ansible's lineinfile or template modules.

### Migration Order

1. **nginx-multisite cookbook** (moderate complexity)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate management
   - Configure multiple sites
   - Implement security hardening

2. **cache cookbook** (low complexity)
   - Set up Memcached
   - Configure Redis with authentication

3. **fastapi-tutorial cookbook** (high complexity)
   - Set up PostgreSQL database
   - Deploy FastAPI application from Git
   - Configure Python environment
   - Set up systemd service

### Assumptions

1. The current deployment is targeting a single server environment, as all components (web server, caching, application, database) are deployed to the same host.

2. SSL certificates are self-signed and generated during deployment, not pre-existing.

3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git is publicly accessible and will remain available.

4. The current setup does not appear to use centralized secrets management, with passwords hardcoded in recipes.

5. The Nginx configuration is relatively simple, with static content for each site.

6. No complex orchestration or clustering is present in the current setup.

7. No backup or disaster recovery procedures are defined in the current configuration.

8. The migration will maintain the same overall architecture and deployment strategy.