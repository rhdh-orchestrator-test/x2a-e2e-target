# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 3-4 weeks, with moderate complexity due to the multi-site configuration and security hardening requirements.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and fail2ban/ufw firewall configuration
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
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file listing cookbook dependencies (nginx, memcached, redisio). Will be replaced by Ansible Galaxy requirements.yml.
- `solo.json`: Chef run list and configuration attributes. Will be replaced by Ansible inventory variables.
- `solo.rb`: Chef configuration file. No direct Ansible equivalent needed.
- `Vagrantfile`: VM configuration for development/testing. Can be adapted for Ansible-based provisioning.
- `vagrant-provision.sh`: Shell script for Chef provisioning in Vagrant. Will be replaced by Ansible provisioning.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation and configuration
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package installation and configuration

### Security Considerations

- **SSL Certificate Management**: 
  - Current implementation generates self-signed certificates
  - Migration approach: Use Ansible's openssl_* modules for certificate generation or integrate with Let's Encrypt via certbot

- **Firewall Configuration**: 
  - Current implementation uses UFW
  - Migration approach: Use Ansible's ufw module or firewalld module (more appropriate for Fedora)

- **SSH Hardening**:
  - Current implementation disables root login and password authentication
  - Migration approach: Use Ansible's lineinfile module or dedicated ssh hardening role

- **Fail2ban Configuration**:
  - Current implementation installs and configures fail2ban
  - Migration approach: Use Ansible's template module to configure fail2ban

- **Vault/secrets management**:
  - Redis password hardcoded in recipe (redis_secure_password_123)
  - PostgreSQL password hardcoded in recipe (fastapi_password)
  - Migration approach: Use Ansible Vault for storing sensitive credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation dynamically generates Nginx site configurations based on node attributes
  - Mitigation: Use Ansible's template module with Jinja2 templates to achieve similar functionality

- **SSL Certificate Generation**:
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's openssl_* modules or integrate with certbot for Let's Encrypt certificates

- **Service Orchestration**:
  - Description: Multiple interdependent services (Nginx, Redis, Memcached, PostgreSQL, FastAPI application)
  - Mitigation: Use Ansible handlers and proper dependency management to ensure services are configured and started in the correct order

- **Fedora-specific Configuration**:
  - Description: The current Chef recipes may contain Ubuntu/Debian-specific commands that need adaptation for Fedora
  - Mitigation: Use Ansible's package module with appropriate package names for Fedora and adjust service names as needed

### Migration Order

1. **cache** (Priority 1 - low risk, foundational service)
   - Implement Redis and Memcached configuration
   - Secure Redis with password authentication

2. **nginx-multisite** (Priority 2 - moderate complexity)
   - Implement basic Nginx installation and configuration
   - Configure SSL certificate generation
   - Implement security hardening (fail2ban, firewall)
   - Configure virtual hosts

3. **fastapi-tutorial** (Priority 3 - depends on database)
   - Implement PostgreSQL installation and configuration
   - Deploy FastAPI application from Git
   - Configure Python environment and dependencies
   - Set up systemd service

### Assumptions

1. The target environment will continue to be Fedora-based systems (specifically Fedora 42 as indicated in the Vagrantfile).
2. Self-signed certificates are acceptable for the migrated solution, though the option to use Let's Encrypt should be considered.
3. The security hardening requirements will remain the same (fail2ban, firewall, SSH hardening).
4. The FastAPI application source repository (https://github.com/dibanez/fastapi_tutorial.git) will remain available.
5. The current Redis and PostgreSQL passwords are development/example passwords and will be replaced with secure passwords in production.
6. The Nginx sites configuration (test.cluster.local, ci.cluster.local, status.cluster.local) is for development purposes and may need to be adjusted for production.
7. The current implementation does not include backup or monitoring solutions, which may need to be addressed in the Ansible implementation.