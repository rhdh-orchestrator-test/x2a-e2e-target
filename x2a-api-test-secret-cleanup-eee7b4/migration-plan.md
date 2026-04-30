# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated complexity is moderate, with security configurations and multiple service integrations requiring careful attention.

**Timeline Estimate:**
- Planning & Setup: 1 week
- Core Infrastructure Migration: 2 weeks
- Testing & Validation: 1 week
- Documentation & Knowledge Transfer: 1 week
- **Total**: 5 weeks

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, fail2ban integration, UFW firewall configuration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file listing cookbook dependencies (nginx, memcached, redisio)
- `solo.json`: Chef configuration file defining the run list and node attributes
- `solo.rb`: Chef configuration file defining paths and log settings
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration file defining VM settings and networking

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks
- **PostgreSQL**: Replace with Ansible postgresql role or postgresql_* modules

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration approach: Use Ansible's openssl_* modules to generate certificates

- **Firewall Configuration**: 
  - UFW is configured with specific rules
  - Migration approach: Use Ansible's ufw module or firewalld module depending on target OS

- **Fail2ban Integration**: 
  - Fail2ban is configured for intrusion prevention
  - Migration approach: Use Ansible to deploy fail2ban configuration files

- **SSH Hardening**: 
  - Root login disabled, password authentication disabled
  - Migration approach: Use Ansible's lineinfile module or ssh_config module

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe
  - PostgreSQL credentials are hardcoded in the recipe
  - Migration approach: Use Ansible Vault for storing sensitive credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Maintaining the dynamic generation of site configurations
  - Mitigation: Use Ansible templates with loops to generate site configurations

- **SSL Certificate Generation**: 
  - Challenge: Ensuring certificates are only generated when needed
  - Mitigation: Use Ansible's check mode and stat module to verify certificate existence

- **Service Dependencies**: 
  - Challenge: Ensuring proper service startup order (PostgreSQL before FastAPI)
  - Mitigation: Use Ansible handlers and meta dependencies to manage service order

- **Redis Configuration Customization**: 
  - Challenge: The current setup uses a ruby_block to modify Redis configuration
  - Mitigation: Use Ansible's lineinfile or template module with proper configuration

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Includes security configurations that should be established first

2. **cache** (Priority 2)
   - Supporting services that the application will use
   - Moderate complexity with Redis authentication

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on other infrastructure
   - Highest complexity with database integration and service configuration

### Assumptions

1. The target environment will continue to be Fedora-based systems (Fedora 42 as specified in Vagrantfile)
2. The same network configuration will be maintained (port forwarding, private network)
3. Self-signed certificates are acceptable for the migrated environment
4. The FastAPI application source will continue to be pulled from the same Git repository
5. The current security configurations (fail2ban, ufw, SSH hardening) are still required
6. Redis and Memcached configurations will maintain the same memory allocations and settings
7. The PostgreSQL database schema and user permissions will remain the same
8. The current directory structure for web content (/var/www/[site]) will be maintained
9. The systemd service configuration for FastAPI will remain similar
10. No additional monitoring or logging solutions are required beyond what's currently configured