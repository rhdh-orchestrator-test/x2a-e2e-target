# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- Moderate number of external dependencies (nginx, memcached, redisio)
- Security configurations that need careful migration
- Self-signed SSL certificate generation that needs to be replicated

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Contains node attributes and run list - will be replaced by Ansible inventory variables
- `solo.rb`: Chef configuration file - no direct Ansible equivalent needed
- `Vagrantfile`: VM configuration for testing - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisioning script - will be replaced by Ansible playbook

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package installation

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates for each site. Ansible should replicate this functionality using the `openssl_certificate` module.
- **Firewall Configuration**: UFW configuration should be migrated to Ansible's `ufw` module.
- **Fail2ban Setup**: Fail2ban configuration should be migrated to Ansible tasks.
- **SSH Hardening**: SSH security settings (disable root login, password authentication) should be migrated to Ansible's `lineinfile` or template module.
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - These should be moved to Ansible Vault

### Technical Challenges

- **Multi-site Configuration**: The dynamic generation of multiple Nginx site configurations will need to be carefully migrated to Ansible's templating system.
- **SSL Certificate Generation**: Self-signed certificate generation logic needs to be preserved in Ansible.
- **Service Dependencies**: Ensuring proper ordering of service installations and configurations (e.g., PostgreSQL before FastAPI application).
- **Idempotency**: Ensuring all operations remain idempotent, especially the database user creation and SSL certificate generation.

### Migration Order

1. **nginx-multisite** (Priority 1): Core infrastructure component that other services depend on
   - Start with basic Nginx installation
   - Add SSL certificate generation
   - Add security hardening (fail2ban, ufw)
   - Add multi-site configuration

2. **cache** (Priority 2): Supporting services
   - Memcached configuration
   - Redis installation and configuration

3. **fastapi-tutorial** (Priority 3): Application deployment
   - PostgreSQL installation and configuration
   - Python environment setup
   - Application deployment
   - Service configuration

### Assumptions

1. The target environment will continue to be Fedora 42 as specified in the Vagrantfile.
2. The self-signed certificates are for development/testing purposes only and not for production use.
3. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate for the target environment.
4. The PostgreSQL and Redis passwords in the current configuration are for development only and will be replaced with secure passwords in Ansible Vault.
5. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain accessible.
6. The current directory structure for web content and configuration files will be maintained.
7. The Vagrant setup will be preserved for testing the Ansible playbooks.