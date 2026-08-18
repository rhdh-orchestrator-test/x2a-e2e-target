# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- No custom resources or complex Chef-specific patterns
- Standard infrastructure components (Nginx, Redis, Memcached, PostgreSQL)
- Security configurations that need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), sysctl security settings

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (nginx, memcached, redisio)
- `solo.json`: Chef configuration with run list and node attributes
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Bash script for provisioning Chef in Vagrant
- `Vagrantfile`: Vagrant configuration for development environment

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile) with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or local development

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or custom role
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy or custom role
- **redisio (~> 7.2.4)**: Replace with Ansible redis role from Galaxy or custom role

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration should maintain the same level of security or improve it
  - Consider using Ansible's openssl_* modules or certbot for Let's Encrypt integration

- **Firewall Configuration**: 
  - UFW firewall rules need to be migrated to equivalent Ansible ufw module tasks
  - Default deny policy with specific allows for SSH, HTTP, HTTPS

- **Fail2ban Configuration**: 
  - Fail2ban setup needs to be migrated to Ansible tasks
  - Template for jail.local configuration

- **SSH Hardening**:
  - Disable root login
  - Disable password authentication
  - These settings should be maintained in the Ansible configuration

- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL user/password in fastapi-tutorial cookbook: "fastapi"/"fastapi_password"
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - The Chef cookbook uses a data-driven approach to configure multiple Nginx sites
  - Ansible implementation should maintain this flexibility while ensuring proper template rendering

- **SSL Certificate Generation**:
  - Self-signed certificate generation logic needs to be replicated in Ansible
  - Ensure proper permissions and ownership of SSL files

- **Service Dependencies**:
  - FastAPI application depends on PostgreSQL
  - Ensure proper ordering of tasks in Ansible playbooks

- **System Tuning**:
  - Security-related sysctl settings need to be migrated
  - Consider using Ansible's sysctl module

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add SSL and security features
   - Finally, add multi-site configuration

2. **cache** (Priority 2)
   - Relatively simple configuration
   - Depends on external roles (memcached, redis)
   - Contains sensitive data (Redis password)

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on PostgreSQL
   - More complex with multiple steps (git clone, venv setup, database config, service setup)

### Assumptions

1. The target environment will continue to use Vagrant for development/testing
2. The same operating systems will be supported (Fedora, Ubuntu, CentOS)
3. Self-signed certificates are acceptable (no requirement for trusted certificates)
4. The current security configurations are appropriate and should be maintained
5. No changes to the application code or database schema are required
6. The same directory structure for web content will be maintained
7. No high availability or clustering requirements exist
8. No specific performance tuning beyond what's in the current configuration is needed
9. No backup or disaster recovery procedures are defined in the current configuration
10. No monitoring or logging solutions are configured beyond standard service logs