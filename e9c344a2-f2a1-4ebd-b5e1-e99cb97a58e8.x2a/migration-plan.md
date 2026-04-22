# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to Ansible roles and playbooks. The estimated complexity is moderate, with security configurations and multi-site SSL setup requiring careful attention.

**Timeline Estimate:**
- Planning and preparation: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and validation: 1 week
- Documentation and knowledge transfer: 1 week
- **Total**: 5-6 weeks

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and proper SSL configuration
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
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4)
- `solo.json`: Defines the run list and configuration attributes for nginx sites and security settings
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `Vagrantfile`: Defines a Fedora 42 VM with port forwarding for development and testing
- `vagrant-provision.sh`: Shell script to install Chef and run the cookbooks in the Vagrant environment

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with the development environment using Fedora 42
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Ansible role
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or DavidWittman.redis

### Security Considerations

- **SSL Certificate Management**: 
  - Migration approach: Use Ansible's `openssl_*` modules for certificate generation
  - Consider integration with Let's Encrypt using `geerlingguy.certbot` role for production

- **Firewall Configuration (UFW)**:
  - Migration approach: Use Ansible's `ufw` module to configure firewall rules

- **fail2ban Integration**:
  - Migration approach: Create an Ansible role for fail2ban configuration using templates

- **SSH Hardening**:
  - Migration approach: Use Ansible's `lineinfile` module or the `ansible-hardening` role

- **Vault/secrets management**:
  - Redis password in cache cookbook: Store in Ansible Vault
  - PostgreSQL credentials in fastapi-tutorial cookbook: Store in Ansible Vault
  - Count of credentials detected: 2 (Redis password, PostgreSQL user/password)

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation dynamically generates site configurations based on node attributes
  - Mitigation: Use Ansible templates with loops to generate site configurations from variables

- **SSL Certificate Generation**:
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's `openssl_certificate` module with proper idempotency checks

- **Service Dependencies**:
  - Description: The FastAPI application depends on PostgreSQL being configured first
  - Mitigation: Use Ansible handlers and proper task ordering to ensure dependencies are met

- **Configuration File Modifications**:
  - Description: The cache cookbook uses a ruby_block to modify Redis configuration files
  - Mitigation: Use Ansible's `lineinfile` or template modules with proper validation

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Create base Nginx role
   - Implement security configurations (fail2ban, UFW)
   - Implement SSL certificate generation
   - Configure virtual hosts

2. **cache** (low complexity, standalone service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on database)
   - Implement PostgreSQL database setup
   - Configure Python environment and application deployment
   - Set up systemd service

### Assumptions

1. The target environment will continue to be either Ubuntu (>= 18.04) or CentOS (>= 7.0)
2. The Vagrant development environment will be maintained for testing
3. Self-signed certificates are acceptable for development, but production may require proper CA-signed certificates
4. The current security configurations are sufficient and should be maintained in the Ansible implementation
5. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
6. The current directory structure for web content and application code will be maintained
7. The Redis and PostgreSQL passwords in the Chef recipes are development passwords and will be replaced with secure passwords in production
8. The current nginx site configurations (test.cluster.local, ci.cluster.local, status.cluster.local) will be maintained
9. The current port configurations (80, 443 for Nginx, 6379 for Redis, 8000 for FastAPI) will be maintained