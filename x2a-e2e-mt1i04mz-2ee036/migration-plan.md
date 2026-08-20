# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server setup with FastAPI application backend and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- No complex custom resources or libraries
- Standard infrastructure components (Nginx, FastAPI, PostgreSQL, Redis, Memcached)
- Security configurations that need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
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

- `Berksfile`: Defines cookbook dependencies (nginx, memcached, redisio) - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Defines the run list and configuration attributes - will be replaced by Ansible inventory variables
- `solo.rb`: Chef configuration file - not needed in Ansible
- `Vagrantfile`: Defines the development VM - can be adapted for Ansible testing
- `vagrant-provision.sh`: Installs Chef and runs cookbooks - will be replaced by Ansible provisioning

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or create a custom role
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy or create a custom role
- **redisio (~> 7.2.4)**: Replace with Ansible redis role from Galaxy or create a custom role

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should preserve this functionality while allowing for future integration with Let's Encrypt or other certificate providers.
- **Firewall Configuration**: UFW rules need to be migrated to equivalent Ansible UFW module tasks.
- **Fail2ban Configuration**: Configuration needs to be migrated to Ansible tasks.
- **SSH Hardening**: SSH configuration hardening (disabling root login, password authentication) needs to be preserved.
- **System Hardening**: sysctl security settings need to be migrated.
- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL credentials in fastapi-tutorial cookbook: User "fastapi" with password "fastapi_password"
  - These should be migrated to Ansible Vault or another secrets management solution

### Technical Challenges

- **Multi-site Configuration**: The dynamic generation of Nginx site configurations based on attributes needs to be carefully migrated to Ansible templates and variables.
- **Service Dependencies**: Ensuring proper ordering of service deployments (e.g., PostgreSQL before FastAPI application).
- **SSL Certificate Generation**: Ensuring secure certificate generation and management in Ansible.
- **Idempotency**: Ensuring all operations remain idempotent, particularly for database user creation and SSL certificate generation.

### Migration Order

1. **nginx-multisite** (Priority 1): Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Add site configuration templates
   - Add security hardening features

2. **cache** (Priority 2): Supporting service with external dependencies
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (Priority 3): Application deployment that depends on other services
   - Implement PostgreSQL installation and configuration
   - Implement Python environment setup
   - Implement application deployment and service configuration

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions.
2. Self-signed certificates are acceptable for the migrated solution (production would likely use proper certificates).
3. The same directory structure for web content and application code will be maintained.
4. The PostgreSQL and Redis passwords in the code are development passwords and will be replaced with proper secrets management in production.
5. The Vagrant development environment will be maintained but updated to use Ansible provisioning.
6. No custom Chef resources or libraries are in use beyond what has been discovered in the analysis.
7. The current security configurations are appropriate for the target environment and should be preserved.