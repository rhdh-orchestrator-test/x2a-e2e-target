# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- Multiple interconnected services
- Security configurations that need careful migration
- External dependencies on community cookbooks

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and custom configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), custom site templates

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

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `Policyfile.rb`: Chef Policyfile defining the run list and cookbook dependencies
- `solo.json`: Configuration data for Chef Solo, contains site configurations and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Defines a Fedora 42 VM for development/testing with port forwarding and networking
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ based on cookbook metadata
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or custom Redis configuration tasks
- **ssl_certificate (~> 2.1)**: Replace with Ansible openssl_* modules for certificate management

### Security Considerations

- **Firewall Management**: The Chef cookbook uses UFW; migrate to Ansible's `ufw` module or `firewalld` module depending on target OS
- **Fail2ban Configuration**: Migrate fail2ban configuration to Ansible tasks using templates
- **SSH Hardening**: Preserve SSH security settings (disable root login, password authentication)
- **SSL Certificate Management**: Ensure secure handling of SSL certificates and private keys
- **Vault/secrets management**:
  - Redis password in plaintext in the cache cookbook (redis_secure_password_123)
  - PostgreSQL database credentials in plaintext in the fastapi-tutorial cookbook (fastapi:fastapi_password)
  - No Chef Vault or encrypted data bags detected, but sensitive data should be migrated to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple virtual hosts with SSL needs careful translation to Ansible templates
- **Service Orchestration**: Ensuring proper service restart/reload notifications are preserved in Ansible handlers
- **Idempotency**: Ensuring database creation and user setup tasks are idempotent in Ansible
- **Python Environment Management**: Converting the Python virtual environment setup to Ansible's pip module
- **SSL Certificate Generation**: Translating the self-signed certificate generation to Ansible's openssl_* modules

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security configurations that should be established first

2. **cache** (Priority 2)
   - Supporting services that the application may depend on
   - Relatively self-contained and can be migrated independently

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on properly configured infrastructure
   - Contains database setup that should come after core infrastructure

### Assumptions

1. The target environment will continue to be Fedora-based (or compatible with the existing configuration)
2. Self-signed certificates are acceptable for development/testing (production would likely use proper certificates)
3. The security requirements (fail2ban, ufw, SSH hardening) will remain the same
4. The FastAPI application repository will remain available at the specified URL
5. The current plaintext secrets will be migrated to Ansible Vault
6. The multi-site configuration pattern will be preserved in the Ansible roles
7. No custom Chef resources are used that would require special handling in Ansible
8. The PostgreSQL database schema and initialization is handled by the FastAPI application itself
9. The current VM specifications (2GB RAM, 2 CPUs) will remain sufficient for the application stack