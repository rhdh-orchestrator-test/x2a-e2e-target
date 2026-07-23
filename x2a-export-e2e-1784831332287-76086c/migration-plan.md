# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services (Redis and Memcached) and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, configuration templates, and security settings.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- Total: 5-6 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- Security configurations need careful attention
- External dependencies on community cookbooks need to be replaced with Ansible equivalents

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall), sysctl security settings

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (nginx, memcached, redisio)
- `solo.json`: Defines the Chef run list and configuration attributes
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Defines the Vagrant VM configuration (Fedora 42)

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be a local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or use the `ansible.builtin.package` module with templates
- **memcached (~> 6.0)**: Replace with Ansible's `memcached` role or use the `ansible.builtin.package` module with templates
- **redisio (~> 7.2.4)**: Replace with Ansible's `redis` role or use the `ansible.builtin.package` module with templates

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW. In Ansible, use the `ansible.posix.firewalld` or `community.general.ufw` module
- **Fail2ban**: The Chef cookbook configures fail2ban. In Ansible, use the `community.general.fail2ban` module
- **SSH Hardening**: The Chef cookbook disables root login and password authentication. In Ansible, use the `ansible.posix.sshd` module
- **SSL Certificates**: The Chef cookbook generates self-signed certificates. In Ansible, use the `community.crypto.openssl_*` modules
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Configuration**: The Chef cookbook uses a data structure to define multiple Nginx sites. In Ansible, this can be handled with variables and templates, but care must be taken to maintain the same flexibility
- **SSL Certificate Generation**: The Chef cookbook generates self-signed certificates. In Ansible, this can be handled with the `community.crypto.openssl_*` modules
- **Service Dependencies**: The FastAPI application depends on PostgreSQL. In Ansible, this can be handled with proper ordering of tasks and handlers

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Add security hardening (fail2ban, UFW)
   - Add multi-site configuration

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis configuration with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Implement PostgreSQL installation and configuration
   - Implement Python environment setup
   - Implement application deployment from Git
   - Implement systemd service configuration

### Assumptions

1. The target environment will continue to be Fedora 42 as specified in the Vagrantfile
2. The same directory structure for web content will be maintained
3. Self-signed certificates are acceptable for the migrated solution
4. The same security hardening measures are required in the Ansible version
5. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
6. The Redis and PostgreSQL passwords in the Chef cookbooks are development passwords and will be replaced with more secure passwords in production
7. The Vagrant setup is primarily for development/testing, and the Ansible playbooks should be usable in other environments as well