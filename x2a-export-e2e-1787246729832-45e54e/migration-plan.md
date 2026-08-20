# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration scope is moderate, consisting of three primary cookbooks with external dependencies. Based on the complexity and size, a migration timeline of 2-3 weeks is estimated for a single engineer, or 1 week with a team of 2-3 engineers working in parallel.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and SSL certificate management
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup, security hardening (fail2ban, ufw)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database provisioning, systemd service configuration

### Infrastructure Files

- `Berksfile`: Manages cookbook dependencies, including external cookbooks from Chef Supermarket (nginx, memcached, redisio)
- `solo.json`: Contains node configuration including the run list and attributes for Nginx sites and security settings
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `vagrant-provision.sh`: Bash script for provisioning a Vagrant VM with Chef Solo
- `Vagrantfile`: Defines a Fedora 42 VM with port forwarding and network configuration

### Target Details

Based on the source configuration files:

- **Operating System**: Supports Ubuntu (>= 18.04) and CentOS (>= 7.0) as specified in cookbook metadata, with Fedora 42 used in Vagrant development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role (e.g., geerlingguy.redis)

### Security Considerations

- **SSL/TLS Configuration**: Migration must preserve SSL certificate paths and configuration
  - Current paths: /etc/ssl/certs (certificates) and /etc/ssl/private (private keys)
  - Consider using Ansible's crypto modules for certificate management

- **Firewall Configuration**: UFW firewall is enabled in the Chef configuration
  - Use Ansible's ufw module to maintain equivalent firewall rules

- **SSH Hardening**: SSH configuration disables root login and password authentication
  - Use Ansible's ssh_config module to apply equivalent security settings

- **Fail2ban Integration**: Fail2ban is enabled for intrusion prevention
  - Use Ansible's fail2ban role to maintain equivalent protection

- **Vault/secrets management**: 
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - Consider using Ansible Vault to secure these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: The current setup manages multiple virtual hosts with SSL
  - Challenge: Preserving the flexibility of the current multi-site configuration
  - Mitigation: Create a templated Ansible role that can generate site configurations from variables

- **Redis Configuration Patching**: The cache cookbook includes a ruby_block that modifies Redis configuration
  - Challenge: Replicating the custom Redis configuration modifications
  - Mitigation: Use Ansible's lineinfile or template module with proper conditionals

- **FastAPI Application Deployment**: The current setup clones a Git repository and sets up a Python environment
  - Challenge: Ensuring idempotent application deployment and updates
  - Mitigation: Use Ansible's git module with version pinning and handlers for service restart

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Relatively self-contained with clear configuration patterns

2. **cache** (Priority 2)
   - Supporting service with external dependencies
   - Moderate complexity due to Redis configuration customization

3. **fastapi-tutorial** (Priority 3)
   - Application-specific deployment
   - Depends on properly configured infrastructure components

### Assumptions

1. The current Chef setup is functional and represents the desired state
2. No major architectural changes are planned during the migration
3. The target environment will continue to be VM-based (Vagrant/libvirt)
4. SSL certificates are managed outside of the automation process
5. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
6. The migration will maintain support for both Ubuntu and CentOS operating systems
7. No CI/CD pipeline integration is currently in place
8. The Nginx sites configuration in solo.json represents the complete set of virtual hosts
9. Redis and Memcached are used by the FastAPI application, though this connection isn't explicitly configured