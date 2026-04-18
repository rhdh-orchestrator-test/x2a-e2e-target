# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- Total: 5-6 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- External dependencies on community cookbooks need to be replaced with Ansible Galaxy roles
- Security configurations need careful migration to maintain the same level of protection

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and custom configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (nginx, memcached, redisio)
- `solo.json`: Defines the Chef run list and node attributes
- `solo.rb`: Chef Solo configuration
- `vagrant-provision.sh`: Provisioning script for Vagrant
- `Vagrantfile`: Vagrant configuration for development environment

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development/testing

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or custom role
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role from Galaxy

### Security Considerations

- **SSL/TLS Configuration**: 
  - Self-signed certificate generation needs to be migrated
  - Strong cipher configuration must be preserved
  - HSTS headers must be maintained

- **Firewall Configuration**:
  - UFW rules need to be migrated to equivalent Ansible UFW module tasks

- **Fail2ban Configuration**:
  - Fail2ban jail configuration needs to be migrated

- **System Hardening**:
  - Sysctl security settings need to be preserved
  - SSH hardening (disable root login, password authentication) must be maintained

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the FastAPI recipe (`fastapi:fastapi_password`)
  - These should be migrated to Ansible Vault

### Technical Challenges

- **Multi-site Configuration**: 
  - The dynamic generation of Nginx site configurations based on node attributes needs to be carefully migrated to Ansible templates and variables

- **SSL Certificate Generation**:
  - The self-signed certificate generation logic needs to be replicated in Ansible

- **Service Dependencies**:
  - Ensuring proper service dependencies and restart handlers are maintained

- **Database Configuration**:
  - PostgreSQL user and database creation needs to be migrated to Ansible PostgreSQL modules

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Then add SSL and security features
   - Finally, implement multi-site configuration

2. **cache** (Priority 2)
   - Implement Memcached and Redis configurations
   - Ensure proper security for Redis authentication

3. **fastapi-tutorial** (Priority 3)
   - Implement PostgreSQL database setup
   - Deploy FastAPI application
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora-based systems
2. The same network configuration (ports, IP addresses) will be maintained
3. Self-signed certificates are acceptable for the migrated solution
4. The FastAPI application repository will remain available at the same URL
5. The directory structure for web content and application code will remain the same
6. No changes to the application configuration or functionality are required
7. The migration will not involve containerization of the services
8. The same security requirements will apply to the Ansible-based solution