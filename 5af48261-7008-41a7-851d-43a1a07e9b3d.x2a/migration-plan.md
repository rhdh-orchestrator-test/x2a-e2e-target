# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-component application stack consisting of:
- Nginx web server with multiple SSL-enabled virtual hosts
- Caching services (Redis and Memcached)
- FastAPI Python application with PostgreSQL database

The migration complexity is **moderate** with an estimated timeline of 2-3 weeks. The repository has a well-organized structure with clear separation of concerns between cookbooks, making it suitable for incremental migration. The presence of security configurations, SSL certificates, and database credentials will require careful handling during migration.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Self-signed SSL certificates, fail2ban integration, UFW firewall configuration, multiple virtual hosts

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef run list and node attributes configuration
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Vagrant configuration for local development/testing using Fedora 42
- `vagrant-provision.sh`: Provisioning script for Vagrant VM setup and Chef execution

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used for development in Vagrant
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role or package installation tasks with custom configuration

### Security Considerations

- **SSL Certificate Management**: Self-signed certificates are generated for development. Migration should:
  - Maintain the same directory structure (`/etc/ssl/certs` and `/etc/ssl/private`)
  - Preserve file permissions (640 for private keys, root:ssl-cert ownership)
  - Consider using Ansible's `openssl_*` modules for certificate generation

- **Firewall Configuration**: UFW is configured with specific rules:
  - Default deny policy
  - Allow SSH, HTTP, HTTPS
  - Migrate using Ansible's `ufw` module

- **Fail2ban Integration**: Configured for intrusion prevention:
  - Custom jail configuration
  - Migrate using Ansible's `template` module for configuration files

- **SSH Hardening**:
  - Root login disabled
  - Password authentication disabled
  - Migrate using Ansible's `lineinfile` or `template` modules

- **Vault/secrets management**:
  - Database credentials in FastAPI application (PostgreSQL user/password)
  - Redis authentication password
  - Consider using Ansible Vault for these secrets

### Technical Challenges

- **Multi-site Nginx Configuration**: The current setup dynamically generates site configurations based on node attributes. Ansible will need to:
  - Use templates with variable substitution
  - Handle SSL certificate generation for each site
  - Maintain the same directory structure and naming conventions

- **Service Orchestration**: The current setup has interdependent services:
  - PostgreSQL must be running before FastAPI application
  - Nginx depends on site configurations
  - Use Ansible handlers and proper task ordering to maintain these dependencies

- **Python Application Deployment**: The FastAPI application deployment involves:
  - Git repository cloning
  - Virtual environment setup
  - Dependencies installation
  - Environment file creation with database credentials
  - Systemd service configuration
  - Ansible has modules for all these tasks, but coordination will be important

### Migration Order

1. **cache cookbook** (Priority 1, low risk):
   - Simple package installation and configuration
   - Good starting point to establish patterns for service management

2. **nginx-multisite cookbook** (Priority 2, moderate complexity):
   - Core infrastructure component
   - Security configurations should be established early
   - SSL certificate generation logic needs to be tested thoroughly

3. **fastapi-tutorial cookbook** (Priority 3, higher complexity):
   - Application deployment with database dependencies
   - Requires proper handling of secrets and environment configuration

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS as specified in the cookbook metadata.
2. The self-signed certificates are for development only; production would use proper certificates.
3. The current security configurations (fail2ban, UFW, SSH hardening) are appropriate for the target environment.
4. The PostgreSQL database will continue to run on the same host as the FastAPI application.
5. The Redis password and PostgreSQL credentials will need to be managed securely in the Ansible implementation.
6. The Vagrant setup is primarily for development/testing and may not need to be migrated if alternative testing methods are available.