# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with FastAPI application backend and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- Total: 5-6 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- Moderate number of external dependencies
- Security configurations that need careful migration
- Self-signed SSL certificate generation that needs to be replicated

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures nginx with multiple SSL-enabled subdomains, security hardening, and site configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), sysctl security settings

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Configures caching services (memcached and redis) with security settings
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Dependency management file listing cookbook dependencies (nginx, memcached, redisio)
- `solo.json`: Chef configuration file with run list and node attributes
- `solo.rb`: Chef configuration file for Chef Solo
- `Vagrantfile`: Vagrant configuration for development/testing environment
- `vagrant-provision.sh`: Shell script to provision Chef in Vagrant VM

### Target Details

Based on the source configuration files:

- **Operating System**: Supports Ubuntu 18.04+ and CentOS 7.0+, with Fedora 42 used in Vagrant
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration should maintain the same level of security for private keys
  - Consider using Ansible's openssl_* modules for certificate generation

- **Firewall Configuration**: 
  - UFW firewall rules need to be migrated to equivalent Ansible ufw module tasks
  - Default deny policy with specific allows for SSH, HTTP, HTTPS

- **Fail2ban Integration**: 
  - Fail2ban configuration needs to be migrated to Ansible
  - Custom jail.local template needs to be preserved

- **SSH Hardening**: 
  - SSH configuration disables root login and password authentication
  - These settings need to be preserved in Ansible

- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL database credentials in fastapi-tutorial cookbook: "fastapi:fastapi_password"
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - The Chef cookbook dynamically creates site configurations based on node attributes
  - Ansible implementation will need similar templating approach
  - Challenge: Maintaining the same flexibility while ensuring proper SSL configuration

- **Self-signed Certificate Generation**: 
  - Chef generates self-signed certificates for each site
  - Ansible will need to use openssl_* modules to replicate this functionality
  - Challenge: Ensuring proper permissions and security for private keys

- **System Hardening**: 
  - Multiple security configurations (sysctl, SSH, firewall, fail2ban)
  - Challenge: Ensuring all security measures are properly migrated without gaps

- **Service Orchestration**: 
  - The current setup has interdependent services (nginx, PostgreSQL, FastAPI application)
  - Challenge: Maintaining proper service start order and dependencies in Ansible

### Migration Order

1. **cache** (Priority 1 - Low complexity)
   - Simple configuration of memcached and redis
   - Good starting point with minimal dependencies

2. **nginx-multisite** (Priority 2 - Medium complexity)
   - Core infrastructure component
   - Security configurations need careful migration
   - SSL certificate generation needs to be properly implemented

3. **fastapi-tutorial** (Priority 3 - Medium complexity)
   - Application deployment with database dependencies
   - Requires proper service configuration and environment setup

### Assumptions

1. The target environment will continue to be Ubuntu/CentOS based systems
2. Self-signed certificates are acceptable (not using Let's Encrypt or other CA)
3. The same security posture is required in the Ansible implementation
4. The FastAPI application source will remain at the same GitHub repository
5. The multi-site configuration pattern will be maintained
6. The Vagrant development environment should be preserved but updated for Ansible
7. No changes to the application architecture are planned during migration