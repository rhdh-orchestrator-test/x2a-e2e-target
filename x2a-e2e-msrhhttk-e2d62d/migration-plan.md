# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server setup with FastAPI application backend and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- No custom resources or complex Chef-specific patterns
- Standard web and application stack with common components
- Some security configurations that need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificate generation
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup, security hardening (fail2ban, ufw, sysctl)

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database setup
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment, Git repository deployment, PostgreSQL database, systemd service

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (nginx, memcached, redisio) - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Defines the run list and configuration attributes - will be replaced by Ansible inventory variables
- `solo.rb`: Chef Solo configuration - not needed in Ansible
- `Vagrantfile`: Defines the development VM - can be adapted for Ansible testing
- `vagrant-provision.sh`: Installs Chef and runs cookbooks - will be replaced by Ansible provisioner

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible community.general.nginx_* modules or geerlingguy.nginx role
- **memcached (~> 6.0)**: Replace with geerlingguy.memcached role
- **redisio (~> 7.2.4)**: Replace with geerlingguy.redis role

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW - migrate to Ansible's community.general.ufw module
- **Fail2ban Setup**: Migrate fail2ban configuration to Ansible's community.general.fail2ban module
- **SSH Hardening**: Migrate SSH security settings using Ansible's openssh_config module
- **SSL/TLS Management**: 
  - Self-signed certificates are generated for each site
  - Consider using Ansible's community.crypto.openssl_* modules
  - Potential upgrade path to Let's Encrypt using community.crypto.acme_* modules
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Configuration**: The nginx-multisite cookbook dynamically creates site configurations based on attributes. This pattern needs to be replicated in Ansible using templates and loops.
- **SSL Certificate Generation**: Self-signed certificates are generated for each site. This needs to be carefully migrated to ensure proper permissions and security.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL. These dependencies need to be properly managed in Ansible.
- **Idempotency**: Ensure all custom commands (like database creation) remain idempotent in Ansible.

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security configurations that should be established first
   - Relatively self-contained with clear templates and configurations

2. **cache** (Priority 2)
   - Supports the application but doesn't have complex dependencies
   - Relies on external roles (memcached, redis) that need to be integrated

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on other infrastructure components
   - Contains database setup that needs careful migration for idempotency

### Assumptions

1. The target environment will continue to be Fedora/RHEL-based systems, with potential support for Ubuntu/Debian
2. Self-signed certificates are acceptable for the migration (not moving to Let's Encrypt immediately)
3. The same directory structure for web content will be maintained
4. The same security policies will be applied in the Ansible configuration
5. PostgreSQL and Python versions will remain compatible with the FastAPI application
6. The FastAPI application repository URL and structure remain unchanged
7. The Redis and Memcached configuration parameters remain the same
8. The Vagrant development environment will be maintained for testing