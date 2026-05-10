# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. Based on the complexity and dependencies, this migration is estimated to take 2-3 weeks with a team of 2 engineers.

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

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef configuration file containing the run list and node attributes
- `solo.rb`: Chef configuration file specifying cookbook paths and log settings
- `Vagrantfile`: Defines a Fedora 42 VM with port forwarding for development/testing
- `vagrant-provision.sh`: Shell script that installs Chef and runs the cookbooks in the Vagrant environment

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) based on cookbook metadata, with Fedora 42 used for development in Vagrant
- **Virtual Machine Technology**: Vagrant with libvirt provider (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` role or direct package installation and configuration

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each virtual host
  - Migration approach: Use Ansible's `openssl_*` modules or community.crypto collection

- **Firewall Configuration**: 
  - UFW is configured to allow only SSH, HTTP, and HTTPS
  - Migration approach: Use Ansible's `ufw` module

- **Fail2ban Setup**: 
  - Configured for brute force protection
  - Migration approach: Use Ansible to install and configure fail2ban

- **SSH Hardening**: 
  - Root login disabled and password authentication disabled
  - Migration approach: Use Ansible's `lineinfile` module or `ansible.posix.sshd` module

- **Vault/secrets management**:
  - Redis password hardcoded in recipe: "redis_secure_password_123"
  - PostgreSQL credentials hardcoded in recipe: "fastapi:fastapi_password"
  - Environment variables with database connection string in .env file
  - Migration approach: Use Ansible Vault for all credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current setup dynamically generates Nginx site configurations based on node attributes
  - Mitigation: Use Ansible templates with variable substitution and loops

- **Redis Configuration Patching**: 
  - Description: The Chef cookbook uses a ruby_block to modify Redis configuration files after they're created
  - Mitigation: Create a custom Ansible template for Redis configuration or use lineinfile module

- **Service Orchestration**: 
  - Description: The current setup has specific service dependencies and restart notifications
  - Mitigation: Use Ansible handlers and proper task ordering with notify directives

- **SSL Certificate Generation**: 
  - Description: Self-signed certificates are generated for each virtual host
  - Mitigation: Use Ansible's crypto modules to generate certificates or integrate with Let's Encrypt

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Implement security hardening (fail2ban, UFW)
   - Configure virtual hosts

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Set up PostgreSQL database and user
   - Deploy FastAPI application from Git
   - Configure Python environment and dependencies
   - Create systemd service

### Assumptions

1. The target environment will continue to be either Ubuntu (>= 18.04) or CentOS (>= 7.0)
2. The same security requirements will apply in the new environment
3. Self-signed certificates are acceptable for the migrated solution (vs. Let's Encrypt or other CA)
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The Redis configuration hack in the cache cookbook is necessary due to compatibility issues with the Redis version
6. The Vagrant development environment will be replaced with an equivalent Ansible-based setup
7. No additional monitoring or logging requirements beyond what's in the current Chef setup