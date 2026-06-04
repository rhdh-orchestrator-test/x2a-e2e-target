# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site web server with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 3-4 weeks, with moderate complexity due to the interdependencies between services and security configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificate generation
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup, security hardening (fail2ban, ufw, sysctl)

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints.
- `solo.json`: Chef configuration file defining the run list and node attributes. Contains configuration for nginx sites and security settings.
- `solo.rb`: Chef configuration file specifying file paths and log settings.
- `Vagrantfile`: Defines a Vagrant VM configuration using Fedora 42 with port forwarding and resource allocation.
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef, install dependencies, and run Chef Solo.

### Target Details

- **Operating System**: Fedora (based on Vagrantfile specifying "generic/fedora42"), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting local development/testing environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or custom role
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy or custom role
- **redisio (~> 7.2.4)**: Replace with Ansible redis role from Galaxy or custom role

### Security Considerations

- **SSL/TLS Management**: 
  - Migration approach: Use Ansible's openssl_* modules to generate self-signed certificates
  - Consider integrating with Ansible Vault for certificate storage

- **Firewall Configuration (UFW)**:
  - Migration approach: Use Ansible's ufw module to configure firewall rules

- **Fail2ban Configuration**:
  - Migration approach: Use Ansible to install and configure fail2ban with templates

- **SSH Hardening**:
  - Migration approach: Use Ansible's lineinfile or template module to configure SSH security settings

- **Vault/secrets management**:
  - Redis password in cache cookbook (hardcoded as 'redis_secure_password_123')
  - PostgreSQL database credentials in fastapi-tutorial cookbook (hardcoded as 'fastapi_password')
  - Consider using Ansible Vault to secure these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation uses Chef templates and attributes to configure multiple Nginx sites
  - Mitigation: Create Ansible templates with similar structure, using host_vars or group_vars to define site configurations

- **Redis Configuration Patching**:
  - Description: The cache cookbook uses a ruby_block to modify Redis configuration after installation
  - Mitigation: Create a custom Redis configuration template in Ansible that includes the correct settings from the start

- **Service Orchestration**:
  - Description: Ensuring services start in the correct order (e.g., PostgreSQL before FastAPI application)
  - Mitigation: Use Ansible handlers and the 'notify' mechanism to ensure proper service restart ordering

- **Self-signed Certificate Generation**:
  - Description: The current implementation generates self-signed certificates for each site
  - Mitigation: Use Ansible's openssl_* modules to generate certificates with similar parameters

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation and configuration
   - Add SSL/TLS certificate generation
   - Implement security hardening (fail2ban, ufw, sysctl)
   - Configure virtual hosts

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Set up PostgreSQL database and user
   - Deploy FastAPI application from Git
   - Configure Python environment and dependencies
   - Create and enable systemd service

### Assumptions

1. The target environment will continue to be Fedora-based, but should support Ubuntu and CentOS as specified in the cookbook metadata.
2. Self-signed certificates are acceptable for the migrated solution (production environments would likely use Let's Encrypt or other CA-signed certificates).
3. The current hardcoded passwords in the Chef recipes will be replaced with Ansible Vault secured variables.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The Vagrant development environment will be maintained, but converted to use Ansible provisioning instead of Chef.
6. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate for the target environment.
7. The nginx sites configuration in solo.json (test.cluster.local, ci.cluster.local, status.cluster.local) will be maintained in the Ansible inventory.