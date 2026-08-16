# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration scope is moderate, consisting of three primary cookbooks with external dependencies. Based on the complexity and size, an estimated timeline of 2-3 weeks would be reasonable for a complete migration to Ansible, including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL setup, security hardening

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
- `solo.json`: Contains the run list and configuration data for Chef Solo. Will be migrated to Ansible inventory variables.
- `solo.rb`: Chef Solo configuration file. Will be replaced by Ansible configuration.
- `Vagrantfile`: Defines the development VM environment. Can be adapted for Ansible testing with minimal changes.
- `vagrant-provision.sh`: Provisioning script for Vagrant that installs Chef and runs cookbooks. Will need to be replaced with Ansible provisioning.

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ mentioned in cookbook metadata
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible `nginx` role from Galaxy or custom role
- **memcached (~> 6.0)**: Replace with Ansible `geerlingguy.memcached` role
- **redisio (~> 7.2.4)**: Replace with Ansible `geerlingguy.redis` role or custom Redis role

### Security Considerations

- **SSL Configuration**: The nginx-multisite cookbook manages SSL certificates and private keys. Migration should maintain secure certificate handling.
  - Migration approach: Use Ansible Vault for certificate storage or integrate with external certificate management
  
- **Redis Authentication**: Redis is configured with password authentication.
  - Migration approach: Store Redis password in Ansible Vault and template into configuration

- **Security Hardening**: The nginx-multisite cookbook includes security configurations.
  - Migration approach: Implement equivalent security configurations in Ansible templates

- **Fail2ban and UFW**: Security settings in solo.json indicate Fail2ban and UFW are enabled.
  - Migration approach: Include Ansible tasks for Fail2ban and UFW configuration

- **SSH Hardening**: SSH configuration disables root login and password authentication.
  - Migration approach: Implement equivalent SSH hardening in Ansible

- **Vault/secrets management**:
  - PostgreSQL credentials in fastapi-tutorial cookbook (username: fastapi, password: fastapi_password)
  - Redis authentication password in cache cookbook (redis_secure_password_123)
  - FastAPI environment variables in .env file
  - Total credentials detected: 3 (2 database passwords, 1 application configuration)

### Technical Challenges

- **Multi-site Nginx Configuration**: The nginx-multisite cookbook manages multiple virtual hosts with SSL.
  - Mitigation: Create Ansible templates that can generate equivalent site configurations from variables

- **Redis Configuration Hack**: The cache cookbook includes a ruby_block to modify Redis configuration.
  - Mitigation: Create proper Redis configuration templates in Ansible that don't require post-processing

- **FastAPI Application Deployment**: The fastapi-tutorial cookbook clones a Git repository and sets up a Python environment.
  - Mitigation: Use Ansible's git module and pip module to manage application deployment

- **PostgreSQL User and Database Setup**: The fastapi-tutorial cookbook creates PostgreSQL users and databases.
  - Mitigation: Use Ansible's postgresql_user and postgresql_db modules for cleaner database management

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate management
   - Implement virtual host configuration
   - Add security hardening

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis configuration with authentication

3. **fastapi-tutorial** (high complexity, application deployment)
   - Set up PostgreSQL database and user
   - Implement Git repository deployment
   - Configure Python virtual environment and dependencies
   - Create systemd service configuration

### Assumptions

1. The current deployment is targeting a single VM environment as indicated by the Vagrantfile.
2. SSL certificates are self-signed for development purposes (based on Vagrant provisioning script comments).
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git is publicly accessible.
4. The current setup does not appear to use centralized secret management beyond configuration files.
5. The nginx-multisite cookbook appears to have site-specific files in the files directory that would need to be migrated.
6. The migration will maintain the same basic architecture (Nginx + Redis/Memcached + FastAPI + PostgreSQL).
7. No CI/CD pipeline integration is visible in the current repository.
8. No monitoring or logging solutions are explicitly configured beyond default service logs.
9. The current setup does not appear to use distributed configuration or service discovery.