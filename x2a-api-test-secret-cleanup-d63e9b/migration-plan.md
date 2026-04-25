# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, configuration templates, and security settings. The estimated timeline for migration is 3-4 weeks, with moderate complexity due to the security configurations and multi-site SSL setup.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and custom configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall), HTTP security headers

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file listing cookbook dependencies (nginx, memcached, redisio) - will be replaced with Ansible Galaxy requirements.yml
- `Vagrantfile`: Development environment configuration for Fedora 42 - can be adapted for Ansible testing
- `solo.json`: Chef node configuration with run list and attributes - will be converted to Ansible group_vars
- `solo.rb`: Chef configuration file - not needed in Ansible
- `vagrant-provision.sh`: Script to install Chef and run cookbooks - will be replaced with Ansible provisioning

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package management
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package management
- **PostgreSQL**: Replace with Ansible postgresql role or direct package management

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each virtual host
  - Migration approach: Use Ansible's openssl_* modules or community.crypto collection

- **Firewall Configuration**: 
  - UFW is configured with specific rules for HTTP/HTTPS/SSH
  - Migration approach: Use Ansible's ufw module or firewalld module depending on target OS

- **Fail2ban Integration**: 
  - Custom jail configuration for brute force protection
  - Migration approach: Use Ansible's template module with fail2ban configuration

- **System Hardening**: 
  - Sysctl security parameters
  - SSH hardening (root login disabled, password authentication disabled)
  - Migration approach: Use Ansible's sysctl and lineinfile/template modules

- **Vault/secrets management**:
  - Redis password hardcoded in recipe: "redis_secure_password_123"
  - PostgreSQL credentials hardcoded in recipe: "fastapi:fastapi_password"
  - FastAPI environment variables with database connection string
  - Migration approach: Use Ansible Vault for all credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current setup dynamically generates multiple virtual hosts with SSL
  - Mitigation: Use Ansible loops with templates to generate similar configuration

- **SSL Certificate Generation**: 
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's openssl_* modules to generate certificates or integrate with Let's Encrypt

- **Service Orchestration**: 
  - Description: Multiple interdependent services (Nginx, Redis, Memcached, PostgreSQL, FastAPI)
  - Mitigation: Use Ansible handlers and proper dependency ordering

- **Security Hardening**: 
  - Description: Comprehensive security measures across multiple services
  - Mitigation: Leverage Ansible security roles or create dedicated security tasks

### Migration Order

1. **cache cookbook** (low risk, foundational service)
   - Simple Redis and Memcached configuration
   - Few dependencies

2. **nginx-multisite cookbook** (moderate complexity)
   - Core web server functionality
   - Security configurations
   - SSL certificate management

3. **fastapi-tutorial cookbook** (high complexity, application layer)
   - Depends on PostgreSQL
   - Requires application deployment and configuration
   - Systemd service management

### Assumptions

1. The target environment will continue to be Fedora/CentOS/Ubuntu based on the current cookbook support
2. Self-signed certificates are acceptable for the migrated solution (vs. Let's Encrypt integration)
3. The same security hardening approach will be maintained
4. The FastAPI application source will continue to be pulled from the same Git repository
5. Redis and Memcached configurations will remain similar
6. The multi-site configuration pattern will be preserved
7. No additional monitoring or logging solutions need to be integrated
8. The current password/security approach is acceptable but should be moved to Ansible Vault
9. No CI/CD pipeline integration is required as part of the migration