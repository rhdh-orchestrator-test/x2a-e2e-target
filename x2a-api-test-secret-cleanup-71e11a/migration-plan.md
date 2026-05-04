# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, configuration templates, and security hardening settings. The estimated timeline for migration is 3-4 weeks, with moderate complexity due to the security configurations and multi-site setup.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and fail2ban integration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening, fail2ban integration, UFW firewall configuration

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies with version constraints
- `Vagrantfile`: Defines a Fedora 42 VM with port forwarding for development and testing
- `solo.json`: Chef configuration file with run list and node attributes for Nginx sites and security settings
- `solo.rb`: Chef configuration file for cookbook paths and logging settings
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef

### Target Details

Based on the source configuration files:

- **Operating System**: The repository supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) as specified in the metadata.rb files. The Vagrantfile uses Fedora 42 for development.
- **Virtual Machine Technology**: Vagrant with libvirt provider as specified in the Vagrantfile.
- **Cloud Platform**: No specific cloud platform is targeted. The configuration appears to be for on-premises or generic VM deployment.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks
- **Python 3 and venv**: Use Ansible's package module for installation and pip module for dependency management

### Security Considerations

- **SSL/TLS Configuration**: The nginx-multisite cookbook generates self-signed certificates. In Ansible, use the openssl_* modules to generate certificates or integrate with community.crypto collection.
- **Firewall Rules**: UFW configuration in security.rb should be migrated to Ansible's ufw module.
- **fail2ban Configuration**: Convert fail2ban.jail.local.erb template to Ansible template with the same security settings.
- **System Hardening**: The sysctl security settings should be migrated to Ansible's sysctl module.
- **SSH Hardening**: The SSH security configurations should be migrated to Ansible's lineinfile or template module.
- **Vault/secrets management**:
  - Redis password in cache/recipes/default.rb (hardcoded as 'redis_secure_password_123')
  - PostgreSQL user password in fastapi-tutorial/recipes/default.rb (hardcoded as 'fastapi_password')
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Configuration**: The dynamic generation of Nginx site configurations based on node attributes will need careful translation to Ansible's template module with proper variable handling.
- **SSL Certificate Generation**: The self-signed certificate generation logic needs to be replicated in Ansible, ensuring proper file permissions and ownership.
- **Service Dependencies**: Ensuring proper service dependencies and restart handlers are maintained in the Ansible playbooks.
- **PostgreSQL User and Database Creation**: The direct PostgreSQL commands need to be replaced with Ansible's postgresql_* modules.
- **Redis Configuration Hack**: The ruby_block that modifies Redis configuration will need a custom approach in Ansible, possibly using lineinfile or replace module.

### Migration Order

1. **nginx-multisite** (Priority 1): This is the core infrastructure component that hosts the web applications.
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Implement security hardening features
   - Configure multi-site virtual hosts

2. **cache** (Priority 2): Caching services that support the web applications.
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper service management

3. **fastapi-tutorial** (Priority 3): Application deployment that depends on the database.
   - Set up PostgreSQL database
   - Deploy FastAPI application from Git
   - Configure Python environment and dependencies
   - Create systemd service

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS as specified in the metadata.rb files.
2. The self-signed certificates are for development/testing only and not production use.
3. The hardcoded passwords in the recipes are not for production use and will be replaced with Ansible Vault variables.
4. The Vagrant setup is primarily for development and testing, not for production deployment.
5. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git is accessible and contains the expected code.
6. The current security configurations are appropriate for the target environment and don't need significant changes beyond the technology migration.
7. The current directory structure and naming conventions will be maintained in the Ansible roles.
8. No additional features beyond what's in the current Chef cookbooks are required in the Ansible roles.