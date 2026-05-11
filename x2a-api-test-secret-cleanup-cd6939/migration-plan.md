# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup with three primary cookbooks: nginx-multisite, cache, and fastapi-tutorial. The migration to Ansible will involve converting Chef recipes, templates, and attributes to Ansible roles, tasks, templates, and variables. Based on the repository analysis, this is a medium complexity migration with an estimated timeline of 3-4 weeks for a small team (2-3 people).

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)

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

- `Berksfile`: Manages cookbook dependencies - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Contains node configuration and run list - will be replaced by Ansible inventory variables
- `solo.rb`: Chef configuration file - will be replaced by ansible.cfg
- `Vagrantfile`: Defines development VM - can be adapted for Ansible Vagrant provisioner
- `vagrant-provision.sh`: Provisions the Vagrant VM with Chef - will be replaced by Ansible provisioning

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)

### Security Considerations

- **SSL Certificate Management**: 
  - Migration approach: Use Ansible's openssl_* modules for certificate generation
  - Consider integrating with Ansible Vault for private key storage

- **Firewall Configuration (UFW)**:
  - Migration approach: Use Ansible's ufw module for firewall management

- **Fail2ban Configuration**:
  - Migration approach: Use Ansible's template module to configure fail2ban

- **SSH Hardening**:
  - Migration approach: Use Ansible's lineinfile or template module to configure SSH

- **Vault/secrets management**:
  - Redis password in cache cookbook (hardcoded as 'redis_secure_password_123')
  - PostgreSQL credentials in fastapi-tutorial cookbook (hardcoded as 'fastapi_password')
  - Environment variables in .env file for FastAPI application
  - Total credentials detected: 2 hardcoded passwords

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current Chef implementation dynamically creates multiple Nginx sites with SSL
  - Mitigation: Use Ansible loops with templates to generate site configurations

- **SSL Certificate Generation**:
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's openssl_* modules with proper idempotency checks

- **Redis Configuration Patching**:
  - Description: The Chef cookbook uses a ruby_block to modify Redis configuration
  - Mitigation: Create a proper Ansible template for Redis configuration instead of patching

- **PostgreSQL User and Database Creation**:
  - Description: Uses shell commands to create database and user
  - Mitigation: Use Ansible's postgresql_* modules for proper idempotent management

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Add security hardening (fail2ban, ufw)
   - Add multi-site configuration

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Implement PostgreSQL installation and configuration
   - Implement Python environment setup
   - Implement application deployment
   - Implement systemd service configuration

### Assumptions

1. The target environment will continue to be Fedora-based systems (Fedora 42 as specified in Vagrantfile)
2. Self-signed SSL certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or other CA)
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
4. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate for the target environment
5. The Redis and PostgreSQL passwords in the Chef recipes are development passwords and will be replaced with Ansible Vault secured passwords
6. The Nginx sites configuration in solo.json overrides the default attributes in the cookbook
7. The application is intended to run on a single server (monolithic deployment)