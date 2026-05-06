# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup with three primary cookbooks: nginx-multisite, cache, and fastapi-tutorial. The infrastructure appears to be designed for a development or testing environment using Vagrant with Fedora 42. The migration to Ansible will involve converting Chef recipes, templates, and attributes to Ansible roles, tasks, templates, and variables.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:**
- Medium complexity due to multiple cookbooks with interdependencies
- Security configurations that need careful migration
- External cookbook dependencies that need Ansible equivalents

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)

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

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4)
- `solo.json`: Defines the run list and configuration parameters for Chef Solo
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Defines the development VM using Fedora 42 with port forwarding and resource allocation
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ mentioned in cookbook metadata
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development/testing

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or community.general.memcached module
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or community.general.redis module
- **PostgreSQL**: Replace with Ansible postgresql role or postgresql_* modules

### Security Considerations

- **SSL Certificate Management**: 
  - Migration approach: Use Ansible's openssl_* modules to generate self-signed certificates
  - Consider integrating with ansible.posix.acme_certificate for Let's Encrypt in production

- **Firewall Configuration (UFW)**:
  - Migration approach: Use ansible.posix.ufw module to configure firewall rules

- **Fail2ban Configuration**:
  - Migration approach: Use community.general.fail2ban module or custom templates

- **SSH Hardening**:
  - Migration approach: Use ansible.posix.sshd_config module to configure SSH security settings

- **Vault/secrets management**:
  - Redis password in cache cookbook (hardcoded as 'redis_secure_password_123')
  - PostgreSQL password in fastapi-tutorial cookbook (hardcoded as 'fastapi_password')
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation uses Chef attributes and templates to generate multiple virtual host configurations
  - Mitigation: Create Ansible templates with Jinja2 loops to generate similar configurations from variables

- **Redis Configuration Hack**: 
  - Description: The cache cookbook includes a ruby_block to modify Redis configuration files after they're created
  - Mitigation: Create a custom Redis configuration template in Ansible that properly handles these settings

- **Service Orchestration**: 
  - Description: The current setup manages service dependencies and notifications
  - Mitigation: Use Ansible handlers and meta dependencies to ensure proper service restart ordering

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Relatively self-contained with clear configuration patterns

2. **cache** (Priority 2)
   - Depends on external cookbooks (memcached, redisio)
   - Moderate complexity with custom configuration

3. **fastapi-tutorial** (Priority 3)
   - Application deployment with database dependencies
   - Requires coordination with other components

### Assumptions

1. The target environment will continue to be Fedora-based systems, though the cookbooks claim support for Ubuntu and CentOS
2. Self-signed certificates are acceptable for the migrated solution (production would likely require proper certificates)
3. The current security configurations are appropriate and should be maintained in the Ansible version
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current hardcoded passwords in the Chef recipes are for development only and will be replaced with Ansible Vault in production
6. The Vagrant development workflow should be preserved in the Ansible migration
7. No additional features beyond what's in the current Chef implementation are required