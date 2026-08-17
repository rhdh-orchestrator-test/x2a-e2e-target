# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server setup with FastAPI application backend and caching services. The migration scope includes 3 Chef cookbooks with moderate complexity. Based on the repository analysis, we estimate a 2-3 week timeline for complete migration, with the most complex components being the Nginx multi-site configuration and security hardening.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), sysctl security settings

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Configures caching services (Memcached and Redis) with security settings
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef Solo configuration file containing the run list and node attributes
- `solo.rb`: Chef Solo configuration file specifying file paths and log settings
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration file for local development environment

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or local development

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or community.general.memcached module
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or community.general.redis module

### Security Considerations

- **Firewall Configuration**: Migration of ufw rules to Ansible's firewalld or ufw modules
- **Fail2ban Configuration**: Migration of fail2ban jail configuration to Ansible's fail2ban module
- **SSH Hardening**: Migration of SSH security settings (disable root login, password authentication)
- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL credentials in fastapi-tutorial cookbook: User "fastapi" with password "fastapi_password"
  - SSL certificates and private keys stored in /etc/ssl/certs and /etc/ssl/private
  - Consider using Ansible Vault for storing these credentials securely

### Technical Challenges

- **SSL Certificate Generation**: The Chef cookbook generates self-signed certificates for development. Ansible will need to replicate this functionality or integrate with Let's Encrypt for production.
- **Multi-site Configuration**: The dynamic generation of multiple Nginx virtual hosts based on node attributes will need careful translation to Ansible templates.
- **System Hardening**: The comprehensive security settings (sysctl, fail2ban, ufw) will require multiple Ansible roles or careful module orchestration.
- **Service Dependencies**: Ensuring proper ordering of service installation, configuration, and startup in Ansible.

### Migration Order

1. **cache cookbook** (low complexity, standalone functionality)
   - Implement Memcached configuration
   - Implement Redis configuration with authentication

2. **nginx-multisite cookbook** (moderate complexity, core infrastructure)
   - Implement base Nginx installation and configuration
   - Implement SSL certificate generation
   - Implement virtual host configuration
   - Implement security hardening (fail2ban, ufw, sysctl)

3. **fastapi-tutorial cookbook** (high complexity, application deployment)
   - Implement PostgreSQL database setup
   - Implement Python application deployment
   - Implement systemd service configuration

### Assumptions

1. The target environment will continue to use the same operating systems (Fedora/Ubuntu/CentOS)
2. Self-signed certificates are acceptable for development, but production may require proper CA-signed certificates
3. The security requirements (fail2ban, ufw, SSH hardening) will remain the same
4. The application deployment strategy (Git clone + venv) will remain unchanged
5. The Nginx configuration structure (sites-available/sites-enabled) will be maintained
6. The PostgreSQL database structure and user permissions will remain the same
7. The Redis and Memcached configurations will maintain the same security settings
8. The Vagrant development environment will be maintained but converted to use Ansible provisioner