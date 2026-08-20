# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with FastAPI application backend and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- Moderate number of external dependencies
- Security configurations that need careful migration
- Self-contained development environment using Vagrant

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW, sysctl security settings

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Configures caching services including Memcached and Redis
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies - will be replaced by Ansible Galaxy requirements.yml
- `Vagrantfile`: Defines the development VM - can be adapted for Ansible testing
- `solo.json`: Contains node configuration - will be replaced by Ansible inventory and group_vars
- `solo.rb`: Chef configuration - will be replaced by ansible.cfg
- `vagrant-provision.sh`: Provisioning script - will be replaced by Ansible playbook calls

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or local development

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for development
  - Migration should maintain the same certificate paths and permissions
  - Consider using Ansible's openssl_* modules or community.crypto collection

- **Firewall Configuration**: 
  - UFW firewall rules need to be migrated
  - Use Ansible's ufw module to maintain the same security posture

- **SSH Hardening**:
  - SSH root login disabled
  - Password authentication disabled
  - Use Ansible's lineinfile or template module to configure sshd_config

- **Fail2ban Configuration**:
  - Fail2ban is used for brute force protection
  - Migrate fail2ban jail configuration using Ansible templates

- **Vault/secrets management**:
  - Credentials detected:
    - PostgreSQL user/password in fastapi-tutorial cookbook
    - Redis password in cache cookbook
  - Recommend using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - The current implementation uses Chef templates and attributes
  - Ansible solution will need to use templates and variables to achieve the same flexibility
  - Challenge: Maintaining the same level of abstraction for site configuration

- **Service Orchestration**: 
  - Chef notifies are used to reload/restart services when configurations change
  - Ansible handlers will need to be configured to maintain the same behavior
  - Challenge: Ensuring proper service restart ordering

- **PostgreSQL Database Setup**:
  - Current implementation uses inline SQL commands
  - Ansible solution should use postgresql_* modules for better idempotency
  - Challenge: Ensuring database operations are idempotent

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Add security hardening features
   - Add multi-site configuration

2. **cache** (Priority 2)
   - Relatively self-contained with clear dependencies
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (Priority 3)
   - Depends on PostgreSQL which needs to be configured properly
   - Requires proper service management
   - Implement database setup
   - Implement application deployment
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora-based systems
2. Self-signed certificates are acceptable for the migrated solution
3. The same directory structure and file paths will be maintained
4. The FastAPI application repository will remain available at the specified URL
5. The security requirements (SSH hardening, firewall, fail2ban) will remain the same
6. The Vagrant development environment will be maintained but updated to use Ansible
7. No additional monitoring or logging requirements beyond what's in the current configuration