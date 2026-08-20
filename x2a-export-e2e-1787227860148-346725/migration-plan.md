# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration scope is moderate, involving three primary cookbooks with external dependencies. Based on the complexity and size, the estimated timeline for migration is 2-3 weeks with 1 dedicated engineer or 1-1.5 weeks with 2 engineers working in parallel.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
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

- `Berksfile`: Manages cookbook dependencies, including external cookbooks from Chef Supermarket (nginx, memcached, redisio). Will need to be replaced with Ansible Galaxy requirements.
- `solo.json`: Contains node attributes and run list for Chef Solo. Will be migrated to Ansible inventory variables.
- `solo.rb`: Chef Solo configuration file. Will be replaced with Ansible configuration.
- `Vagrantfile`: Defines the development VM using Fedora 42. Can be adapted for Ansible-based provisioning.
- `vagrant-provision.sh`: Bash script that installs Chef and runs the cookbooks. Will be replaced with Ansible provisioning.

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>=18.04) and CentOS (>=7.0) based on cookbook metadata, but the Vagrantfile uses Fedora 42.
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or the `ansible.posix.nginx` collection
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` role or DavidWittman.redis

### Security Considerations

- **SSL/TLS Configuration**: The nginx-multisite cookbook manages SSL certificates. Migration should preserve the certificate paths and configurations.
  - Migration approach: Use Ansible's `community.crypto` collection for certificate management
  
- **Redis Authentication**: Redis is configured with password authentication.
  - Migration approach: Ensure Redis password is stored in Ansible Vault

- **Security Hardening**: The configuration includes fail2ban, ufw firewall, and SSH hardening.
  - Migration approach: Use `ansible.posix.firewall` and dedicated security roles

- **Vault/secrets management**:
  - Redis password hardcoded in the cache cookbook: `redis_secure_password_123`
  - PostgreSQL credentials hardcoded in the fastapi-tutorial cookbook: `fastapi:fastapi_password`
  - Environment variables with sensitive data in .env file for FastAPI application
  - Count: 3 sets of credentials detected across 2 modules

### Technical Challenges

- **Multi-site Nginx Configuration**: The nginx-multisite cookbook dynamically creates virtual hosts based on node attributes. 
  - Mitigation: Use Ansible templates with loops to generate similar configuration

- **PostgreSQL User/Database Creation**: The current implementation uses inline SQL commands.
  - Mitigation: Use Ansible's `community.postgresql` collection for more idempotent database management

- **Python Application Deployment**: The current implementation clones a Git repository and sets up a virtual environment.
  - Mitigation: Use Ansible's `git` module and `pip` module for more declarative management

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation and configuration
   - Add SSL/TLS support
   - Implement virtual hosts configuration
   - Add security hardening

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Set up PostgreSQL database and user
   - Deploy Python application from Git
   - Configure environment and systemd service

### Assumptions

1. The current Chef setup is functional and represents the desired end state
2. No major architectural changes are planned during the migration
3. The same operating systems (Ubuntu/CentOS/Fedora) will be targeted
4. The Vagrant development environment should be preserved
5. SSL certificates are self-signed for development (based on Vagrant setup)
6. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git is accessible and will remain available
7. No CI/CD pipeline integration is required as part of the migration
8. The migration will maintain the same level of security hardening
9. Redis and PostgreSQL passwords in the current implementation are for development only and will be replaced with Ansible Vault secured values