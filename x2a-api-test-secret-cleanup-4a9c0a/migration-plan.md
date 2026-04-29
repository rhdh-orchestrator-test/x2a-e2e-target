# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, configuration templates, and security settings. The estimated timeline for migration is 3-4 weeks, with moderate complexity due to the multi-site configuration and security requirements.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and fail2ban integration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, firewall configuration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment, Git repository deployment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4)
- `solo.json`: Defines the Chef run list and configuration attributes for nginx sites and security settings
- `solo.rb`: Configures Chef Solo paths and logging
- `Vagrantfile`: Defines a Fedora 42 VM with port forwarding for development/testing
- `vagrant-provision.sh`: Bash script to provision the Vagrant VM with Chef

### Target Details

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) based on cookbook metadata, with Fedora 42 used for development in Vagrant
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_config module
- **memcached (~> 6.0)**: Replace with Ansible memcached role
- **redisio (~> 7.2.4)**: Replace with Ansible redis role
- **PostgreSQL**: Replace with Ansible postgresql role or postgresql_* modules

### Security Considerations

- **SSL/TLS Configuration**: 
  - Self-signed certificate generation needs to be migrated to Ansible openssl_* modules
  - Secure TLS configuration (TLSv1.2/1.3 only, strong ciphers)

- **Firewall Configuration**: 
  - UFW configuration needs to be migrated to Ansible ufw module
  - Port allowances for SSH (22), HTTP (80), HTTPS (443)

- **Fail2ban Integration**:
  - Fail2ban configuration needs to be migrated to Ansible fail2ban role or templates

- **SSH Hardening**:
  - Disable root login and password authentication settings

- **Vault/secrets management**:
  - Redis password in cache cookbook (plaintext "redis_secure_password_123")
  - PostgreSQL user password in fastapi-tutorial cookbook (plaintext "fastapi_password")
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Converting the dynamic site generation from Chef to Ansible
  - Mitigation: Use Ansible with_items/loop constructs with templates

- **SSL Certificate Management**: 
  - Challenge: Ensuring proper permissions and security for SSL private keys
  - Mitigation: Use Ansible's file module with appropriate mode/owner/group settings

- **Service Dependencies**: 
  - Challenge: Ensuring proper service startup order (PostgreSQL before FastAPI app)
  - Mitigation: Use Ansible handlers and meta dependencies

- **Redis Configuration Hack**: 
  - Challenge: The Chef cookbook uses a ruby_block to modify Redis config
  - Mitigation: Create a proper Ansible template for Redis configuration

### Migration Order

1. **nginx-multisite cookbook** (moderate complexity)
   - Core web server functionality
   - Security configurations (fail2ban, ufw, SSH hardening)
   - SSL certificate generation

2. **cache cookbook** (low complexity)
   - Memcached configuration
   - Redis installation and configuration

3. **fastapi-tutorial cookbook** (high complexity)
   - PostgreSQL database setup
   - Python application deployment
   - Environment configuration
   - Systemd service setup

### Assumptions

1. The target environment will continue to be either Ubuntu (>= 18.04) or CentOS (>= 7.0)
2. The Vagrant development environment will be maintained but converted to use Ansible provisioner
3. Self-signed certificates are acceptable for development, but production would use proper certificates
4. The current security configurations (fail2ban, ufw, SSH hardening) are sufficient and should be maintained
5. The FastAPI application source code will continue to be pulled from the same Git repository
6. Redis and Memcached configurations will remain similar in terms of memory allocation and features
7. The multi-site Nginx configuration pattern will be preserved
8. PostgreSQL database name, user, and schema will remain the same
9. The current plaintext passwords in the cookbooks will be migrated to Ansible Vault
10. The systemd service configuration for the FastAPI application will remain similar