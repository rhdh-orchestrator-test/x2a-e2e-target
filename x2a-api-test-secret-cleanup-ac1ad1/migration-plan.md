# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks, handling external dependencies, and ensuring proper security configurations are maintained.

**Scope**: 3 Chef cookbooks with interdependencies and external cookbook dependencies
**Complexity**: Medium
**Estimated Timeline**: 3-4 weeks

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and proper SSL configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl), custom Nginx configuration templates

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file listing both local and external cookbook dependencies
- `solo.json`: Chef configuration file containing the run list and node attributes
- `solo.rb`: Chef configuration file specifying cookbook paths and log settings
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration for development environment using Fedora 42

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development/testing

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)

### Security Considerations

- **SSL Certificate Management**: 
  - Migration approach: Use Ansible's openssl_* modules for certificate generation
  - Consider integrating with Ansible Vault for secure key storage

- **Firewall Configuration (UFW)**:
  - Migration approach: Use Ansible's ufw module to maintain identical firewall rules

- **Fail2ban Configuration**:
  - Migration approach: Use Ansible to deploy and configure fail2ban with identical jail settings

- **SSH Hardening**:
  - Migration approach: Use Ansible's lineinfile or template module to configure SSH security settings

- **Vault/secrets management**:
  - Redis password in cache cookbook (plaintext in recipe)
  - PostgreSQL credentials in fastapi-tutorial cookbook (plaintext in recipe)
  - Consider using Ansible Vault to secure these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current Chef implementation uses a dynamic approach to configure multiple Nginx sites
  - Mitigation: Create an Ansible role with templates that can handle the same dynamic site configuration based on variables

- **SSL Certificate Generation**:
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's openssl_* modules to generate certificates with similar parameters

- **PostgreSQL User and Database Creation**:
  - Description: The current implementation uses inline shell commands
  - Mitigation: Use Ansible's postgresql_* modules for more idempotent database management

- **Python Virtual Environment Management**:
  - Description: The current implementation uses execute resources
  - Mitigation: Use Ansible's pip module with virtualenv parameter for cleaner implementation

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx configuration
   - Add SSL certificate generation
   - Implement security hardening (fail2ban, ufw)
   - Configure virtual hosts

2. **cache** (low complexity, standalone services)
   - Configure Memcached
   - Configure Redis with authentication

3. **fastapi-tutorial** (high complexity, application deployment)
   - Set up PostgreSQL
   - Deploy application code
   - Configure Python environment
   - Set up systemd service

### Assumptions

1. The target environment will continue to be Fedora-based systems (specifically Fedora 42 as indicated in the Vagrantfile)
2. The same security requirements will be maintained in the Ansible implementation
3. Self-signed certificates are acceptable for the migrated environment (production would likely use Let's Encrypt or other CA)
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current directory structure in the target environment (/opt/server/*, /var/www/*) should be preserved
6. The Redis and PostgreSQL passwords in the current implementation are for development only and will be replaced with secure passwords stored in Ansible Vault