# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server environment with FastAPI application backend and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

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
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Configures caching services (Memcached and Redis) with security settings
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (nginx, memcached, redisio)
- `solo.json`: Chef run list and configuration attributes
- `solo.rb`: Chef Solo configuration
- `Vagrantfile`: Development environment configuration using Fedora 42
- `vagrant-provision.sh`: Provisioning script for Vagrant environment

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

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
  - Migration approach: Use Ansible `ansible.posix.ufw` module or `firewalld` module depending on target OS

- **Fail2ban Integration**:
  - Configured for SSH and web protection
  - Migration approach: Use Ansible `fail2ban` role or direct configuration

- **SSH Hardening**:
  - Root login disabled
  - Password authentication disabled
  - Migration approach: Use Ansible `ansible.posix.ssh_config` module or `devsec.hardening.ssh_hardening` role

- **Vault/secrets management**:
  - Redis password is hardcoded in the Chef recipe
  - PostgreSQL credentials are hardcoded in the FastAPI recipe
  - Migration approach: Move all credentials to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Maintaining the dynamic generation of site configurations
  - Mitigation: Use Ansible templates with loops over site definitions in variables

- **SSL Certificate Management**: 
  - Challenge: Ensuring proper permissions and security for private keys
  - Mitigation: Use Ansible's file permissions management and validate security settings

- **Service Orchestration**: 
  - Challenge: Ensuring proper service startup order (PostgreSQL before FastAPI, etc.)
  - Mitigation: Use Ansible handlers and meta dependencies between roles

- **Python Environment Management**:
  - Challenge: Properly setting up Python virtual environments
  - Mitigation: Use Ansible's `pip` module with virtualenv support

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add SSL certificate management
   - Add security hardening features
   - Add multi-site configuration

2. **cache** (Priority 2)
   - Independent service with external dependencies
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on PostgreSQL
   - Implement PostgreSQL installation and configuration
   - Implement Python environment setup
   - Implement application deployment and service configuration

### Assumptions

1. The target environment will continue to be Fedora 42 or similar Linux distributions.
2. Self-signed certificates are acceptable for development, but production may require proper CA-signed certificates.
3. The security requirements (fail2ban, firewall, SSH hardening) will remain the same.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The current hardcoded credentials are for development only and will be replaced with proper secret management in production.
6. The Vagrant development environment will be maintained, but may be replaced with a similar Ansible-based setup.
7. No custom Chef resources or complex Chef-specific patterns are in use that would require special handling.