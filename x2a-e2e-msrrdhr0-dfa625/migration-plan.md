# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- Total: 5-6 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- Multiple external dependencies need to be addressed
- Security configurations require careful migration
- Self-signed SSL certificates and multi-site configuration add complexity

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and SSL certificate management
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database setup
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

**CRITICAL PATH VERIFICATION:**
All Chef cookbooks with recipes/default.rb files have been verified and included in the inventory:
- cookbooks/nginx-multisite/recipes/default.rb - VERIFIED
- cookbooks/fastapi-tutorial/recipes/default.rb - VERIFIED
- cookbooks/cache/recipes/default.rb - VERIFIED

### Infrastructure Files

- `Berksfile`: Manages cookbook dependencies, including external cookbooks from Chef Supermarket
- `solo.json`: Contains node attributes and run list for Chef Solo
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Defines development VM using Fedora 42, with port forwarding and network configuration
- `vagrant-provision.sh`: Bash script to provision the VM with Chef Solo

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with development environment using Fedora 42
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or use the `ansible.builtin.package` module
- **memcached (~> 6.0)**: Replace with Ansible's `memcached` role from Ansible Galaxy or custom role
- **redisio (~> 7.2.4)**: Replace with Ansible's `redis` role from Ansible Galaxy or custom role

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration should maintain the same level of security or improve it
  - Consider using Ansible's `openssl_*` modules or `community.crypto` collection

- **Firewall Configuration**: 
  - UFW is configured to allow only SSH, HTTP, and HTTPS
  - Use Ansible's `ufw` module to maintain the same configuration

- **SSH Hardening**:
  - Root login is disabled
  - Password authentication is disabled
  - Use Ansible's `lineinfile` module or dedicated SSH role

- **System Hardening**:
  - Sysctl security parameters are configured
  - fail2ban is installed and configured
  - Use Ansible's `sysctl` module and community roles for fail2ban

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the FastAPI recipe (`fastapi`/`fastapi_password`)
  - These should be migrated to Ansible Vault or other secret management solution
  - Count of credentials detected: 2 (Redis password, PostgreSQL credentials)

### Technical Challenges

- **Multi-site Configuration**: 
  - The nginx-multisite cookbook manages multiple virtual hosts with different configurations
  - Solution: Create Ansible templates with loops to generate site configurations

- **SSL Certificate Generation**: 
  - Self-signed certificates are generated for each site
  - Solution: Use Ansible's `openssl_certificate` module to generate certificates

- **Service Dependencies**: 
  - FastAPI service depends on PostgreSQL
  - Solution: Use Ansible's `meta: flush_handlers` and proper ordering of tasks

- **Redis Configuration Hack**: 
  - The cache cookbook includes a hack to fix Redis configuration
  - Solution: Create proper Redis configuration template in Ansible

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Add security hardening (fail2ban, UFW)
   - Add multi-site configuration

2. **cache** (Priority 2)
   - Memcached and Redis services
   - Ensure Redis authentication is properly configured
   - Fix Redis configuration issues properly in Ansible

3. **fastapi-tutorial** (Priority 3)
   - Application deployment with database
   - Ensure proper dependency on PostgreSQL
   - Configure systemd service
   - Secure database credentials using Ansible Vault

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/Fedora
2. The same network configuration will be maintained
3. Self-signed certificates are acceptable for the target environment
4. The FastAPI application repository will remain available at the same URL
5. The same security requirements will apply in the target environment
6. The Vagrant development environment will be maintained
7. No additional monitoring or logging requirements beyond what's in the current code
8. No high availability or clustering requirements for Redis or Memcached