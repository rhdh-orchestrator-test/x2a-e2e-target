# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI Python application backed by PostgreSQL. The migration scope is moderate, consisting of three primary cookbooks with external dependencies. Based on the complexity and size, this migration is estimated to take 2-3 weeks with 1-2 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, including security hardening
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate management, security hardening (fail2ban, ufw)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Chef dependency manager file listing cookbook dependencies. Will be replaced by Ansible Galaxy requirements.yml.
- `solo.json`: Chef node configuration with run list and attributes. Will be replaced by Ansible inventory variables.
- `solo.rb`: Chef configuration file. Will be replaced by Ansible configuration.
- `Vagrantfile`: Defines the development VM. Can be adapted to use Ansible provisioner instead of Chef.
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef. Will be replaced with Ansible provisioning.

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or create a custom role
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role from Galaxy

### Security Considerations

- **SSL Certificate Management**: 
  - Migration approach: Use Ansible's openssl_* modules for certificate management
  - Current implementation uses self-signed certificates stored in /etc/ssl/certs and /etc/ssl/private

- **Redis Authentication**:
  - Migration approach: Use Ansible Vault for the Redis password currently hardcoded as 'redis_secure_password_123'
  - Store sensitive values in encrypted vault files

- **PostgreSQL Authentication**:
  - Migration approach: Use Ansible Vault for the PostgreSQL password currently hardcoded as 'fastapi_password'
  - Implement idempotent database user and permission creation

- **System Hardening**:
  - Migration approach: Maintain security configurations for fail2ban, ufw, and SSH hardening
  - Use Ansible's built-in modules for firewall and SSH configuration

- **Vault/secrets management**:
  - Credentials detected: 2 (Redis password, PostgreSQL password)
  - Environment variables in .env file for FastAPI application

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation manages multiple virtual hosts with SSL
  - Mitigation: Use Ansible templates with loops to generate site configurations from variables

- **Service Orchestration**: 
  - Description: The current implementation manages dependencies between services (PostgreSQL before FastAPI)
  - Mitigation: Use Ansible handlers and proper task ordering to ensure services start in the correct order

- **Python Application Deployment**:
  - Description: The current implementation clones a Git repository and sets up a Python virtual environment
  - Mitigation: Use Ansible's git module and pip module to manage Python applications

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Create base Nginx role
   - Implement virtual host configuration
   - Implement SSL certificate management
   - Implement security hardening

2. **cache** (low complexity, standalone services)
   - Implement Memcached configuration
   - Implement Redis configuration with authentication

3. **fastapi-tutorial** (high complexity, depends on database)
   - Implement PostgreSQL database setup
   - Implement Python application deployment
   - Implement systemd service configuration

### Assumptions

1. The current Chef implementation is functional and represents the desired state
2. Self-signed certificates are acceptable for the migration (production would likely use proper certificates)
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git is available and will remain accessible
4. The migration will maintain the same security posture (fail2ban, ufw, SSH hardening)
5. The Vagrant development environment should be preserved with equivalent functionality
6. No CI/CD pipeline integration is required as part of the migration
7. The current implementation does not use Chef data bags or other external data sources
8. The target environment will continue to be Fedora-based systems