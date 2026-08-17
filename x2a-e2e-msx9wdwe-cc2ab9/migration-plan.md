# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration scope is moderate, consisting of three primary cookbooks with external dependencies. Based on the complexity and size of the codebase, an estimated timeline of 2-3 weeks would be reasonable for a complete migration to Ansible.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL setup, security hardening (fail2ban, ufw)

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
- `solo.json`: Contains node configuration including the run list and attributes for Nginx sites and security settings
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `Vagrantfile`: Defines a Vagrant VM for development/testing using Fedora 42, with port forwarding and network configuration
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef Solo

### Target Details

Based on the source configuration files:

- **Operating System**: Supports Ubuntu (>= 18.04) and CentOS (>= 7.0) as specified in cookbook metadata, with Fedora 42 used in Vagrant development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)

### Security Considerations

- **SSL Configuration**: Migration must preserve SSL certificate paths and configuration for multiple sites
  - Current paths: /etc/ssl/certs (certificates) and /etc/ssl/private (private keys)
  - Migration approach: Use Ansible's crypto modules for certificate management

- **Firewall Configuration**: UFW firewall is enabled in the security settings
  - Migration approach: Use Ansible's ufw module to maintain identical firewall rules

- **SSH Hardening**: SSH configuration disables root login and password authentication
  - Migration approach: Use Ansible's ssh_config module to apply identical hardening

- **Fail2ban**: Enabled in the security settings
  - Migration approach: Use Ansible's package and template modules to configure fail2ban

- **Vault/secrets management**:
  - Redis password hardcoded in cache cookbook (redis_secure_password_123)
  - PostgreSQL credentials hardcoded in fastapi-tutorial cookbook (fastapi/fastapi_password)
  - Migration approach: Move all credentials to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The current setup manages multiple virtual hosts with SSL
  - Mitigation: Use Ansible templates with loops to generate similar site configurations
  - Complexity: Medium

- **Redis Configuration Hack**: The current setup includes a ruby_block to modify Redis configuration
  - Mitigation: Create custom Redis configuration template in Ansible
  - Complexity: Medium

- **FastAPI Application Deployment**: Involves Git clone, venv setup, and systemd service
  - Mitigation: Use Ansible's git, pip, and systemd modules
  - Complexity: Low

- **PostgreSQL User and Database Setup**: Current implementation uses direct psql commands
  - Mitigation: Use Ansible's postgresql_user and postgresql_db modules
  - Complexity: Low

### Migration Order

1. **nginx-multisite cookbook** (Priority 1)
   - Core infrastructure component that other services depend on
   - Relatively self-contained with clear configuration

2. **cache cookbook** (Priority 2)
   - Supports application but not directly user-facing
   - Has external dependencies on memcached and redis

3. **fastapi-tutorial cookbook** (Priority 3)
   - Application deployment that depends on properly configured infrastructure
   - Involves database setup and application configuration

### Assumptions

1. The current Chef setup is functional and represents the desired state
2. SSL certificates are managed outside this configuration (no certificate generation code was found)
3. The Nginx sites configuration in solo.json is complete and represents all required virtual hosts
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git is accessible and contains the correct application code
5. The PostgreSQL database schema is managed by the FastAPI application and not by Chef
6. No custom Chef resources or libraries are in use beyond what was observed in the repository
7. The migration will target the same operating systems (Ubuntu 18.04+ or CentOS 7+)
8. No CI/CD pipeline integration was observed, so no special considerations are needed for automation systems