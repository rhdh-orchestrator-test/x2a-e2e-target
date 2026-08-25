# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server setup with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- Total: 5-6 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- External dependencies are explicitly defined in the Berksfile
- Security configurations are comprehensive but straightforward
- The deployment is focused on a standard web stack (Nginx, Redis, Memcached, PostgreSQL)

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), sysctl security settings

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (both local and external from Chef Supermarket)
- `solo.json`: Contains node configuration including run list and attribute overrides
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Shell script to provision Chef in the Vagrant VM
- `Vagrantfile`: Defines the Vagrant VM configuration (Fedora 42)

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) as specified in cookbook metadata, with Fedora 42 used in Vagrant
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks
- **Python 3 and venv**: Use Ansible's package module and pip module for Python dependencies
- **PostgreSQL**: Use Ansible's postgresql_* modules from community.postgresql collection

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW; migrate to Ansible's ufw module or firewalld module depending on target OS
- **Fail2ban**: Migrate fail2ban configuration to Ansible tasks using templates
- **SSH Hardening**: Preserve SSH security settings (disable root login, disable password authentication)
- **SSL Certificates**: Migrate self-signed certificate generation to Ansible's openssl_* modules
- **Vault/secrets management**:
  - Redis password in cache/recipes/default.rb
  - PostgreSQL credentials in fastapi-tutorial/recipes/default.rb
  - Consider using Ansible Vault for these secrets

### Technical Challenges

- **Multi-site Nginx Configuration**: Ensure the dynamic generation of site configurations is preserved in Ansible
- **SSL Certificate Management**: Properly handle certificate generation and permissions
- **Service Dependencies**: Maintain proper ordering of service installations and configurations
- **Idempotency**: Ensure all operations remain idempotent, especially database user/schema creation

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Add security hardening (fail2ban, ufw)
   - Add multi-site configuration

2. **cache** (Priority 2)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (Priority 3)
   - Set up PostgreSQL database
   - Deploy FastAPI application
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Vagrant-based for development/testing
2. The same operating systems (Ubuntu/CentOS) will be supported
3. Self-signed certificates are acceptable (no Let's Encrypt integration required)
4. The FastAPI application source will remain available at the same Git repository
5. The same security requirements will apply (fail2ban, ufw, SSH hardening)
6. No CI/CD pipeline integration is required for the Ansible conversion
7. The Redis password and PostgreSQL credentials will need to be securely managed
8. The directory structure for web content will remain the same