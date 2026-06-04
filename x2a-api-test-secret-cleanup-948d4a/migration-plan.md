# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application with PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- External dependencies on community cookbooks need to be replaced with Ansible Galaxy roles
- Security configurations and SSL certificate management require careful handling
- Secrets management needs to be improved during migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)

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

- `Berksfile`: Dependency management for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef configuration file with run list and node attributes
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration for development environment using Fedora 42

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development/testing

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` module and configuration templates
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role for Memcached (e.g., `geerlingguy.memcached`)
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role for Redis (e.g., `geerlingguy.redis`)

### Security Considerations

- **Firewall Configuration**: Migration of UFW rules to Ansible's `ufw` module
- **Fail2ban Setup**: Convert fail2ban configuration to Ansible tasks
- **SSH Hardening**: Migrate SSH security configurations (disable root login, password authentication)
- **Sysctl Security Settings**: Convert sysctl security configurations to Ansible
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the FastAPI cookbook (`fastapi:fastapi_password`)
  - SSL certificates are self-generated in the nginx-multisite cookbook
  - Recommendation: Use Ansible Vault for all credentials

### Technical Challenges

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Consider using Ansible's `openssl_*` modules or integrating with Let's Encrypt via `geerlingguy.certbot`
- **Multi-site Configuration**: The dynamic generation of Nginx site configurations based on node attributes will need to be replicated in Ansible using templates and variables
- **Redis Configuration Hacks**: The current implementation includes a Ruby block to modify Redis configuration files after they're created. This will need a cleaner approach in Ansible
- **PostgreSQL User/Database Creation**: The current implementation uses direct shell commands. This should be replaced with Ansible's PostgreSQL modules

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Create base Nginx role
   - Implement security hardening
   - Set up SSL certificate generation
   - Configure virtual hosts

2. **cache** (low complexity, standalone service)
   - Set up Memcached configuration
   - Implement Redis with proper authentication

3. **fastapi-tutorial** (high complexity, application deployment)
   - Set up PostgreSQL database
   - Deploy application from Git
   - Configure Python environment
   - Set up systemd service

### Assumptions

1. The target environment will continue to be Fedora-based systems
2. Self-signed certificates are acceptable for development/testing
3. The current security configurations are appropriate for the target environment
4. The FastAPI application repository will remain available at the specified URL
5. The current Redis configuration hack is a workaround for compatibility issues that may not be necessary in Ansible
6. The current directory structure in `/opt` and `/var/www` will be maintained
7. No additional monitoring or logging requirements beyond what's currently implemented
8. No high availability or clustering requirements for Redis or PostgreSQL