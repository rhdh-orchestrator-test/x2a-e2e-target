# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server setup with FastAPI application backend and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- Well-structured Chef cookbooks with clear separation of concerns
- Standard web server, application, and caching configurations
- Security hardening requirements that need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and SSL certificate management
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, SSH hardening)

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database setup
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Caching services configuration (Memcached and Redis)
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef Solo configuration with run list and node attributes
- `solo.rb`: Chef Solo configuration file with paths and log settings
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration for development/testing environment

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata and Vagrantfile)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible `nginx` role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible `memcached` role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible `redis` role or package installation tasks with custom configuration

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW. Migration should use Ansible's `firewalld` or `ufw` modules depending on target OS.
- **Fail2ban Setup**: Migrate fail2ban configuration to Ansible tasks with appropriate templates.
- **SSH Hardening**: Migrate SSH security settings (disable root login, password authentication) using Ansible's `lineinfile` or templates.
- **SSL Certificate Management**: Replace self-signed certificate generation with Ansible's `openssl_*` modules.
- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL credentials in fastapi-tutorial cookbook: "fastapi:fastapi_password"
  - No Chef Vault or encrypted data bags detected, but plain text passwords in recipes need to be secured

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of site configurations based on node attributes needs careful migration to Ansible variables and templates.
- **SSL Certificate Management**: Self-signed certificate generation logic needs to be replicated or replaced with Let's Encrypt integration.
- **Service Dependencies**: Ensuring proper ordering of service installations and configurations (e.g., PostgreSQL before FastAPI application).
- **Idempotency**: Ensuring all Ansible tasks are properly idempotent, especially for the database creation and user setup tasks.

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security hardening that should be applied early

2. **cache** (Priority 2)
   - Relatively simple configuration
   - Independent of other services
   - Required by applications

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on database and potentially caching services
   - More complex with multiple dependencies

### Assumptions

1. The target environment will continue to use Vagrant for development/testing
2. Self-signed certificates are acceptable for the migrated solution (vs. Let's Encrypt)
3. The same security hardening requirements will apply in the Ansible version
4. PostgreSQL and Redis passwords currently in plaintext will be migrated to Ansible Vault
5. The FastAPI application source will continue to be pulled from the same Git repository
6. The same operating systems (Fedora/Ubuntu/CentOS) will be supported
7. No changes to the application architecture are required during migration