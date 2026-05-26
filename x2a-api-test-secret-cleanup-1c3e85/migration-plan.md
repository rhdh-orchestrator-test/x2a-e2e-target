# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- **Total**: 5-6 weeks

**Complexity Assessment:** Medium
- The repository has well-structured Chef cookbooks with clear dependencies
- Security configurations are present and need careful migration
- External cookbook dependencies need to be replaced with Ansible Galaxy roles or custom implementations

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)

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

- `Berksfile`: Defines cookbook dependencies (nginx, memcached, redisio) - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Defines the run list and configuration attributes - will be replaced by Ansible inventory variables
- `solo.rb`: Chef Solo configuration - will be replaced by Ansible configuration
- `Vagrantfile`: Defines the development VM - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisions the VM with Chef - will be replaced with Ansible provisioning

### Target Details

- **Operating System**: Based on the cookbooks, the target systems are Ubuntu (>= 18.04) and CentOS (>= 7.0), with the Vagrantfile specifically using Fedora 42
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified in the repository, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role from Galaxy or direct package installation
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role or custom implementation
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` role or custom implementation

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW - migrate to Ansible's `ufw` module
- **Fail2ban Setup**: Migrate fail2ban configuration to Ansible's `fail2ban` module or custom role
- **SSH Hardening**: Migrate SSH security settings (disable root login, password authentication) to Ansible's `ssh` module
- **SSL Certificate Management**: Migrate self-signed certificate generation to Ansible's `openssl_*` modules
- **Vault/secrets management**:
  - Redis password in cache cookbook: `redis_secure_password_123` (hardcoded)
  - PostgreSQL password in fastapi-tutorial cookbook: `fastapi_password` (hardcoded)
  - Both credentials should be migrated to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple virtual hosts needs careful translation to Ansible templates
- **SSL Certificate Management**: Self-signed certificate generation needs to be properly implemented in Ansible
- **Service Dependencies**: Ensuring proper ordering of service deployments (e.g., PostgreSQL before FastAPI application)
- **Idempotency**: Ensuring all operations are idempotent, especially database user/schema creation

### Migration Order

1. **nginx-multisite** (Priority 1): Foundation for web services, moderate complexity
2. **cache** (Priority 2): Independent service but with external dependencies
3. **fastapi-tutorial** (Priority 3): Application deployment that depends on properly configured web server

### Assumptions

1. The target environment will continue to use the same operating systems (Ubuntu/CentOS/Fedora)
2. The deployment architecture will remain the same (single server with all services)
3. Self-signed certificates are acceptable for development (production would likely use Let's Encrypt or similar)
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current security configurations are appropriate for the target environment
6. No custom Chef resources or libraries are used that would require special handling
7. The current Vagrant setup for development/testing will be maintained