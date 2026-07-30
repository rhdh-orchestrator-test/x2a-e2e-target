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
- Standard infrastructure components (Nginx, Redis, Memcached, FastAPI)
- Security configurations that need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: FastAPI Python application deployment with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database configuration, systemd service management

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and SSL certificate management
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup, security hardening with fail2ban and UFW

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef configuration file with run list and node attributes
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Defines the development VM environment using Vagrant
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ based on cookbook metadata
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible `nginx` role or use the `ansible.builtin.package` module to install Nginx directly
- **memcached (~> 6.0)**: Replace with Ansible `memcached` role or use the `ansible.builtin.package` module with appropriate templates
- **redisio (~> 7.2.4)**: Replace with Ansible `redis` role or use the `ansible.builtin.package` module with appropriate templates

### Security Considerations

- **SSL/TLS Management**: 
  - Migration approach: Use Ansible's `openssl_*` modules for certificate generation
  - Consider integration with Let's Encrypt using `community.crypto.acme_certificate`

- **Firewall Configuration (UFW)**:
  - Migration approach: Use Ansible's `community.general.ufw` module to manage firewall rules

- **Fail2ban Configuration**:
  - Migration approach: Use Ansible's `community.general.fail2ban` module or template-based configuration

- **SSH Hardening**:
  - Migration approach: Use Ansible's `ansible.posix.sshd_config` module to manage SSH configuration

- **Vault/secrets management**:
  - Credentials detected:
    - Redis password in cache cookbook: `redis_secure_password_123`
    - PostgreSQL credentials in fastapi-tutorial cookbook: `fastapi:fastapi_password`
  - Migration approach: Use Ansible Vault to encrypt sensitive values

### Technical Challenges

- **Multi-site Nginx Configuration**:
  - Description: The current Chef implementation uses a dynamic approach to configure multiple Nginx sites
  - Mitigation strategy: Use Ansible loops with templates to achieve similar functionality

- **SSL Certificate Generation**:
  - Description: Self-signed certificates are generated for development environments
  - Mitigation strategy: Use Ansible's `community.crypto.openssl_*` modules to generate certificates

- **Service Orchestration**:
  - Description: The current implementation has interdependent services (Nginx, FastAPI, PostgreSQL)
  - Mitigation strategy: Use Ansible handlers and proper dependency ordering

### Migration Order

1. **cache** (Priority 1 - low risk, foundation service)
   - Simple configuration for Memcached and Redis
   - Few dependencies on other components

2. **nginx-multisite** (Priority 2 - moderate complexity)
   - Core web server configuration
   - Security hardening components
   - SSL certificate management

3. **fastapi-tutorial** (Priority 3 - higher complexity)
   - Application deployment
   - Database configuration
   - Depends on proper web server setup

### Assumptions

1. The target environment will continue to use Fedora or similar Linux distributions
2. Self-signed certificates are acceptable for development environments
3. The same security policies (SSH hardening, firewall rules) will be maintained
4. The FastAPI application source will remain available at the same GitHub repository
5. PostgreSQL database structure and user requirements will remain the same
6. The multi-site configuration pattern will be preserved
7. Redis and Memcached will continue to be used as caching solutions