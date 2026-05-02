# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- **Total**: 5-6 weeks

**Complexity Assessment**: Medium
- The codebase is well-structured with clear separation of concerns
- External dependencies on community cookbooks will need Ansible equivalents
- Security configurations are present and will need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall), sysctl security settings

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

- `Berksfile`: Dependency management file listing cookbook dependencies (nginx, memcached, redisio)
- `Vagrantfile`: Defines development VM using Fedora 42, configures networking and provisioning
- `solo.json`: Chef configuration file with run list and node attributes
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or collection (e.g., `ansible.posix.nginx`)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., `geerlingguy.memcached`)
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role (e.g., `geerlingguy.redis`)

### Security Considerations

- **Firewall Configuration**: UFW firewall rules need to be migrated to Ansible UFW module
- **Fail2ban Setup**: Configuration needs to be migrated to Ansible fail2ban role
- **SSH Hardening**: SSH configuration (disable root login, password authentication) needs careful migration
- **SSL Certificate Management**: Self-signed certificate generation needs to be handled in Ansible
- **Vault/secrets management**:
  - Redis password in cache cookbook (hardcoded as 'redis_secure_password_123')
  - PostgreSQL database credentials in fastapi-tutorial cookbook (hardcoded as 'fastapi_password')
  - Environment variables in .env file for FastAPI application

### Technical Challenges

- **SSL Certificate Generation**: The current implementation generates self-signed certificates; this needs to be replicated in Ansible or potentially upgraded to use Let's Encrypt
- **Multi-site Configuration**: The dynamic generation of Nginx site configurations based on node attributes needs to be carefully migrated to Ansible templates
- **Service Dependencies**: Ensuring proper ordering of service deployments (e.g., PostgreSQL before FastAPI application)
- **Security Hardening**: Ensuring all security configurations are properly migrated without introducing vulnerabilities

### Migration Order

1. **nginx-multisite** (Priority 1): Foundation for web services, other components depend on it
2. **cache** (Priority 2): Independent service but required by applications
3. **fastapi-tutorial** (Priority 3): Application deployment that depends on properly configured infrastructure

### Assumptions

1. The target environment will continue to be Fedora-based systems
2. Self-signed certificates are acceptable for the migrated solution (not production-ready)
3. The same directory structure and file paths will be maintained in the Ansible implementation
4. Hardcoded credentials will be replaced with Ansible Vault in the migrated solution
5. The current Chef implementation is functional and represents the desired end state
6. No additional features beyond what's in the current Chef implementation are required
7. The Vagrant development environment will be maintained but updated to use Ansible provisioning