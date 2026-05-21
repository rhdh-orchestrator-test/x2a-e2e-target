# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 3-4 weeks, with moderate complexity due to the multi-site configuration and security considerations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site-specific configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site SSL configuration, security hardening (fail2ban, UFW firewall), self-signed certificate generation

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database provisioning, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints.
- `solo.json`: Chef configuration file defining the run list and node attributes for nginx sites and security settings.
- `solo.rb`: Chef configuration file specifying cookbook paths and logging settings.
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef.
- `Vagrantfile`: Defines the Vagrant VM configuration using Fedora 42 with port forwarding and networking setup.

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) as specified in cookbook metadata, but the Vagrantfile uses Fedora 42.
- **Virtual Machine Technology**: Vagrant with libvirt provider as specified in the Vagrantfile.
- **Cloud Platform**: Not specified, appears to be designed for local development/testing.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks with custom configuration

### Security Considerations

- **Firewall Configuration**: The Chef recipes configure UFW firewall rules that need to be migrated to Ansible's `ufw` module or `firewalld` module depending on target OS.
- **fail2ban Setup**: Fail2ban configuration needs to be migrated to Ansible tasks.
- **SSH Hardening**: SSH security settings (disabling root login, password authentication) need to be migrated to Ansible's `lineinfile` or template modules.
- **Vault/secrets management**:
  - Redis password in cache cookbook: `redis_secure_password_123` (hardcoded in attributes)
  - PostgreSQL credentials in fastapi-tutorial cookbook: Username `fastapi` with password `fastapi_password` (hardcoded in recipe)
  - SSL certificates and private keys managed in nginx-multisite cookbook (self-generated)

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple virtual hosts with SSL needs careful translation to Ansible templates and loops.
- **SSL Certificate Management**: Self-signed certificate generation logic needs to be replicated in Ansible.
- **Service Dependencies**: Ensuring proper ordering of service installations and configurations, particularly for the FastAPI application which depends on PostgreSQL.
- **Idempotency**: Ensuring all operations remain idempotent, especially database user creation and application deployment.

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - First migrate the basic Nginx installation and configuration
   - Then implement the SSL certificate generation
   - Finally implement the multi-site configuration

2. **cache** (low complexity, standalone services)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, application deployment)
   - Implement PostgreSQL installation and configuration
   - Implement Python environment setup and application deployment
   - Configure systemd service

### Assumptions

1. The target environment will continue to use the same operating systems (Ubuntu/CentOS/Fedora).
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or other certificate authority).
3. The hardcoded credentials in the Chef recipes will be replaced with Ansible Vault for improved security.
4. The FastAPI application source code will remain available at the same GitHub repository.
5. The Vagrant development environment will be maintained, but Chef provisioning will be replaced with Ansible.
6. The current security configurations (fail2ban, UFW, SSH hardening) are appropriate for the target environment.
7. The multi-site configuration with three virtual hosts (test, ci, status) will remain the same.