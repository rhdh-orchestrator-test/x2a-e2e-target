# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- Standard web server and application deployment patterns
- Multiple interdependent services (Nginx, FastAPI, PostgreSQL, Redis, Memcached)
- Security hardening requirements
- SSL certificate management

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)

- **fastapi-tutorial**:
    - Description: FastAPI Python application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Node configuration with run list and attributes - will be replaced by Ansible inventory and group_vars
- `solo.rb`: Chef configuration file - will be replaced by ansible.cfg
- `Vagrantfile`: Development environment definition - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisioning script for Vagrant - will be replaced by Ansible playbook calls

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks

### Security Considerations

- **Firewall Configuration**: UFW rules need to be migrated to Ansible's ufw module
- **Fail2ban Setup**: Configuration needs to be migrated to Ansible tasks
- **SSH Hardening**: SSH configuration needs to be migrated to Ansible's openssh_* modules
- **SSL Certificate Management**: Self-signed certificate generation needs to be migrated to Ansible's openssl_* modules
- **Vault/secrets management**:
  - Redis password in cache cookbook (plaintext in recipe)
  - PostgreSQL user password in fastapi-tutorial cookbook (plaintext in recipe)
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Configuration**: Ensuring the dynamic generation of Nginx site configurations works correctly in Ansible
- **SSL Certificate Management**: Properly handling certificate generation and permissions
- **Service Dependencies**: Maintaining correct order of operations for interdependent services
- **Idempotency**: Ensuring all operations are idempotent, especially database creation and user setup

### Migration Order

1. **nginx-multisite**: Foundation for web services, relatively self-contained
2. **cache**: Middleware services with external dependencies
3. **fastapi-tutorial**: Application deployment that depends on other services

### Assumptions

1. The target environment will continue to be Fedora/CentOS/Ubuntu based systems
2. The same network configuration and hostname setup will be maintained
3. Self-signed certificates are acceptable for development (production would likely use Let's Encrypt or similar)
4. The FastAPI application repository will remain available at the specified URL
5. PostgreSQL and Redis passwords are development credentials and will be replaced with Ansible Vault secured values
6. The current Vagrant setup will be maintained but modified to use Ansible provisioner