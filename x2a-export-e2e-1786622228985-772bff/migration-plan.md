# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application with PostgreSQL database. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- External dependencies are explicitly defined in Berksfile
- Security configurations are comprehensive but straightforward
- No complex custom resources or libraries identified

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW

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

- `Berksfile`: Defines cookbook dependencies (both local and external from Chef Supermarket)
- `solo.json`: Contains node attributes and run list for Chef Solo
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef
- `Vagrantfile`: Defines the Vagrant VM configuration (Fedora 42)

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in Vagrant
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create custom Nginx role
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or DavidWittman.redis

### Security Considerations

- **Firewall Configuration**: UFW rules need to be migrated to appropriate firewall modules (ufw or firewalld depending on target OS)
  - Migration approach: Use Ansible's `ufw` module for Ubuntu and `firewalld` module for CentOS/Fedora with conditional tasks

- **Fail2ban Setup**: Configuration needs to be migrated to Ansible
  - Migration approach: Use Ansible's `template` module to deploy fail2ban configuration files

- **SSH Hardening**: SSH configuration changes need to be migrated
  - Migration approach: Use Ansible's `lineinfile` module or templates to configure SSH daemon

- **SSL Certificate Management**: Self-signed certificate generation needs to be migrated
  - Migration approach: Use Ansible's `openssl_*` modules for certificate generation and management

- **Vault/secrets management**:
  - Redis password in cache cookbook: Found hardcoded password "redis_secure_password_123"
  - PostgreSQL credentials in fastapi-tutorial cookbook: Found hardcoded username "fastapi" and password "fastapi_password"
  - Migration approach: Move all credentials to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple virtual hosts based on node attributes
  - Mitigation: Use Ansible's template module with Jinja2 templates and variable structures similar to the Chef attributes

- **SSL Certificate Generation**: The self-signed certificate generation logic needs to be replicated
  - Mitigation: Use Ansible's `openssl_certificate`, `openssl_csr`, and `openssl_privatekey` modules

- **System Tuning**: The sysctl security configurations need to be migrated
  - Mitigation: Use Ansible's `sysctl` module to apply the same kernel parameters

- **Service Orchestration**: Ensuring services start in the correct order with proper notifications
  - Mitigation: Use Ansible handlers and proper task ordering with dependencies

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security configurations that should be applied first

2. **cache** (Priority 2)
   - Supporting services that the application may depend on
   - Relatively simple configuration with external dependencies

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on both web server and cache services
   - More complex with database setup and application configuration

### Assumptions

1. The target environment will continue to use the same operating systems (Ubuntu/CentOS/Fedora)
2. The same security requirements will apply in the new environment
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
4. The multi-site configuration pattern will be maintained
5. Self-signed certificates are acceptable for the target environment (no requirement for Let's Encrypt or commercial certificates)
6. The Vagrant development environment will be maintained but converted to use Ansible provisioner
7. No changes to the application architecture are required as part of the migration