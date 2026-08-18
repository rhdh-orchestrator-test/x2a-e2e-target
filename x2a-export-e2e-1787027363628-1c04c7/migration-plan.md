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
- External dependencies on community cookbooks need to be replaced with Ansible Galaxy roles
- Security configurations need careful migration to maintain hardening standards

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), custom Nginx configuration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (both local and external from Chef Supermarket)
- `solo.json`: Contains the run list and configuration data for Chef Solo
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Defines the Vagrant VM configuration (Fedora 42)

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in Vagrant
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role from Galaxy or direct package installation
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role or custom tasks
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` role or custom tasks

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW with specific rules for SSH, HTTP, and HTTPS. Ansible will need equivalent `ufw` or `firewalld` tasks.
- **Fail2Ban Setup**: The Chef cookbook configures fail2ban with custom jail settings. Ansible will need to implement similar configuration.
- **SSH Hardening**: The Chef cookbook disables root login and password authentication. Ansible will need to maintain these security practices.
- **SSL Certificate Management**: Self-signed certificates are generated for each site. Ansible will need to handle certificate generation or integration with Let's Encrypt.
- **Vault/secrets management**:
  - Redis password in cache cookbook: `redis_secure_password_123`
  - PostgreSQL database credentials in fastapi-tutorial cookbook: User `fastapi` with password `fastapi_password`
  - SSL certificates and private keys stored in `/etc/ssl/certs` and `/etc/ssl/private`

### Technical Challenges

- **Multi-site Configuration**: The Chef cookbook dynamically creates Nginx site configurations based on attributes. Ansible will need to implement similar templating logic.
- **SSL Certificate Generation**: The Chef cookbook generates self-signed certificates for each site. Ansible will need to implement similar certificate generation or integrate with Let's Encrypt.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL, and the Nginx sites depend on the FastAPI application. Ansible will need to manage these dependencies correctly.
- **Idempotent Execution**: Ensuring that the Ansible playbooks are idempotent, especially for tasks like database creation and user setup.

### Migration Order

1. **nginx-multisite** (Priority 1): Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Implement security hardening (fail2ban, ufw)
   - Configure multi-site setup

2. **cache** (Priority 2): Supporting services for the application
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper service management

3. **fastapi-tutorial** (Priority 3): Application deployment
   - Set up PostgreSQL database
   - Deploy FastAPI application from Git
   - Configure Python environment
   - Set up systemd service

### Assumptions

1. The target environment will continue to be Vagrant VMs or similar Linux servers.
2. The same security requirements will apply in the new Ansible implementation.
3. Self-signed certificates are acceptable for development/testing environments.
4. The FastAPI application source code will remain available at the specified Git repository.
5. The directory structure for web content and application files will remain the same.
6. The migration will not involve changes to the application code itself, only the infrastructure configuration.
7. The current Chef implementation is functional and can be used as a reference for the expected behavior of the Ansible roles.
8. Secrets management will need to be addressed, possibly using Ansible Vault instead of hardcoded passwords.