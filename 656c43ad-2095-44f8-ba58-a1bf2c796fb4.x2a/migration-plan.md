# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup with three cookbooks: `nginx-multisite`, `cache`, and `fastapi-tutorial`. The migration to Ansible will involve converting these cookbooks to Ansible roles and playbooks. The complexity is moderate, with an estimated timeline of 3-4 weeks for a complete migration, including testing and documentation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificates
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup, fail2ban integration, UFW firewall configuration, security hardening

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Manages cookbook dependencies, including external dependencies from Chef Supermarket (nginx, memcached, redisio)
- `solo.json`: Contains node configuration data including site configurations and security settings
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Provisioning script for Vagrant environment
- `Vagrantfile`: Defines the development VM using Fedora 42

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in the Vagrant development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or collection (e.g., `ansible.posix.nginx`)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., `geerlingguy.memcached`)
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role (e.g., `geerlingguy.redis`)

### Security Considerations

- **SSL/TLS Management**: 
  - Self-signed certificates are generated for development
  - Migration should maintain the same security level or improve it
  - Consider using Ansible's `community.crypto` collection for certificate management

- **Firewall Configuration**: 
  - UFW is configured to allow only SSH, HTTP, and HTTPS
  - Migration should use Ansible's firewall modules (`ansible.posix.ufw` or `ansible.posix.firewalld`)

- **SSH Hardening**:
  - Root login is disabled
  - Password authentication is disabled
  - Migration should maintain these security practices

- **Fail2ban Integration**:
  - Configured to protect against brute force attacks
  - Migration should include equivalent Ansible tasks

- **Vault/secrets management**:
  - Hardcoded credentials found in `cache` cookbook (Redis password: "redis_secure_password_123")
  - Hardcoded credentials in `fastapi-tutorial` cookbook (PostgreSQL user/password: "fastapi"/"fastapi_password")
  - Migration should use Ansible Vault to secure these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - The current setup uses Chef templates to generate site configurations
  - Ansible will need to replicate this dynamic site generation based on variables
  - Solution: Use Ansible templates with similar variable structure

- **Service Dependencies**:
  - The FastAPI application depends on PostgreSQL
  - Migration needs to maintain proper service ordering and dependencies
  - Solution: Use Ansible handlers and meta dependencies between roles

- **Custom Resource Handling**:
  - The nginx-multisite cookbook uses custom resources
  - Migration will need to convert these to Ansible modules or roles
  - Solution: Map custom resources to appropriate Ansible modules

### Migration Order

1. **cache** (Priority 1 - Low complexity)
   - Simple configuration of Memcached and Redis
   - Few dependencies on other components
   - Good starting point to establish patterns

2. **nginx-multisite** (Priority 2 - Moderate complexity)
   - Core infrastructure component
   - Contains security configurations that other components depend on
   - Moderate complexity due to templates and security configurations

3. **fastapi-tutorial** (Priority 3 - Moderate complexity)
   - Application deployment that depends on other infrastructure
   - Contains database setup and application configuration
   - Should be migrated after infrastructure components

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based systems
2. The development workflow will continue to use Vagrant for testing
3. Self-signed certificates are acceptable for development, but production may require proper certificates
4. The current security configurations are appropriate and should be maintained
5. The PostgreSQL database will continue to be deployed on the same host as the application
6. The Redis password and PostgreSQL credentials will need to be secured in the Ansible implementation
7. The FastAPI application source will continue to be pulled from the same Git repository
8. The current directory structure for web content will be maintained