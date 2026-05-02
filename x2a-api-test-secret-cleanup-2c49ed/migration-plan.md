# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application with PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, configuration templates, and security settings.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- **Total**: 5-6 weeks

**Complexity Assessment**: Medium
- Well-structured Chef cookbooks with clear separation of concerns
- External dependencies on community cookbooks that need Ansible equivalents
- Security configurations that require careful migration
- Hardcoded credentials that need to be moved to Ansible Vault

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, dependency on community cookbooks

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4)
- `Vagrantfile`: Defines development environment using Fedora 42, with port forwarding and network configuration
- `solo.json`: Contains Chef run list and node attributes for nginx sites and security configurations
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` module and custom templates
- **memcached (~> 6.0)**: Replace with Ansible's `apt`/`yum` modules and custom templates
- **redisio (~> 7.2.4)**: Replace with Ansible's `apt`/`yum` modules and custom templates
- **Python 3 and pip**: Use Ansible's `apt`/`yum` and `pip` modules
- **PostgreSQL**: Use Ansible's `postgresql_*` modules

### Security Considerations

- **fail2ban configuration**: Migrate fail2ban jail configuration to Ansible templates
- **UFW firewall rules**: Replace with Ansible's `ufw` module
- **SSH hardening**: Migrate SSH configuration to use Ansible's `lineinfile` or templates
- **Sysctl security settings**: Migrate to Ansible's `sysctl` module
- **Vault/secrets management**:
  - Redis password in cache cookbook: Move to Ansible Vault
  - PostgreSQL credentials in fastapi-tutorial cookbook: Move to Ansible Vault
  - SSL certificates and private keys: Use Ansible Vault or consider integration with external certificate management

### Technical Challenges

- **Custom Resource Migration**: The `lineinfile` custom resource in nginx-multisite needs to be replaced with Ansible's native `lineinfile` module
- **SSL Certificate Generation**: Replace Chef's OpenSSL commands with Ansible's `openssl_*` modules
- **Service Dependencies**: Ensure proper ordering of service dependencies in Ansible (PostgreSQL before FastAPI, etc.)
- **Configuration File Modifications**: The Redis configuration file modifications in the cache cookbook need careful migration to Ansible

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add virtual hosts and SSL configuration
   - Implement security hardening

2. **cache** (Priority 2)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper integration with Nginx

3. **fastapi-tutorial** (Priority 3)
   - Set up PostgreSQL database
   - Deploy FastAPI application
   - Configure systemd service
   - Integrate with Nginx and caching services

### Assumptions

1. The target environment will continue to be Fedora-based systems
2. The same network configuration and port mappings will be maintained
3. Self-signed SSL certificates are acceptable (production would likely use Let's Encrypt or similar)
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current security configurations are appropriate for the target environment
6. No additional monitoring or logging solutions need to be integrated
7. The current directory structure in `/opt/server/` for website content will be maintained
8. The PostgreSQL database schema is managed by the FastAPI application and not by Chef