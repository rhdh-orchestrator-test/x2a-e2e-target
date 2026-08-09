# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server setup with FastAPI backend and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing: 1 week
- Documentation and Knowledge Transfer: 1 week
- Total: 5-6 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- No custom resources or complex Chef-specific patterns
- Standard web and application server configurations
- Security configurations that need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and SSL certificate management
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database setup
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment, Git repository deployment, PostgreSQL database configuration, systemd service

- **cache**:
    - Description: Caching services configuration including Memcached and Redis
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef Solo configuration with run list and node attributes
- `solo.rb`: Chef Solo configuration file with paths and log settings
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration for development environment using Fedora 42

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or local development

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or memcached module
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or community.general.redis module

### Security Considerations

- **SSL Certificate Management**: The current setup generates self-signed certificates. Migration should:
  - Preserve the same certificate generation logic
  - Consider integrating with Ansible's crypto modules for certificate management
  - Maintain proper file permissions for private keys

- **Firewall Configuration**: The current setup uses UFW:
  - Migrate to Ansible's firewalld or ufw modules based on target OS
  - Ensure the same ports (22, 80, 443) remain open
  - Maintain default deny policy

- **Fail2ban Configuration**: 
  - Migrate fail2ban configuration using Ansible's template module
  - Ensure service is enabled and started

- **SSH Hardening**:
  - Maintain settings for disabling root login and password authentication
  - Use Ansible's lineinfile or template module for sshd_config

- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL credentials in fastapi-tutorial cookbook: User "fastapi" with password "fastapi_password"
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Preserving the dynamic generation of virtual host configurations based on site attributes
  - Mitigation: Use Ansible's with_items/loop constructs with templates to achieve similar functionality

- **SSL Certificate Generation**:
  - Challenge: Ensuring certificates are only generated when needed
  - Mitigation: Use Ansible's stat module to check for existing certificates before generation

- **Service Dependencies**:
  - Challenge: Maintaining proper service dependencies (e.g., FastAPI depends on PostgreSQL)
  - Mitigation: Use Ansible's meta dependencies or explicit handlers

- **Redis Configuration Hack**:
  - Challenge: The Chef cookbook includes a hack to fix Redis configuration
  - Mitigation: Create a proper template for Redis configuration in Ansible

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security configurations that should be established first

2. **cache** (Priority 2)
   - Relatively simple configuration
   - Required by the application but has fewer dependencies

3. **fastapi-tutorial** (Priority 3)
   - Depends on both web server and potentially cache services
   - More complex with database setup and application deployment

### Assumptions

1. The target environment will continue to use the same operating systems (Fedora/Ubuntu/CentOS)
2. Self-signed certificates are acceptable (no integration with Let's Encrypt or other CA)
3. The same directory structure for web content will be maintained
4. PostgreSQL will be installed locally rather than using an external database
5. The FastAPI application source will continue to be pulled from the same Git repository
6. The Vagrant development environment will be maintained but converted to use Ansible provisioner
7. No changes to the application architecture are planned during migration