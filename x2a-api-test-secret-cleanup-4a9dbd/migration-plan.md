# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 3-4 weeks, with moderate complexity due to the interdependencies between components and security configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificates
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database provisioning, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies with version constraints
- `solo.json`: Chef configuration file containing the run list and node attributes for Nginx sites and security settings
- `solo.rb`: Chef configuration file defining paths and log settings
- `Vagrantfile`: Defines a Fedora 42 VM for local development with port forwarding and resource allocation
- `vagrant-provision.sh`: Shell script that installs Chef and runs the cookbooks in the Vagrant environment

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with the development environment using Fedora 42
- **Virtual Machine Technology**: Vagrant with libvirt provider for local development
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or collection (e.g., `ansible.posix.nginx`)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., `geerlingguy.memcached`)
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role (e.g., `geerlingguy.redis`)

### Security Considerations

- **Firewall Configuration**: The migration must preserve UFW firewall rules for SSH, HTTP, and HTTPS
  - Migration approach: Use Ansible's `ufw` module to configure firewall rules
  
- **Fail2ban Setup**: Intrusion prevention system must be maintained
  - Migration approach: Use Ansible's `template` module to configure fail2ban with the same jail settings

- **SSH Hardening**: SSH configuration disables root login and password authentication
  - Migration approach: Use Ansible's `lineinfile` module or `template` module to configure SSH settings

- **SSL Certificate Management**: Self-signed certificates are generated for each virtual host
  - Migration approach: Use Ansible's `openssl_certificate` module to generate self-signed certificates

- **Vault/secrets management**: 
  - Redis password is hardcoded in the Chef recipe
  - PostgreSQL credentials are hardcoded in the FastAPI recipe
  - Migration approach: Use Ansible Vault to encrypt sensitive values and reference them in playbooks

### Technical Challenges

- **Multi-site Configuration**: The Nginx setup supports multiple virtual hosts with dynamic configuration
  - Mitigation: Use Ansible's template module with Jinja2 loops to generate site configurations from variables

- **Service Interdependencies**: The FastAPI application depends on PostgreSQL, and the web server depends on the application
  - Mitigation: Use Ansible handlers and proper task ordering to ensure services start in the correct order

- **Redis Configuration Hack**: The Chef recipe includes a Ruby block to modify Redis configuration files
  - Mitigation: Create a custom Redis configuration template in Ansible that properly handles the configuration without post-processing

- **Environment File Management**: The FastAPI application requires an environment file with database credentials
  - Mitigation: Use Ansible templates with Vault-encrypted variables to securely generate the environment file

### Migration Order

1. **cache** (Priority 1): Relatively simple cookbook with external dependencies, provides foundation for other services
2. **nginx-multisite** (Priority 2): Core infrastructure component with security configurations
3. **fastapi-tutorial** (Priority 3): Application deployment that depends on other components

### Assumptions

1. The target environment will continue to support the same operating systems (Ubuntu 18.04+ or CentOS 7.0+)
2. The Vagrant development environment will be maintained for testing
3. Self-signed certificates are acceptable for development (not production)
4. The FastAPI application source repository will remain available at the specified URL
5. The current security configurations are appropriate for the target environment
6. No additional monitoring or logging solutions need to be integrated
7. The current Redis and Memcached configurations meet performance requirements
8. PostgreSQL will continue to be the database backend for the FastAPI application