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
- The repository has well-structured Chef cookbooks with clear dependencies
- Security configurations are present and need careful migration
- External cookbook dependencies need to be replaced with Ansible Galaxy roles or custom implementations

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, fail2ban integration, UFW firewall

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, service management

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (nginx, memcached, redisio) - will be replaced with Ansible Galaxy requirements.yml
- `solo.json`: Contains node attributes and run list - will be converted to Ansible group_vars or host_vars
- `solo.rb`: Chef Solo configuration - will be replaced with ansible.cfg
- `Vagrantfile`: Defines the development VM - can be adapted for Ansible testing
- `vagrant-provision.sh`: Installs Chef and runs the cookbooks - will be replaced with Ansible provisioner

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role from Galaxy or create a custom role
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role or create a custom role
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` role or create a custom role

### Security Considerations

- **SSL/TLS Configuration**: 
  - Self-signed certificate generation needs to be migrated
  - SSL configuration parameters need to be preserved (TLS 1.2/1.3, cipher suites)
  - Certificate and key paths need to be maintained

- **Firewall Configuration**:
  - UFW rules need to be migrated to Ansible's `ufw` module
  - Default deny policy and specific allow rules need to be preserved

- **fail2ban Integration**:
  - Configuration needs to be migrated to use Ansible's `template` module
  - Service management needs to be handled

- **SSH Hardening**:
  - Root login and password authentication settings need to be migrated
  - Use Ansible's `lineinfile` module or templates for sshd_config

- **Vault/secrets management**:
  - Redis password needs to be secured (currently hardcoded as 'redis_secure_password_123')
  - PostgreSQL password needs to be secured (currently hardcoded as 'fastapi_password')
  - Consider using Ansible Vault for sensitive values

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Dynamically generating multiple virtual host configurations based on variables
  - Mitigation: Use Ansible's template module with loops to generate site configurations

- **SSL Certificate Generation**:
  - Challenge: Generating self-signed certificates with proper permissions
  - Mitigation: Use Ansible's `openssl_certificate` module with appropriate owner/group settings

- **Database Initialization**:
  - Challenge: Creating PostgreSQL users and databases idempotently
  - Mitigation: Use Ansible's `postgresql_*` modules instead of shell commands

- **Service Dependencies**:
  - Challenge: Ensuring services start in the correct order
  - Mitigation: Use Ansible's `meta: flush_handlers` and proper handler notification

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security configurations that should be established first

2. **cache** (Priority 2)
   - Supporting services that the application will use
   - Moderate complexity with external dependencies

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on both nginx and database
   - Contains database setup that should come after infrastructure components

### Assumptions

1. The target environment will continue to be Fedora-based systems
2. The same directory structure for web content will be maintained
3. Self-signed certificates are acceptable (no Let's Encrypt integration required)
4. The same security policies should be applied in the Ansible version
5. The FastAPI application source will continue to be pulled from the same Git repository
6. Redis and Memcached configurations will remain similar
7. No high availability or clustering is required for any services
8. No specific backup or monitoring solutions are currently implemented
9. The migration will not introduce new features beyond what's in the current Chef implementation
10. The Vagrant development environment will be maintained for testing