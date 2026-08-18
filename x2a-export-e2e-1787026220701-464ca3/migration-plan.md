# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration scope is moderate, consisting of three primary cookbooks with external dependencies. Based on the complexity and size, the estimated timeline for migration is 2-3 weeks with 1-2 engineers.

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

- `Berksfile`: Manages cookbook dependencies, including external cookbooks from Chef Supermarket (nginx, memcached, redisio)
- `solo.json`: Contains Chef run list and configuration data for Nginx sites and security settings
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `Vagrantfile`: Defines a Fedora 42 VM for local development with port forwarding and resource allocation
- `vagrant-provision.sh`: Bash script that installs Chef and Berkshelf, then runs Chef Solo in the Vagrant VM

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) as specified in cookbook metadata, with Fedora 42 used for development in Vagrant
- **Virtual Machine Technology**: Vagrant with libvirt provider for local development
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role (e.g., geerlingguy.redis)

### Security Considerations

- **SSL Configuration**: Migration must preserve SSL certificate paths and configuration for multiple sites
  - Current paths: /etc/ssl/certs (certificates) and /etc/ssl/private (private keys)
  - Migration approach: Use Ansible's crypto modules for certificate management

- **Nginx Security Hardening**: Security configurations in security.conf.erb template
  - Migration approach: Ensure equivalent security headers and settings in Ansible templates

- **Redis Authentication**: Redis is configured with password authentication
  - Migration approach: Ensure Redis password is stored securely in Ansible Vault

- **SSH Hardening**: SSH configuration disables root login and password authentication
  - Migration approach: Use Ansible ssh_config module with equivalent settings

- **Fail2ban and UFW**: Security tools are enabled in the configuration
  - Migration approach: Use Ansible modules for fail2ban and ufw configuration

- **Vault/secrets management**:
  - Redis password hardcoded in recipe (redis_secure_password_123)
  - PostgreSQL credentials hardcoded in FastAPI recipe (fastapi/fastapi_password)
  - FastAPI environment variables with database connection string
  - Count: 3 sets of credentials detected across modules

### Technical Challenges

- **Multi-site Nginx Configuration**: The current setup dynamically creates multiple virtual hosts with SSL
  - Mitigation: Create Ansible templates with Jinja2 loops to generate similar configuration

- **PostgreSQL User and Database Creation**: The current setup uses inline SQL commands
  - Mitigation: Use Ansible's postgresql_user and postgresql_db modules for cleaner implementation

- **FastAPI Application Deployment**: The current setup clones from Git and sets up a Python environment
  - Mitigation: Use Ansible's git module and pip module to replicate functionality

- **Redis Configuration Hack**: The current setup includes a ruby_block to modify Redis configuration
  - Mitigation: Create a proper Redis configuration template in Ansible to avoid post-configuration modifications

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Create Ansible role for Nginx installation and configuration
   - Implement virtual host templates with SSL support
   - Configure security settings

2. **cache** (low complexity, standalone services)
   - Create Ansible roles for Memcached and Redis
   - Implement Redis authentication using Ansible Vault for password storage

3. **fastapi-tutorial** (high complexity, application deployment)
   - Create Ansible role for Python application deployment
   - Implement PostgreSQL database setup
   - Configure systemd service

### Assumptions

1. The current Chef setup is functional and represents the desired end state
2. SSL certificates are managed outside this configuration (no certificate generation code is present)
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git is accessible
4. The target environment will continue to be either Ubuntu (>= 18.04) or CentOS (>= 7.0)
5. The Vagrant setup is primarily for development/testing and not part of the production deployment
6. No custom Chef resources or libraries are in use that would require special handling
7. No complex orchestration or ordering dependencies exist beyond what's visible in the recipes
8. The current security settings (fail2ban, ufw, SSH hardening) are appropriate for the target environment