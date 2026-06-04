# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The Chef cookbooks are well-structured and follow standard patterns
- External dependencies on community cookbooks will need Ansible equivalents
- Security configurations are present and need careful migration
- Multiple services with interdependencies increase complexity

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, fail2ban integration, UFW firewall rules

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4)
- `solo.json`: Defines the run list and configuration parameters for nginx sites and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Defines a Fedora 42 VM with port forwarding and networking for development/testing
- `vagrant-provision.sh`: Shell script to install Chef and run the cookbooks in the Vagrant environment

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) as specified in cookbook metadata, with Fedora 42 used for development in Vagrant
- **Virtual Machine Technology**: Vagrant with libvirt provider as indicated in the Vagrantfile
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Ansible role
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or `DavidWittman.redis`

### Security Considerations

- **SSL/TLS Configuration**: 
  - Self-signed certificate generation needs to be migrated to Ansible
  - Strong cipher configuration and security headers must be preserved
  - Migration approach: Use Ansible's `openssl_*` modules or community.crypto collection

- **Firewall Configuration**: 
  - UFW rules need to be migrated
  - Migration approach: Use Ansible's `ufw` module

- **fail2ban Integration**:
  - Configuration templates need to be migrated
  - Migration approach: Create equivalent templates and use Ansible's template module

- **System Hardening**:
  - SSH hardening (disable root login, password authentication)
  - Sysctl security parameters
  - Migration approach: Use Ansible's `lineinfile` or `template` modules

- **Vault/secrets management**:
  - Redis password in plaintext in the cache cookbook
  - PostgreSQL password in plaintext in the fastapi-tutorial cookbook
  - Migration approach: Use Ansible Vault to encrypt sensitive values

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation uses Chef's resource model to dynamically create multiple virtual hosts
  - Mitigation: Use Ansible's with_items/loop constructs with templates to achieve similar functionality

- **Service Interdependencies**:
  - Description: The FastAPI application depends on PostgreSQL, and the web server depends on the application being available
  - Mitigation: Use Ansible handlers and the `notify` mechanism to manage service restarts and dependencies

- **Custom Ruby Logic**:
  - Description: The cache cookbook contains a ruby_block to modify Redis configuration
  - Mitigation: Replace with Ansible's `lineinfile` or `replace` modules

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation
   - Add SSL certificate generation
   - Configure virtual hosts
   - Implement security features (fail2ban, firewall)

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper service management

3. **fastapi-tutorial** (high complexity, depends on database)
   - Set up PostgreSQL database
   - Deploy application code
   - Configure environment and dependencies
   - Set up systemd service

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS as specified in the cookbook metadata
2. The Ansible control node will have network access to the managed nodes similar to the Chef setup
3. Python will be available on the target systems for Ansible to function
4. Self-signed certificates are acceptable for development/testing, but production may require proper certificates
5. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
6. The current security configurations are appropriate and should be maintained in the Ansible implementation
7. The Redis and PostgreSQL passwords in plaintext will be secured using Ansible Vault in the new implementation
8. The Vagrant development environment will be replaced with an equivalent Ansible-based setup