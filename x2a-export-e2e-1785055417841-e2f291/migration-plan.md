# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server setup with FastAPI application backend and caching services. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Scope**: 3 Chef cookbooks with external dependencies
**Complexity**: Medium
**Estimated Timeline**: 2-3 weeks

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificate generation
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup, security hardening (fail2ban, ufw, sysctl)

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database setup
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment, PostgreSQL database, systemd service

- **cache**:
    - Description: Caching services configuration including Memcached and Redis
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks - will be replaced by Ansible requirements.yml
- `solo.json`: Chef run list and configuration attributes - will be replaced by Ansible inventory variables
- `solo.rb`: Chef configuration file - will be replaced by ansible.cfg
- `Vagrantfile`: Development environment configuration - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisioning script for Vagrant - will be replaced by Ansible playbook

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package module
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package module

### Security Considerations

- **SSL/TLS Management**: 
  - Self-signed certificate generation for development
  - Migration approach: Use Ansible crypto modules (openssl_certificate, openssl_privatekey)

- **Firewall Configuration**: 
  - UFW setup with default deny policy and specific allow rules
  - Migration approach: Use Ansible ufw module or firewalld module depending on target OS

- **Fail2ban Integration**: 
  - Jail configuration for SSH and web services
  - Migration approach: Use Ansible fail2ban module or template module for configuration

- **SSH Hardening**: 
  - Disable root login and password authentication
  - Migration approach: Use Ansible ssh_config module or template module

- **Vault/secrets management**:
  - Redis password in cache cookbook (hardcoded as 'redis_secure_password_123')
  - PostgreSQL password in fastapi-tutorial cookbook (hardcoded as 'fastapi_password')
  - Migration approach: Use Ansible Vault for sensitive values

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation uses Chef templates and attributes to configure multiple virtual hosts
  - Mitigation: Use Ansible template module with Jinja2 templates, maintaining the same structure but adapting to Ansible variable syntax

- **Service Orchestration**: 
  - Description: The FastAPI application depends on PostgreSQL being configured first
  - Mitigation: Use Ansible handlers and proper task ordering to ensure dependencies are met

- **SSL Certificate Generation**: 
  - Description: Self-signed certificates are generated for each virtual host
  - Mitigation: Use Ansible's openssl_* modules to generate certificates with proper permissions

- **Security Hardening**: 
  - Description: Multiple security layers (fail2ban, ufw, sysctl, SSH) need to be coordinated
  - Mitigation: Create separate security role with appropriate tags for selective application

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation and configuration
   - Add virtual host configuration
   - Implement SSL certificate generation
   - Add security hardening features

2. **cache** (low complexity, standalone service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on database)
   - Implement PostgreSQL database setup
   - Configure Python environment and application deployment
   - Set up systemd service

### Assumptions

1. The target environment will continue to be Fedora/CentOS/Ubuntu based on the current configuration
2. Self-signed certificates are acceptable for development (production would likely use Let's Encrypt or other CA)
3. The security requirements (fail2ban, ufw, SSH hardening) will remain the same
4. The FastAPI application repository URL will remain accessible
5. The multi-site configuration pattern will be maintained
6. Redis and Memcached will continue to be the caching solutions
7. PostgreSQL will continue to be the database for the FastAPI application