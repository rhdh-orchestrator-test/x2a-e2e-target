# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- Moderate number of external dependencies (nginx, memcached, redis)
- Security configurations that need careful migration
- Multiple site configurations with SSL certificates

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and custom configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), sysctl security settings

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints.
- `solo.json`: Chef configuration file defining the run list and node attributes. Contains site configurations and security settings.
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings.
- `Vagrantfile`: Defines the development VM using Fedora 42, with port forwarding and network configuration.
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef, installs dependencies and runs Chef Solo.

### Target Details

- **Operating System**: Fedora (based on Vagrantfile specifying "generic/fedora42"), with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Libvirt (specified in Vagrantfile)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or collection (e.g., `ansible.posix.nginx`)
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation and configuration
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package installation and configuration
- **Python 3 and venv**: Use Ansible's pip module for Python dependency management
- **PostgreSQL**: Use Ansible's postgresql modules for database management

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated in the Chef cookbook
  - Migration should use Ansible's `openssl_*` modules to generate certificates
  - Consider integrating with Let's Encrypt for production environments

- **Firewall Configuration**: 
  - UFW configuration needs to be migrated to Ansible's `ufw` module
  - Ensure all required ports (22, 80, 443) remain accessible

- **Fail2ban Setup**: 
  - Migrate fail2ban configuration to Ansible
  - Ensure jail configurations are properly translated

- **SSH Hardening**: 
  - Disable root login and password authentication settings need to be preserved
  - Use Ansible's `lineinfile` or templates for SSH configuration

- **Vault/secrets management**:
  - Redis password ("redis_secure_password_123") in cache cookbook
  - PostgreSQL database credentials ("fastapi:fastapi_password") in fastapi-tutorial cookbook
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Configuration**: The dynamic generation of multiple Nginx sites with SSL needs careful translation to Ansible templates and loops
- **Service Dependencies**: Ensuring proper ordering of service installation and configuration (e.g., PostgreSQL before FastAPI app)
- **SSL Certificate Generation**: Ensuring certificates are only generated when needed (idempotence)
- **Redis Configuration Hacks**: The Chef cookbook contains a hack to fix Redis configuration that needs to be properly addressed in Ansible
- **Python Environment Management**: Ensuring proper setup of Python virtual environments and dependencies

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add multi-site and SSL support
   - Implement security hardening (fail2ban, ufw, sysctl)

2. **cache** (Priority 2)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper service management

3. **fastapi-tutorial** (Priority 3)
   - Set up PostgreSQL database
   - Deploy FastAPI application from Git
   - Configure Python environment and dependencies
   - Create and enable systemd service

### Assumptions

1. The target environment will continue to be Fedora-based, with support for Ubuntu and CentOS as specified in the cookbook metadata.
2. Self-signed certificates are acceptable for development, but production environments may require proper CA-signed certificates.
3. The security settings (fail2ban, ufw, SSH hardening) are required in the migrated solution.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The current Redis and Memcached configurations are sufficient for the application's needs.
6. The current directory structure in the target environment (/opt/server/*, /var/www/*) should be preserved.
7. The current port configurations (Nginx on 80/443, FastAPI on 8000) should be maintained.
8. The PostgreSQL database name and credentials can remain the same in the migrated solution.