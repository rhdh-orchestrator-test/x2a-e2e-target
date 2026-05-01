# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, configuration templates, and security settings.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 3-4 weeks
- Testing and Validation: 2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 7-8 weeks

**Complexity Assessment:** Medium to High
- Multiple interconnected services
- Security configurations that need careful migration
- External dependencies on Chef Supermarket cookbooks

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and custom configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup with self-signed certificates, security hardening (fail2ban, ufw, headers)

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file listing both local cookbooks and external dependencies from Chef Supermarket (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `Vagrantfile`: Defines a Fedora 42 VM with port forwarding and resource allocation for testing
- `solo.json`: Chef Solo configuration with run list and node attributes for Nginx sites and security settings
- `solo.rb`: Chef Solo configuration specifying cookbook paths and log settings
- `vagrant-provision.sh`: Bash script to provision the Vagrant VM with Chef Solo

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development/testing

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Ansible role
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or DavidWittman.redis

### Security Considerations

- **SSL/TLS Configuration**: 
  - Migration approach: Use Ansible's `openssl_*` modules to generate self-signed certificates
  - Ensure proper file permissions for private keys

- **Firewall (UFW)**: 
  - Migration approach: Use Ansible's `ufw` module to configure firewall rules
  - Ensure idempotent rule application

- **fail2ban**: 
  - Migration approach: Use Ansible Galaxy role `geerlingguy.security` or create custom tasks
  - Ensure jail configurations are properly migrated

- **SSH Hardening**: 
  - Migration approach: Use Ansible's `lineinfile` module to modify sshd_config
  - Consider using `ansible.posix.sshd` module for more robust configuration

- **Vault/secrets management**:
  - Redis password in cache cookbook: Use Ansible Vault to store the password
  - PostgreSQL credentials in fastapi-tutorial cookbook: Use Ansible Vault for database credentials
  - Count of credentials detected: 2 (Redis password, PostgreSQL user/password)

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current Chef implementation uses templates to generate site configurations dynamically based on node attributes
  - Mitigation strategy: Create Ansible templates with similar logic, using host_vars or group_vars to define site configurations

- **Redis Configuration Patching**: 
  - Description: The Chef cookbook uses a ruby_block to modify Redis configuration files after they're created
  - Mitigation strategy: Create a custom Redis configuration template in Ansible rather than modifying files after creation

- **FastAPI Application Deployment**: 
  - Description: The current implementation clones a Git repository and sets up a Python environment
  - Mitigation strategy: Use Ansible's git module and pip module to replicate this functionality

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security configurations that should be established first

2. **cache** (Priority 2)
   - Supporting services that the application may depend on
   - Moderate complexity with external dependencies

3. **fastapi-tutorial** (Priority 3)
   - Application layer that depends on both web server and database
   - Contains database setup that should come after infrastructure components

### Assumptions

1. The target environment will continue to be Fedora-based systems (specifically Fedora 42 as specified in the Vagrantfile)
2. The self-signed SSL certificates approach is acceptable for the migrated solution
3. The security requirements (fail2ban, ufw, SSH hardening) will remain the same
4. The FastAPI application source code repository will remain available at the specified URL
5. The directory structure for web content and application files will remain the same
6. The Redis and PostgreSQL passwords in the Chef recipes are development passwords and will be replaced with proper secrets management in production
7. The Nginx site configurations (test.cluster.local, ci.cluster.local, status.cluster.local) will remain the same
8. The port mappings and networking configuration will be preserved in the migrated solution