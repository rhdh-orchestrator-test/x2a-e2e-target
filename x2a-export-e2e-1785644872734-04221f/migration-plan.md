# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration scope is moderate, involving 3 cookbooks with clear responsibilities and several external dependencies. The estimated timeline for migration is 2-3 weeks, with complexity primarily in the Nginx configuration and SSL certificate management.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL setup, security hardening (fail2ban, UFW)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment, Git repository deployment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Manages cookbook dependencies - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Contains node configuration and attributes - will be replaced by Ansible group_vars and host_vars
- `solo.rb`: Chef configuration file - will be replaced by ansible.cfg
- `Vagrantfile`: Defines the development VM - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisioning script for Vagrant - will be replaced by Ansible playbook

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrant provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks

### Security Considerations

- **SSL Certificate Management**: The nginx-multisite cookbook manages SSL certificates in `/etc/ssl/certs` and `/etc/ssl/private`. Migration should use Ansible's crypto modules for certificate management.
- **Redis Authentication**: Redis is configured with a hardcoded password (`redis_secure_password_123`) that should be moved to Ansible Vault.
- **PostgreSQL Authentication**: FastAPI database uses hardcoded credentials (`fastapi:fastapi_password`) that should be moved to Ansible Vault.
- **Security Hardening**: The following security measures need to be maintained:
  - fail2ban configuration
  - UFW firewall rules
  - SSH hardening (root login disabled, password authentication disabled)
  - Nginx security headers

### Technical Challenges

- **Multi-site Nginx Configuration**: The current setup dynamically creates multiple virtual hosts with SSL. This will require careful templating in Ansible.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL being configured first. Ansible handlers and proper task ordering will be needed.
- **Redis Configuration Patching**: The current Chef implementation includes a hack to fix Redis configuration. This will need a clean implementation in Ansible.

### Migration Order

1. **cache cookbook** (Low complexity, foundational service)
   - Implement Memcached configuration
   - Implement Redis with proper authentication

2. **nginx-multisite cookbook** (Medium complexity, core infrastructure)
   - Implement base Nginx installation
   - Implement security configurations
   - Implement SSL certificate management
   - Implement virtual host configuration

3. **fastapi-tutorial cookbook** (High complexity, application layer)
   - Implement PostgreSQL database setup
   - Implement Python environment and application deployment
   - Implement systemd service configuration

### Assumptions

1. The current Chef implementation assumes Fedora 42 as the target OS, but the cookbooks claim to support Ubuntu 18.04+ and CentOS 7.0+. The Ansible implementation should maintain this compatibility.
2. SSL certificates appear to be self-signed for development purposes. The migration will need to clarify if production certificates (e.g., Let's Encrypt) should be implemented.
3. The FastAPI application is pulled from a public GitHub repository. The migration should confirm if this is appropriate for production or if a private repository should be used.
4. The current implementation contains hardcoded credentials that should be secured using Ansible Vault in the migrated solution.
5. The Nginx configuration assumes specific domain names (test.cluster.local, ci.cluster.local, status.cluster.local). The migration should confirm if these are the actual production domains.