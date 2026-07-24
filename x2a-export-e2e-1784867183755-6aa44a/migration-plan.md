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
- The codebase is well-structured with clear separation of concerns
- Limited custom resources and complex logic
- Several external dependencies that need to be replaced with Ansible Galaxy roles
- Security configurations that require careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening (fail2ban, ufw), and SSL certificate management
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and ufw

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Contains node attributes and run list - will be replaced by Ansible inventory variables
- `solo.rb`: Chef Solo configuration - will be replaced by Ansible configuration
- `Vagrantfile`: Defines the development VM - can be adapted for Ansible testing
- `vagrant-provision.sh`: Installs Chef and runs cookbooks - will be replaced with Ansible provisioning

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` module or community.general collection
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or DavidWittman.redis

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated in the Chef cookbook
  - Migration approach: Use Ansible's `openssl_*` modules for certificate generation
  - Consider integrating with Let's Encrypt for production environments

- **Firewall Configuration**:
  - UFW is configured in the Chef cookbook
  - Migration approach: Use Ansible's `ufw` module or `firewalld` module depending on target OS

- **SSH Hardening**:
  - Root login and password authentication are disabled
  - Migration approach: Use Ansible's `lineinfile` module or dedicated SSH hardening role

- **Fail2ban Configuration**:
  - Fail2ban is installed and configured
  - Migration approach: Use Ansible Galaxy role `geerlingguy.security` or create custom role

- **Vault/secrets management**:
  - Hardcoded Redis password in cache cookbook: `redis_secure_password_123`
  - PostgreSQL credentials in fastapi-tutorial cookbook: `fastapi:fastapi_password`
  - Migration approach: Use Ansible Vault for sensitive data

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Dynamically generating virtual host configurations for multiple sites
  - Mitigation: Use Ansible templates with loops over site definitions in variables

- **SSL Certificate Management**: 
  - Challenge: Ensuring secure handling of private keys and certificates
  - Mitigation: Use Ansible Vault for sensitive data and proper file permissions

- **Service Dependencies**: 
  - Challenge: Ensuring proper ordering of service deployments (e.g., PostgreSQL before FastAPI)
  - Mitigation: Use Ansible handlers and proper task dependencies

- **Idempotent Security Configurations**: 
  - Challenge: Ensuring security configurations are applied idempotently
  - Mitigation: Use Ansible's state modules rather than direct command execution

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx configuration, then add SSL and security features

2. **cache** (Priority 2)
   - Relatively simple configuration with well-established Ansible Galaxy alternatives
   - Independent of other services

3. **fastapi-tutorial** (Priority 3)
   - Most complex with database dependencies and application deployment
   - Depends on Nginx for serving

### Assumptions

1. The target environment will continue to be Fedora 42 or similar Linux distributions.
2. Self-signed certificates are acceptable for development, but production may require proper CA-signed certificates.
3. The current security configurations are appropriate and should be maintained in the Ansible implementation.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The current Redis and PostgreSQL passwords are for development only and will be replaced with secure passwords in production.
6. The current directory structure with separate roles for each component will be maintained in the Ansible implementation.
7. The Vagrant development environment will be maintained for testing the Ansible playbooks.