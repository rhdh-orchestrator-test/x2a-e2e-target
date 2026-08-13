# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with FastAPI application backend and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- Total: 5-6 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- No custom resources or complex Chef-specific patterns
- Standard infrastructure components (Nginx, PostgreSQL, Redis, Memcached)
- Security configurations that need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall), sysctl security settings

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Configures caching services (Memcached and Redis) with security settings
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (nginx, memcached, redisio)
- `solo.json`: Chef run list and configuration attributes
- `solo.rb`: Chef Solo configuration
- `Vagrantfile`: Development environment configuration using Vagrant
- `vagrant-provision.sh`: Provisioning script for Vagrant environment

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible `nginx` role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible `geerlingguy.memcached` role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible `geerlingguy.redis` role or direct package installation and configuration

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration approach: Use Ansible `community.crypto.openssl_*` modules for certificate generation
  - Consider integrating with Let's Encrypt for production environments

- **Firewall Configuration**: 
  - UFW is configured with default deny and specific allow rules
  - Migration approach: Use Ansible `ansible.posix.ufw` module or `ansible.builtin.iptables` module

- **Fail2ban Integration**:
  - Configured for SSH and web services
  - Migration approach: Use Ansible `fail2ban` role or direct configuration

- **SSH Hardening**:
  - Root login disabled
  - Password authentication disabled
  - Migration approach: Use Ansible `ansible.posix.ssh_config` module or `devsec.hardening.ssh_hardening` role

- **Vault/secrets management**:
  - Redis password in plaintext in recipe: `redis_secure_password_123`
  - PostgreSQL credentials in plaintext in recipe: `fastapi:fastapi_password`
  - Migration approach: Use Ansible Vault for all credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Maintaining the flexibility of the current multi-site setup
  - Mitigation: Create a flexible Ansible role with templates that can handle multiple site configurations

- **SSL Certificate Management**: 
  - Challenge: Ensuring secure certificate generation and management
  - Mitigation: Use Ansible's crypto modules and consider integration with Let's Encrypt

- **Database Initialization**: 
  - Challenge: Ensuring idempotent database creation and user setup
  - Mitigation: Use Ansible's PostgreSQL modules with proper conditionals

- **Service Dependencies**: 
  - Challenge: Maintaining proper service startup order
  - Mitigation: Use Ansible's `meta: flush_handlers` and proper task ordering

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add SSL certificate management
   - Add security hardening features
   - Add multi-site configuration

2. **cache** (Priority 2)
   - Relatively self-contained with clear dependencies
   - Implement Memcached configuration
   - Implement Redis with proper secret management

3. **fastapi-tutorial** (Priority 3)
   - Depends on PostgreSQL and potentially the web server
   - Implement PostgreSQL installation and configuration
   - Implement Python environment setup
   - Implement application deployment and service configuration

### Assumptions

1. The target environment will continue to be Fedora/CentOS/Ubuntu based systems
2. Self-signed certificates are acceptable for development, but production may require proper CA-signed certificates
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
4. The current security settings (firewall, fail2ban, SSH hardening) are appropriate for the target environment
5. The current Redis and PostgreSQL passwords are development passwords and will be replaced with proper secrets in production
6. The Vagrant development environment will be maintained or replaced with an equivalent
7. No custom Chef resources or libraries are used that would require special handling