# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server setup with FastAPI application backend and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- Security configurations are present and need careful migration
- External dependencies on Chef Supermarket cookbooks need Ansible Galaxy equivalents
- SSL certificate management requires special attention

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)

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

- `Berksfile`: Defines cookbook dependencies - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Contains node configuration and attributes - will be replaced by Ansible inventory and group_vars
- `solo.rb`: Chef configuration file - will be replaced by ansible.cfg
- `Vagrantfile`: Defines development VM - can be adapted for Ansible with minimal changes
- `vagrant-provision.sh`: Provisioning script - will be replaced by Ansible playbook

### Target Details

Based on the source configuration files:

- **Operating System**: Supports Ubuntu 18.04+ and CentOS 7+, with Fedora 42 used in Vagrant
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible `nginx` role from Galaxy or custom role
- **memcached (~> 6.0)**: Replace with Ansible `geerlingguy.memcached` role
- **redisio (~> 7.2.4)**: Replace with Ansible `geerlingguy.redis` role

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration approach: Use Ansible `community.crypto.openssl_*` modules

- **Firewall Configuration**: 
  - UFW is configured with default deny and specific allow rules
  - Migration approach: Use Ansible `community.general.ufw` module

- **Fail2ban Configuration**: 
  - Custom jail configuration
  - Migration approach: Use Ansible `fail2ban` role or tasks

- **SSH Hardening**: 
  - Root login disabled
  - Password authentication disabled
  - Migration approach: Use Ansible `ansible.posix.sshd_config` module

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the FastAPI recipe
  - Migration approach: Use Ansible Vault for all credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Chef uses templates and attributes to configure multiple sites
  - Mitigation: Create Ansible role with templates and variables for multi-site configuration

- **SSL Certificate Generation**: 
  - Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's `community.crypto` collection for certificate management

- **Service Orchestration**: 
  - Chef manages service dependencies and notifications
  - Mitigation: Use Ansible handlers and proper task ordering

- **PostgreSQL Configuration**: 
  - Database and user creation with permissions
  - Mitigation: Use Ansible `community.postgresql` collection

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Create base Nginx role
   - Implement SSL certificate management
   - Configure virtual hosts
   - Implement security hardening

2. **cache** (low complexity, standalone service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, application deployment)
   - Implement Python environment setup
   - Configure PostgreSQL database
   - Set up application deployment
   - Create systemd service

### Assumptions

1. The target environment will continue to use the same operating systems (Ubuntu 18.04+ or CentOS 7+)
2. Self-signed certificates are acceptable for development/testing
3. The same security requirements will apply in the new environment
4. The FastAPI application source code will remain at the same GitHub repository
5. The PostgreSQL database will be local to the application server
6. The Vagrant development environment will be maintained
7. No CI/CD pipeline integration is required (not present in current setup)
8. No monitoring or logging solutions are required beyond what's in the current setup