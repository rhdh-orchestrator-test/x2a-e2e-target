# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, configuration templates, and security settings. Based on the complexity and scope, this migration is estimated to be of medium complexity and should take approximately 2-3 weeks with 1-2 dedicated engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and fail2ban/ufw firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, firewall rules

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file listing cookbook dependencies (nginx, memcached, redisio). Will be replaced by Ansible Galaxy requirements.yml.
- `Vagrantfile`: Defines development VM using Fedora 42. Can be adapted for Ansible testing with minimal changes.
- `solo.json`: Contains Chef node attributes and run list. Will be converted to Ansible group_vars or host_vars.
- `solo.rb`: Chef configuration file. Not needed in Ansible.
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM. Will be replaced by Ansible playbook.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role (e.g., geerlingguy.redis)

### Security Considerations

- **SSL/TLS Configuration**: 
  - Self-signed certificate generation for development
  - Proper SSL protocols and ciphers configuration
  - Migration approach: Use Ansible crypto modules for certificate generation

- **Firewall Configuration**: 
  - UFW firewall rules for SSH, HTTP, HTTPS
  - Migration approach: Use Ansible UFW module or firewalld module depending on target OS

- **Fail2ban Setup**: 
  - Protection against brute force attacks
  - Migration approach: Use Ansible to deploy fail2ban configuration files

- **SSH Hardening**: 
  - Disable root login
  - Disable password authentication
  - Migration approach: Use Ansible to modify sshd_config

- **Vault/secrets management**:
  - Redis password in plaintext in cache cookbook (redis_secure_password_123)
  - PostgreSQL password in plaintext in fastapi-tutorial cookbook (fastapi_password)
  - Migration approach: Use Ansible Vault for storing sensitive credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current setup dynamically generates Nginx site configurations based on node attributes
  - Mitigation: Use Ansible templates with similar logic, leveraging host_vars or group_vars for site definitions

- **SSL Certificate Management**: 
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible crypto modules for certificate generation or consider integrating with Let's Encrypt for production

- **Database Initialization**: 
  - Description: PostgreSQL database and user creation with proper permissions
  - Mitigation: Use Ansible PostgreSQL modules for idempotent database setup

- **Service Orchestration**: 
  - Description: Proper ordering of service installation, configuration, and startup
  - Mitigation: Use Ansible handlers and proper task ordering to ensure services are configured before starting

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Includes security hardening that should be applied first

2. **cache** (Priority 2)
   - Standalone services with external dependencies (memcached, redis)
   - Moderate complexity with authentication requirements

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on web server and database
   - Most complex with git deployment, virtual environment, and database setup

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions.
2. Self-signed certificates are acceptable for development, but production may require proper CA-signed certificates.
3. The security requirements (fail2ban, ufw, SSH hardening) will remain the same in the migrated environment.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. Redis and Memcached configurations don't require clustering or advanced features not mentioned in the current setup.
6. The current plaintext passwords in the Chef recipes will be replaced with Ansible Vault encrypted values.
7. The Nginx sites configuration (test.cluster.local, ci.cluster.local, status.cluster.local) will remain the same.
8. The current setup appears to be for development/testing purposes (Vagrant, self-signed certs) and may need additional hardening for production.