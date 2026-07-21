# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration scope is moderate, involving three primary cookbooks with external dependencies. Based on the complexity and size of the codebase, an estimated timeline of 2-3 weeks is reasonable for a complete migration to Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL setup, security hardening

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
- `solo.json`: Defines the run list and configuration attributes for Chef Solo
- `solo.rb`: Configures Chef Solo paths and settings
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Defines the Vagrant VM configuration (Fedora 42) with port forwarding and networking

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in Vagrant
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)

### Security Considerations

- **SSL Configuration**: Migration must preserve SSL certificate paths and configurations
  - Current paths: /etc/ssl/certs (certificates) and /etc/ssl/private (private keys)
  - Migration approach: Use Ansible's crypto modules for certificate management

- **Redis Authentication**: Redis is configured with password authentication
  - Current implementation: Hard-coded password in Chef recipe
  - Migration approach: Use Ansible Vault for secure password storage

- **PostgreSQL Credentials**: Database credentials for FastAPI application
  - Current implementation: Hard-coded in Chef recipe and .env file
  - Migration approach: Use Ansible Vault for secure credential storage

- **Security Hardening**: Fail2ban, UFW, and SSH hardening configurations
  - Migration approach: Use dedicated Ansible security roles or tasks

- **Vault/secrets management**:
  - Hard-coded Redis password in cache/recipes/default.rb
  - Hard-coded PostgreSQL credentials in fastapi-tutorial/recipes/default.rb
  - Hard-coded database URL in .env file template
  - Count: 3 sets of credentials detected

### Technical Challenges

- **Multi-site Nginx Configuration**: The current setup dynamically creates Nginx site configurations based on node attributes
  - Mitigation: Use Ansible templates with variable substitution and loops

- **Redis Configuration Hack**: The current setup includes a Ruby block to modify Redis configuration files after installation
  - Mitigation: Create custom Redis configuration template in Ansible

- **FastAPI Deployment**: The current setup clones a Git repository and sets up a Python environment
  - Mitigation: Use Ansible's git module and pip module for equivalent functionality

- **Service Orchestration**: Ensuring proper service restart ordering when configurations change
  - Mitigation: Use Ansible handlers and notify directives to manage service restarts

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate management
   - Implement multi-site configuration
   - Add security hardening

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Set up PostgreSQL database and user
   - Deploy FastAPI application from Git
   - Configure Python environment and dependencies
   - Create systemd service

### Assumptions

1. The target environment will continue to be Fedora/CentOS/Ubuntu Linux systems
2. SSL certificates will be managed in the same locations (/etc/ssl/certs and /etc/ssl/private)
3. The FastAPI application repository will remain available at the specified URL
4. The current directory structure in the target environment (/opt/fastapi-tutorial, /var/www/sites) will be maintained
5. The migration will not involve changes to the application code or database schema
6. The current security configurations (fail2ban, UFW, SSH hardening) are sufficient and should be preserved
7. Redis and Memcached configurations will maintain the same port numbers and basic settings
8. The Nginx multi-site configuration pattern will be preserved in the Ansible implementation