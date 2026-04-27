# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web server environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated complexity is medium, with an estimated timeline of 3-4 weeks for a complete migration.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and proper SSL configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), sysctl security settings

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef configuration file containing the run list and node attributes
- `solo.rb`: Chef configuration file specifying cookbook paths and log settings
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration file for local development environment

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development/testing

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or create a custom role
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy
- **redisio (~> 7.2.4)**: Replace with Ansible redis role from Galaxy

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for development
  - Migration should maintain the same security level or improve it
  - Consider using Ansible's openssl module or certbot for Let's Encrypt integration

- **Firewall Configuration**: 
  - Current implementation uses UFW
  - Migrate to Ansible's ufw module or firewalld for Fedora

- **SSH Hardening**:
  - Root login disabled
  - Password authentication disabled
  - Migrate to Ansible's openssh_config module

- **Fail2ban Configuration**:
  - Migrate to Ansible fail2ban role or modules

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL password is hardcoded in the recipe (`fastapi_password`)
  - Migrate to Ansible Vault for secure credential storage

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - The current implementation uses templates to generate site configurations
  - Ansible will need equivalent template functionality with proper variable substitution

- **SSL Certificate Generation**:
  - Current implementation uses inline shell commands
  - Migrate to Ansible's openssl_* modules for better idempotency

- **PostgreSQL User and Database Creation**:
  - Current implementation uses shell commands
  - Migrate to Ansible's postgresql_* modules for better idempotency and error handling

- **Python Virtual Environment Management**:
  - Current implementation uses shell commands
  - Migrate to Ansible's pip module with virtualenv support

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Create base Nginx role
   - Implement SSL certificate generation
   - Implement security hardening (fail2ban, ufw)
   - Implement multi-site configuration

2. **cache** (low complexity, standalone services)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, application deployment)
   - Implement PostgreSQL database setup
   - Implement Python application deployment
   - Implement systemd service configuration

### Assumptions

1. The target environment will continue to be Fedora-based systems
2. Self-signed certificates are acceptable for development environments
3. The same security practices should be maintained in the Ansible implementation
4. The directory structure for web content and application code will remain the same
5. No changes to the application code itself are required
6. The Redis and PostgreSQL passwords in the current implementation are for development only and will be replaced with secure passwords in production
7. The current implementation does not include backup or monitoring solutions
8. The Vagrant setup is primarily for development and testing