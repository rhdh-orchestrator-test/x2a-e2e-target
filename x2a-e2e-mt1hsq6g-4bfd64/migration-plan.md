# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting three Chef cookbooks to Ansible roles, addressing security configurations, and ensuring proper dependency management.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- Total: 5-6 weeks

**Complexity Assessment:** Medium
- Well-structured Chef cookbooks with clear separation of concerns
- Standard infrastructure components (Nginx, Redis, Memcached, PostgreSQL)
- Security configurations that need careful migration
- Self-signed SSL certificates that need to be managed

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificates
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Manages cookbook dependencies, including external cookbooks from Chef Supermarket (nginx, memcached, redisio)
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

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package installation and configuration

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each virtual host
  - Migration approach: Use Ansible's openssl_* modules to generate certificates or community.crypto collection

- **Firewall Configuration**: 
  - UFW is configured to allow only SSH, HTTP, and HTTPS
  - Migration approach: Use Ansible's ufw module or firewalld module depending on target OS

- **SSH Hardening**:
  - Root login disabled
  - Password authentication disabled
  - Migration approach: Use Ansible's lineinfile module or openssh_config module

- **System Hardening**:
  - Sysctl security parameters
  - Migration approach: Use Ansible's sysctl module

- **Fail2ban Configuration**:
  - Configured to protect against brute force attacks
  - Migration approach: Use Ansible's template module to configure fail2ban

- **Vault/secrets management**:
  - Redis password hardcoded in attributes: "redis_secure_password_123"
  - PostgreSQL password hardcoded in recipe: "fastapi_password"
  - Migration approach: Use Ansible Vault to secure these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Maintaining the flexibility of the current multi-site setup
  - Mitigation: Create a flexible Ansible role with templates that can handle multiple site configurations

- **SSL Certificate Management**: 
  - Challenge: Ensuring proper permissions and security for SSL certificates
  - Mitigation: Use Ansible's file module with appropriate permissions and owner/group settings

- **Service Dependencies**: 
  - Challenge: Ensuring proper ordering of service deployment (PostgreSQL before FastAPI, etc.)
  - Mitigation: Use Ansible's meta dependencies and handlers to manage service ordering

- **Idempotency**: 
  - Challenge: Ensuring one-time operations like database creation are idempotent
  - Mitigation: Use Ansible's changed_when and failed_when directives to properly handle state

### Migration Order

1. **cache role** (Priority 1 - Low complexity)
   - Simple dependencies on external packages
   - Minimal configuration files
   - Good starting point to establish patterns

2. **nginx-multisite role** (Priority 2 - Medium complexity)
   - More complex with multiple templates and security configurations
   - Foundation for web services

3. **fastapi-tutorial role** (Priority 3 - Higher complexity)
   - Depends on PostgreSQL
   - Involves application deployment and database configuration
   - Requires systemd service management

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based systems
2. The Vagrant development environment will be maintained for testing
3. Self-signed certificates are acceptable (no Let's Encrypt or commercial certificates required)
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current security hardening approach is appropriate for the target environment
6. No additional monitoring or logging requirements beyond what's in the current configuration
7. The current Redis and Memcached configurations meet performance requirements
8. No high availability or clustering requirements for any services