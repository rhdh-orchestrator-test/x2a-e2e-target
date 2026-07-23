# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services (Redis and Memcached). The migration to Ansible is estimated to be of moderate complexity, requiring approximately 2-3 weeks for a complete migration with testing. The repository uses Chef Solo with Berkshelf for dependency management and contains 3 local cookbooks with several external dependencies.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall)

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies with version constraints
- `solo.json`: Chef Solo configuration file containing the run list and node attributes
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and logging settings
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef Solo
- `Vagrantfile`: Vagrant configuration for local development/testing environment using Fedora 42

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in the Vagrant development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package module
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package module with custom configuration

### Security Considerations

- **SSL/TLS Management**: The current setup generates self-signed certificates for development. Migration should maintain this capability while allowing for production certificate management.
  - Migration approach: Use Ansible's openssl_* modules for certificate generation and management

- **Firewall Configuration**: The current setup uses UFW with specific rules.
  - Migration approach: Use Ansible's ufw module or firewalld module depending on target OS

- **Fail2ban Integration**: Currently configured for brute force protection.
  - Migration approach: Use Ansible's template module to configure fail2ban

- **SSH Hardening**: Disables root login and password authentication.
  - Migration approach: Use Ansible's lineinfile or template module to configure SSH

- **Vault/secrets management**:
  - Redis password in plaintext in the cache cookbook
  - PostgreSQL credentials in plaintext in the fastapi-tutorial cookbook
  - Migration approach: Use Ansible Vault for secret storage

### Technical Challenges

- **Multi-site Nginx Configuration**: The current setup dynamically generates site configurations based on node attributes.
  - Mitigation: Create Ansible templates that can iterate through site configurations in variables

- **SSL Certificate Generation**: Self-signed certificates are generated for each site.
  - Mitigation: Use Ansible's openssl_* modules to replicate this functionality

- **Service Orchestration**: The current setup manages multiple interdependent services (Nginx, PostgreSQL, Redis, Memcached, FastAPI application).
  - Mitigation: Use Ansible handlers and dependencies to ensure proper service ordering

- **Python Application Deployment**: The current setup clones a Git repository and sets up a Python virtual environment.
  - Mitigation: Use Ansible's git, pip, and template modules to replicate this functionality

### Migration Order

1. **cache cookbook** (low risk, standalone services)
   - Implement Memcached configuration
   - Implement Redis configuration with authentication

2. **nginx-multisite cookbook** (moderate complexity)
   - Implement base Nginx configuration
   - Implement security hardening (fail2ban, ufw, sysctl)
   - Implement SSL certificate generation
   - Implement site configuration templates

3. **fastapi-tutorial cookbook** (high complexity, dependencies)
   - Implement PostgreSQL database setup
   - Implement Python environment setup
   - Implement application deployment
   - Implement systemd service configuration

### Assumptions

1. The target environment will continue to support the same operating systems (Ubuntu 18.04+ or CentOS 7.0+)
2. The Vagrant development environment will be maintained for testing
3. Self-signed certificates are acceptable for development, but production deployment may require integration with Let's Encrypt or other certificate providers
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate for the target environment
6. The current Redis password and PostgreSQL credentials will be migrated as-is, though they should be stored securely in Ansible Vault
7. The current site configurations (test.cluster.local, ci.cluster.local, status.cluster.local) will be maintained