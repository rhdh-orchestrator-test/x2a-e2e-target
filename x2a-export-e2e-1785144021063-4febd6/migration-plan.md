# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server setup with FastAPI application backend and caching services. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- No custom resources or complex Chef-specific patterns
- Standard infrastructure components (Nginx, PostgreSQL, Redis, Memcached)
- Self-contained development environment using Vagrant

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)

- **cache**:
    - Description: Configures caching services (memcached and redis) with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Configures FastAPI tutorial application with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python environment setup, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (nginx, memcached, redisio) - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Defines the run list and configuration attributes - will be replaced by Ansible inventory variables
- `solo.rb`: Chef Solo configuration - will be replaced by ansible.cfg
- `Vagrantfile`: Defines the development VM - can be adapted for Ansible with minimal changes
- `vagrant-provision.sh`: Installs Chef and runs cookbooks - will be replaced with Ansible provisioner

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in Vagrant
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` role or direct package installation

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration should maintain the same security level or improve with Let's Encrypt integration
  - Certificate and key paths need to be maintained

- **Firewall Configuration**:
  - UFW is configured to allow only SSH, HTTP, and HTTPS
  - Ansible should use the `ufw` module to maintain the same configuration

- **SSH Hardening**:
  - Root login is disabled
  - Password authentication is disabled
  - Ansible should use the `ansible.posix.sshd` module to maintain these settings

- **Fail2ban Configuration**:
  - Custom jail configuration is applied
  - Ansible should use a dedicated role like `geerlingguy.security` or direct configuration

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the FastAPI recipe
  - These should be moved to Ansible Vault or an external secrets manager

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - The current setup uses templates to generate site configurations
  - Ansible will need to replicate this with templates and loops over site definitions

- **SSL Certificate Generation**:
  - Self-signed certificates are generated with OpenSSL commands
  - Ansible should use the `openssl_*` modules to generate certificates or integrate with Let's Encrypt

- **Application Deployment**:
  - The FastAPI application is deployed from Git with a virtual environment
  - Ansible should use the `git` module and appropriate Python modules

- **Database Configuration**:
  - PostgreSQL database and user creation is done with raw SQL commands
  - Ansible should use the `postgresql_*` modules for better idempotence

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Add security hardening (fail2ban, ufw, sysctl)
   - Add multi-site configuration

2. **cache** (low complexity, standalone service)
   - Configure Memcached
   - Configure Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on database)
   - Set up PostgreSQL database
   - Deploy FastAPI application
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Vagrant for development/testing
2. The same operating systems (Ubuntu/CentOS) will be supported
3. Self-signed certificates are acceptable (no need for Let's Encrypt in development)
4. The FastAPI application source will remain available at the same Git repository
5. No changes to the application architecture are required
6. The migration will maintain the same security posture or improve it
7. No additional monitoring or logging requirements beyond what's in the current configuration