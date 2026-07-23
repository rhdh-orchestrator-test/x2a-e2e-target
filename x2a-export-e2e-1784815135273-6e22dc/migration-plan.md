# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- No complex custom resources or libraries
- Standard infrastructure components (Nginx, Redis, Memcached, PostgreSQL)
- Self-contained environment with Vagrant for testing

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)

- **fastapi-tutorial**:
    - Description: FastAPI Python application deployment with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Caching services configuration including Memcached and Redis
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (nginx, memcached, redisio)
- `solo.json`: Chef run list and configuration attributes
- `solo.rb`: Chef Solo configuration
- `Vagrantfile`: Defines the development VM (Fedora 42)
- `vagrant-provision.sh`: Provisions the VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` role or direct package installation

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration should maintain the same level of security or improve with Let's Encrypt integration
  - Ansible's `community.crypto` collection can handle certificate generation

- **Firewall Configuration**: 
  - UFW is configured to allow only SSH, HTTP, and HTTPS
  - Migration should use Ansible's `ansible.posix.firewalld` for Fedora or `community.general.ufw` for Ubuntu

- **SSH Hardening**:
  - Root login disabled
  - Password authentication disabled
  - Migration should use Ansible's `ansible.posix.ssh_config` module

- **System Hardening**:
  - Sysctl security settings
  - Fail2ban configuration
  - Migration should use Ansible's `ansible.posix.sysctl` module and templates for fail2ban

- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL user/password in fastapi-tutorial cookbook: "fastapi"/"fastapi_password"
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - The Chef cookbook dynamically creates site configurations based on attributes
  - Ansible solution will need to use loops with templates to achieve the same flexibility

- **SSL Certificate Generation**:
  - Self-signed certificates are generated for each site
  - Ansible will need to use the `community.crypto.openssl_*` modules to replicate this functionality

- **Service Orchestration**:
  - The current setup has interdependent services (Nginx depends on FastAPI, which depends on PostgreSQL)
  - Ansible playbook will need to maintain proper ordering with handlers and dependencies

- **Idempotency**:
  - Several Chef resources use `not_if` guards to ensure idempotency
  - Ansible tasks will need equivalent `when` conditions or `creates` parameters

### Migration Order

1. **cache** (Priority 1 - Low complexity)
   - Simple Redis and Memcached configuration
   - Good starting point with minimal dependencies

2. **nginx-multisite** (Priority 2 - Medium complexity)
   - Core infrastructure component
   - Multiple templates and configuration files
   - Security hardening features

3. **fastapi-tutorial** (Priority 3 - Medium complexity)
   - Application deployment
   - Depends on PostgreSQL
   - Requires systemd service configuration

### Assumptions

1. The target environment will continue to be Fedora 42 or similar Linux distributions.
2. Self-signed certificates are acceptable for the migrated solution (not production-ready).
3. The same directory structure for web content will be maintained.
4. The FastAPI application source will continue to be pulled from the same Git repository.
5. The migration will not involve changes to the application code or database schema.
6. The current security settings (firewall, SSH, fail2ban) are appropriate and should be maintained.
7. The Vagrant development environment will be replaced with an equivalent Ansible-based setup.
8. No external infrastructure dependencies exist beyond what's defined in the repository.