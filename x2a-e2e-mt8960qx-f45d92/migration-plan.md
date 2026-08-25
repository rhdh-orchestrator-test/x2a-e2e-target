# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration scope is moderate, consisting of three primary cookbooks with external dependencies. Based on the complexity and size, the estimated timeline for migration is 2-3 weeks with 1 engineer or 1-1.5 weeks with 2 engineers working in parallel.

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
    - Key Features: Python virtual environment, Git repository deployment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies for the Chef environment. Will be replaced by Ansible Galaxy requirements.
- `solo.json`: Contains the Chef run list and configuration attributes. Will be replaced by Ansible inventory variables.
- `solo.rb`: Chef configuration file. Will be replaced by Ansible configuration.
- `Vagrantfile`: Defines the development VM. Can be adapted to use Ansible provisioner instead of Chef.
- `vagrant-provision.sh`: Shell script that installs Chef and runs the cookbooks. Will be replaced with Ansible provisioning script.

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ as indicated in cookbook metadata
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role or redis_* modules

### Security Considerations

- **SSL Configuration**: The nginx-multisite cookbook manages SSL certificates. Migration should preserve certificate paths and configurations.
  - Migration approach: Use ansible.builtin.copy or ansible.builtin.template modules to manage SSL certificates and configurations.

- **Redis Authentication**: Redis is configured with password authentication.
  - Migration approach: Use Ansible Vault to store the Redis password and configure Redis with authentication.

- **Security Hardening**: The nginx-multisite cookbook includes security configurations.
  - Migration approach: Implement equivalent security configurations using Ansible templates and handlers.

- **Vault/secrets management**:
  - Hardcoded credentials detected in fastapi-tutorial recipe (PostgreSQL password: 'fastapi_password')
  - Hardcoded credentials detected in cache recipe (Redis password: 'redis_secure_password_123')
  - These should be migrated to Ansible Vault variables

### Technical Challenges

- **Multi-site Nginx Configuration**: The current setup manages multiple Nginx sites with SSL. 
  - Mitigation: Use Ansible's template module with Jinja2 templates to generate site configurations, similar to the current ERB templates.

- **Service Orchestration**: The current setup manages service dependencies (e.g., FastAPI depends on PostgreSQL).
  - Mitigation: Use Ansible handlers and meta dependencies to ensure proper service ordering.

- **Database Management**: The current setup creates PostgreSQL users and databases.
  - Mitigation: Use Ansible's postgresql_* modules from the community.postgresql collection.

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation and configuration
   - Implement SSL certificate management
   - Configure virtual hosts for multiple sites
   - Implement security hardening

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Set up PostgreSQL database and user
   - Deploy FastAPI application from Git
   - Configure Python environment and dependencies
   - Set up systemd service

### Assumptions

1. The current Chef setup is functional and represents the desired state.
2. The target environment will continue to be Fedora-based systems, with potential for Ubuntu and CentOS as indicated in the metadata.
3. The Vagrant development environment should be preserved with Ansible provisioning.
4. SSL certificates are managed manually or generated on the fly (no automated Let's Encrypt integration was observed).
5. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git is accessible and will remain available.
6. The hardcoded credentials in the recipes are for development purposes and will be replaced with secure credentials in production.
7. The current setup does not include monitoring or logging configurations beyond standard service logs.
8. The migration will maintain the same service architecture and deployment patterns.