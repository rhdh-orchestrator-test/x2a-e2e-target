# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx server with FastAPI application and caching services. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated complexity is moderate, with an estimated timeline of 2-3 weeks for a complete migration.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and SSL certificate management
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup, fail2ban integration, UFW firewall configuration, security hardening

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database setup
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef Solo configuration file with node attributes and run list
- `solo.rb`: Chef Solo Ruby configuration file
- `Vagrantfile`: Vagrant configuration for local development/testing environment
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in Vagrant development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible community.general.nginx or builtin nginx modules
- **memcached (~> 6.0)**: Replace with Ansible community.general.memcached module
- **redisio (~> 7.2.4)**: Replace with Ansible community.redis collection

### Security Considerations

- **SSL/TLS Management**: 
  - Self-signed certificates are generated for development
  - Migration should use Ansible crypto modules for certificate generation
  - Consider integrating with ansible.posix.openssl_* modules

- **Firewall Configuration**: 
  - UFW firewall rules need to be migrated to Ansible's ufw module
  - Ensure SSH, HTTP, and HTTPS ports remain accessible

- **SSH Hardening**:
  - Root login disabled
  - Password authentication disabled
  - Use ansible.posix.ssh_config module for equivalent configuration

- **fail2ban Integration**:
  - Migrate fail2ban configuration to Ansible community.general.fail2ban module

- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL credentials in fastapi-tutorial cookbook: "fastapi:fastapi_password"
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Configuration**: 
  - The nginx-multisite cookbook manages multiple virtual hosts with dynamic configuration
  - Solution: Use Ansible templates with loops to generate site configurations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Solution: Use ansible.builtin.openssl_* modules with proper idempotency checks

- **Service Dependencies**: 
  - FastAPI application depends on PostgreSQL
  - Solution: Use Ansible handlers and meta dependencies to ensure proper ordering

- **Redis Configuration Hack**: 
  - The Chef cookbook includes a hack to fix Redis configuration
  - Solution: Create proper Redis configuration template in Ansible

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add security hardening features
   - Implement SSL certificate management
   - Configure virtual hosts

2. **cache** (Priority 2)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper service management

3. **fastapi-tutorial** (Priority 3)
   - Set up Python environment
   - Configure PostgreSQL database
   - Deploy application code
   - Set up systemd service

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based systems
2. Self-signed certificates are acceptable for development, but production may require integration with Let's Encrypt or other certificate authorities
3. The current security configurations (fail2ban, UFW, SSH hardening) are required in the migrated solution
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current Redis and Memcached configurations meet performance requirements
6. The Vagrant development environment should be preserved or migrated to an equivalent Ansible-based setup
7. No CI/CD pipeline integration is required beyond what's currently implemented