# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks, handling external dependencies, and ensuring proper security configurations are maintained.

**Scope**: 3 Chef cookbooks with dependencies on external cookbooks
**Complexity**: Medium (standard web stack with some security hardening)
**Timeline Estimate**: 2-3 weeks for complete migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, fail2ban integration, UFW firewall setup

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

- `Berksfile`: Defines cookbook dependencies (both local and external from Chef Supermarket)
  - Migration consideration: Replace with Ansible Galaxy requirements.yml
  
- `solo.json`: Contains Chef run list and node attributes
  - Migration consideration: Convert to Ansible group_vars or host_vars

- `solo.rb`: Chef Solo configuration
  - Migration consideration: Replace with ansible.cfg

- `Vagrantfile`: Defines development VM using Fedora 42
  - Migration consideration: Update to use Ansible provisioner instead of Chef

- `vagrant-provision.sh`: Shell script to install Chef and run cookbooks
  - Migration consideration: Replace with simpler Ansible provisioning script

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct configuration

### Security Considerations

- **SSL/TLS Configuration**: 
  - Self-signed certificates are generated for development
  - Migration approach: Use Ansible crypto modules (openssl_certificate, openssl_privatekey)

- **Firewall Configuration**: 
  - UFW is configured with specific rules
  - Migration approach: Use Ansible UFW module or firewalld module depending on target OS

- **Fail2ban Integration**:
  - Configured for intrusion prevention
  - Migration approach: Use Ansible fail2ban module or template configuration files

- **SSH Hardening**:
  - Root login disabled, password authentication disabled
  - Migration approach: Use Ansible ssh_config module or template sshd_config

- **Vault/secrets management**:
  - Redis password is hardcoded in recipe: "redis_secure_password_123"
  - PostgreSQL password is hardcoded in recipe: "fastapi_password"
  - Migration approach: Move credentials to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current setup dynamically creates multiple virtual hosts based on node attributes
  - Mitigation: Use Ansible with_items/loop to create multiple site configurations from variables

- **Redis Configuration Hack**: 
  - Description: The current setup includes a ruby_block to modify Redis configuration file after installation
  - Mitigation: Create a proper Redis configuration template in Ansible

- **Service Orchestration**: 
  - Description: Services have dependencies (FastAPI depends on PostgreSQL)
  - Mitigation: Use Ansible handlers and meta tasks to ensure proper service ordering

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Add security configurations (fail2ban, firewall)
   - Add virtual host configuration

2. **cache** (low complexity, independent service)
   - Configure Memcached
   - Configure Redis with authentication

3. **fastapi-tutorial** (high complexity, application deployment)
   - Set up PostgreSQL database
   - Deploy application code
   - Configure Python environment
   - Set up systemd service

### Assumptions

1. The target environment will continue to be Fedora-based, though the cookbooks support Ubuntu and CentOS
2. Self-signed certificates are acceptable for development (production would likely use Let's Encrypt or other CA)
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
4. The current security configurations are appropriate for the target environment
5. No custom Nginx modules or configurations beyond what's in the cookbooks are required
6. The Redis configuration hack is necessary due to compatibility issues with the redisio cookbook
7. No additional monitoring or logging beyond what's configured is required