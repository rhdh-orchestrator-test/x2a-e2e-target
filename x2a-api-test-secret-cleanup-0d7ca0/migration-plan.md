# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three primary Chef cookbooks to Ansible roles and playbooks, addressing external dependencies, and ensuring security configurations are properly maintained.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has well-structured Chef cookbooks with clear dependencies
- Security configurations are present and need careful migration
- Multiple services need to be coordinated (Nginx, Redis, Memcached, PostgreSQL, FastAPI)

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server configured to host multiple SSL-enabled websites with security hardening
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup, security hardening (fail2ban, ufw, sysctl), custom Nginx configurations

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

- `Berksfile`: Defines cookbook dependencies including external cookbooks from Chef Supermarket (nginx, memcached, redisio)
- `solo.json`: Defines the Chef run list and configuration attributes for Nginx sites and security settings
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `Vagrantfile`: Defines a Fedora 42 VM for development/testing with port forwarding and network configuration
- `vagrant-provision.sh`: Shell script to install Chef and run the cookbooks in the Vagrant environment

### Target Details

- **Operating System**: Fedora (based on Vagrantfile specifying "generic/fedora42"), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or DavidWittman.redis

### Security Considerations

- **SSL/TLS Configuration**: 
  - Migration approach: Use Ansible's `openssl_*` modules to generate self-signed certificates
  - Ensure proper file permissions are maintained for private keys

- **Firewall (UFW)**:
  - Migration approach: Use Ansible's `ufw` module to configure firewall rules
  - Ensure the same default deny policy and specific allow rules are maintained

- **Fail2ban**:
  - Migration approach: Use Ansible to install and configure fail2ban with the same jail settings
  - Ensure templates are converted to Jinja2 format

- **System Hardening**:
  - Migration approach: Use Ansible to apply the same sysctl security settings
  - Maintain SSH hardening configurations (disable root login, password authentication)

- **Vault/secrets management**:
  - Redis password in cache cookbook: Move to Ansible Vault
  - PostgreSQL credentials in fastapi-tutorial cookbook: Move to Ansible Vault
  - Count: 2 credentials identified (Redis auth password, PostgreSQL user password)

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current setup dynamically generates Nginx site configurations based on node attributes
  - Mitigation strategy: Use Ansible templates with loops to generate site configurations from variables

- **SSL Certificate Generation**:
  - Description: Self-signed certificates are generated for each site
  - Mitigation strategy: Use Ansible's `openssl_certificate` module to generate certificates with proper permissions

- **Service Coordination**:
  - Description: Multiple interdependent services (Nginx, Redis, PostgreSQL, FastAPI application)
  - Mitigation strategy: Use Ansible handlers and proper dependency ordering to ensure services start in the correct order

- **Redis Configuration Hack**:
  - Description: The Chef cookbook includes a hack to modify Redis configuration
  - Mitigation strategy: Create a proper Redis configuration template in Ansible without requiring post-configuration modifications

### Migration Order

1. **cache** (Priority 1 - low risk, foundational service)
   - Implement Memcached and Redis roles
   - Ensure Redis authentication is properly configured
   - Test service functionality independently

2. **nginx-multisite** (Priority 2 - moderate complexity)
   - Implement Nginx installation and base configuration
   - Implement security hardening (fail2ban, ufw, sysctl)
   - Create templates for site configurations
   - Implement SSL certificate generation
   - Test with static content

3. **fastapi-tutorial** (Priority 3 - highest complexity, depends on other services)
   - Implement PostgreSQL installation and configuration
   - Implement Python environment setup
   - Deploy application from Git
   - Configure systemd service
   - Test integration with Nginx and database

### Assumptions

1. The target environment will continue to be Fedora-based, but the Ansible playbooks should support Ubuntu and CentOS as specified in the cookbook metadata.
2. Self-signed certificates are acceptable for the migration (production environments would likely use Let's Encrypt or other CA-signed certificates).
3. The same security hardening measures are required in the Ansible implementation.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The Redis configuration hack in the cache cookbook is addressing compatibility issues that may need investigation during migration.
6. The current directory structure in the target environment (/opt/server/*, /var/www/*) should be maintained.
7. The Vagrant development environment should be preserved for testing the Ansible playbooks.