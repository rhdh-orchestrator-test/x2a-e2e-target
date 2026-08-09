# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server setup with FastAPI application backend and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- Security configurations are comprehensive but straightforward
- Self-contained development environment using Vagrant
- Limited external dependencies (nginx, memcached, redis)

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
    - Key Features: Python virtual environment setup, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef configuration data including run list and node attributes
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `Vagrantfile`: Defines development VM using Fedora 42, network configuration, and provisioning
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible community.general.nginx_* modules or ansible-galaxy nginx role
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy
- **redisio (~> 7.2.4)**: Replace with Ansible redis role from Galaxy

### Security Considerations

- **Firewall Configuration**: The current setup uses UFW; migration should use appropriate firewall modules (ufw_rule or firewalld depending on target OS)
- **Fail2ban Setup**: Convert fail2ban configuration to Ansible
- **SSH Hardening**: Preserve SSH security settings (disable root login, password authentication)
- **SSL Certificate Management**: Current setup generates self-signed certificates; consider integrating with Ansible's crypto modules
- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL credentials in fastapi-tutorial cookbook: "fastapi:fastapi_password"
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Configuration**: The nginx-multisite cookbook dynamically creates site configurations based on node attributes; this pattern needs to be replicated in Ansible using loops and templates
- **SSL Certificate Generation**: Self-signed certificate generation needs to be handled with Ansible's openssl_* modules
- **Service Dependencies**: Ensuring proper ordering of service deployments (database before application, etc.)
- **Idempotency**: Ensuring all operations remain idempotent, particularly the database user/schema creation

### Migration Order

1. **cache role** (low complexity, foundational service)
   - Implement Memcached configuration
   - Implement Redis with authentication

2. **nginx-multisite role** (medium complexity, independent of other services)
   - Implement base Nginx configuration
   - Implement security hardening
   - Implement SSL certificate generation
   - Implement site configuration

3. **fastapi-tutorial role** (high complexity, depends on database)
   - Implement Python environment setup
   - Implement PostgreSQL configuration
   - Implement application deployment
   - Implement systemd service configuration

### Assumptions

1. The target environment will continue to be Fedora or similar Linux distributions
2. Self-signed certificates are acceptable for the migrated solution
3. The same security policies should be maintained in the Ansible implementation
4. The Vagrant development workflow should be preserved but updated for Ansible
5. No changes to the application code or database schema are required
6. The current directory structure in the target environment should be maintained