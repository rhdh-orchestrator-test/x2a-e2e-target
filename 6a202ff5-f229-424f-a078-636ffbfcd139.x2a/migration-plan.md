# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for deploying multiple web services including a FastAPI application, Nginx with multiple SSL-enabled sites, and caching services (Redis and Memcached). The migration to Ansible is estimated to be of moderate complexity with approximately 2-3 weeks of effort required for a complete migration.

The repository consists of 3 Chef cookbooks with clear responsibilities and minimal external dependencies. The target environment appears to be Fedora 42 (based on the Vagrant configuration), with support for Ubuntu 18.04+ and CentOS 7+ mentioned in the cookbook metadata.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: SSL certificate generation, fail2ban integration, UFW firewall configuration, multi-site virtual hosts

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Configures caching services (Memcached and Redis) with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Manages cookbook dependencies, including external cookbooks from Chef Supermarket (nginx, memcached, redisio)
- `solo.json`: Contains the run list and configuration data for Chef Solo
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Defines the development VM using Fedora 42, with port forwarding and network configuration
- `vagrant-provision.sh`: Shell script to provision the VM with Chef Solo

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary), with support for Ubuntu 18.04+ and CentOS 7+
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or local development

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` module and community.general collection
- **memcached (~> 6.0)**: Replace with Ansible's `community.general.memcached` module
- **redisio (~> 7.2.4)**: Replace with Ansible's `community.general.redis` module or custom role

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated in the nginx-multisite cookbook
  - Migration approach: Use Ansible's `community.crypto.openssl_*` modules for certificate generation

- **Password Security**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - FastAPI database credentials are hardcoded in the fastapi-tutorial cookbook
  - Migration approach: Use Ansible Vault for all credentials

- **System Hardening**:
  - SSH hardening (disable root login, password authentication)
  - Firewall configuration with UFW
  - fail2ban setup
  - sysctl security parameters
  - Migration approach: Use `ansible.posix.firewall` and dedicated security roles from Ansible Galaxy

- **Vault/secrets management**:
  - 2 credentials detected in fastapi-tutorial (PostgreSQL username/password)
  - 1 credential detected in cache cookbook (Redis password)

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Maintaining the flexibility of the current multi-site setup
  - Mitigation: Use Ansible templates with similar structure to the current ERB templates, leveraging host_vars or group_vars for site-specific configuration

- **Service Orchestration**: 
  - Challenge: Ensuring proper service restart only when configuration changes
  - Mitigation: Use Ansible handlers similar to Chef notifications

- **PostgreSQL Database Setup**: 
  - Challenge: Creating database users and permissions
  - Mitigation: Use `community.postgresql` collection modules

### Migration Order

1. **cache cookbook** (Priority 1 - low complexity)
   - Simple configuration of Redis and Memcached services
   - Few external dependencies
   - Good starting point to establish patterns

2. **nginx-multisite cookbook** (Priority 2 - moderate complexity)
   - Core infrastructure component
   - Multiple templates and configurations
   - Security hardening components

3. **fastapi-tutorial cookbook** (Priority 3 - moderate complexity)
   - Application deployment
   - Database configuration
   - Systemd service management

### Assumptions

1. The target environment will continue to be Fedora/RHEL-based systems, with potential support for Ubuntu/Debian
2. The same directory structure for web content will be maintained
3. Self-signed certificates are acceptable for the migrated solution (vs. Let's Encrypt or other CA)
4. The current security hardening approach is sufficient and should be maintained
5. The Vagrant development environment should be preserved or migrated to a similar setup