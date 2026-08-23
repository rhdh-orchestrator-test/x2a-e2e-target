# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration scope is moderate, involving three primary cookbooks with external dependencies. Based on the complexity and number of components, we estimate a 2-3 week timeline for complete migration, with testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL setup, security hardening (fail2ban, firewall)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Manages cookbook dependencies, including external cookbooks from Chef Supermarket (nginx, memcached, redisio)
- `solo.json`: Contains Chef run list and configuration data for Nginx sites and security settings
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `Vagrantfile`: Defines development VM using Fedora 42, with port forwarding and network configuration
- `vagrant-provision.sh`: Bash script that installs Chef and runs the provisioning process in the Vagrant VM

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) as specified in cookbook metadata. Development environment uses Fedora 42 (from Vagrantfile).
- **Virtual Machine Technology**: Vagrant with libvirt provider as specified in the Vagrantfile.
- **Cloud Platform**: Not specified. The configuration appears to be designed for on-premises or generic VM deployment.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)

### Security Considerations

- **SSL Configuration**: Migration must preserve SSL certificate paths and configuration
  - Current paths: `/etc/ssl/certs` for certificates, `/etc/ssl/private` for private keys
  - Migration approach: Use Ansible's `copy` or `template` modules with appropriate permissions

- **Fail2Ban Configuration**: Security hardening via fail2ban must be preserved
  - Migration approach: Use Ansible fail2ban role or dedicated tasks

- **Firewall (UFW)**: Firewall rules must be migrated
  - Migration approach: Use Ansible UFW module or firewalld module depending on target OS

- **SSH Hardening**: SSH configuration disables root login and password authentication
  - Migration approach: Use Ansible's `lineinfile` or dedicated SSH role

- **Vault/secrets management**:
  - Redis authentication password hardcoded in recipe (`redis_secure_password_123`)
  - PostgreSQL database credentials hardcoded in recipe (`fastapi:fastapi_password`)
  - FastAPI environment variables with database connection string in plaintext
  - Migration approach: Move all credentials to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The current setup dynamically creates Nginx site configurations based on node attributes
  - Migration approach: Use Ansible templates with variable loops to generate site configurations

- **PostgreSQL User/Database Creation**: The current setup uses inline shell commands
  - Migration approach: Use Ansible's postgresql_user and postgresql_db modules for cleaner implementation

- **Python Application Deployment**: The current setup clones a Git repository and sets up a Python virtual environment
  - Migration approach: Use Ansible's git module and pip module with virtualenv parameter

- **Service Management**: The current setup creates and manages systemd services
  - Migration approach: Use Ansible's template module for service files and service module for management

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation and configuration
   - Implement SSL certificate management
   - Configure virtual hosts for multiple sites
   - Implement security hardening (fail2ban, firewall)

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Set up PostgreSQL database and user
   - Deploy Python application from Git
   - Configure Python virtual environment and dependencies
   - Create and manage systemd service

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS as specified in the cookbook metadata.
2. SSL certificates are managed externally and not generated as part of the deployment process.
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
4. The current security configurations (fail2ban, UFW, SSH hardening) are sufficient and should be maintained.
5. The Vagrant development environment is primarily for testing and not part of the production deployment.
6. No custom Chef resources or libraries are in use that would require special handling.
7. The Redis configuration hack in the cache cookbook is a workaround for compatibility issues that may not be needed in Ansible.
8. The current setup does not include monitoring or logging solutions beyond basic service management.