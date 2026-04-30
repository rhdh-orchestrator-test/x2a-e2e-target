# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, security configurations, and service deployments. Based on the complexity and scope, this migration is estimated to require 3-4 weeks with 1-2 dedicated engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and fail2ban integration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, rate limiting, UFW firewall configuration

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies with version constraints
- `solo.json`: Chef configuration file containing the run list and node attributes for Nginx sites and security settings
- `solo.rb`: Chef configuration file specifying cookbook paths and log settings
- `Vagrantfile`: Vagrant configuration for local development using Fedora 42, with port forwarding and network settings
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef and Berkshelf

### Target Details

Based on the source repository analysis:

- **Operating System**: The configuration supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) as specified in the cookbook metadata files. The Vagrantfile uses Fedora 42 for development.
- **Virtual Machine Technology**: Vagrant with libvirt provider is used for development environments.
- **Cloud Platform**: No specific cloud platform configurations were detected. The setup appears to be designed for on-premises or generic VM deployment.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role or direct configuration tasks
- **Python 3 and venv**: Use Ansible's pip module for Python dependency management
- **PostgreSQL**: Use Ansible's postgresql_* modules for database management

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should use Ansible's openssl_* modules or community.crypto collection.
  - Migration approach: Use Ansible's `community.crypto.openssl_certificate` module to generate self-signed certificates or integrate with Let's Encrypt using `community.crypto.acme_certificate`

- **Firewall Configuration**: UFW is configured with specific rules for SSH, HTTP, and HTTPS.
  - Migration approach: Use Ansible's `community.general.ufw` module to configure the same firewall rules

- **Fail2ban Integration**: Fail2ban is configured for SSH, Nginx HTTP auth, request limiting, and bot detection.
  - Migration approach: Use Ansible to deploy fail2ban configuration files and manage the service

- **System Hardening**: Sysctl parameters are set for network security.
  - Migration approach: Use Ansible's `ansible.posix.sysctl` module to apply the same kernel parameters

- **Vault/secrets management**:
  - Redis password in cache cookbook (hardcoded as 'redis_secure_password_123')
  - PostgreSQL database credentials in fastapi-tutorial cookbook (hardcoded as 'fastapi_password')
  - Migration approach: Use Ansible Vault to securely store and manage these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: The Chef cookbook dynamically generates Nginx site configurations based on node attributes.
  - Mitigation: Create Ansible templates for Nginx site configurations and use loops to generate multiple sites

- **SSL Certificate Generation**: Self-signed certificates are generated for each site.
  - Mitigation: Use Ansible's crypto modules to generate certificates or integrate with Let's Encrypt

- **Service Orchestration**: The current setup manages multiple interdependent services (Nginx, Redis, Memcached, PostgreSQL, FastAPI).
  - Mitigation: Use Ansible's handlers and dependencies to ensure proper service ordering

- **Security Hardening**: Comprehensive security measures are implemented across multiple layers.
  - Mitigation: Create dedicated Ansible roles for security hardening that can be applied consistently

### Migration Order

1. **cache cookbook** (Low complexity, foundational service)
   - Implement Redis and Memcached configuration
   - Secure Redis with password authentication

2. **nginx-multisite cookbook** (Medium complexity, depends on SSL certificates)
   - Implement Nginx installation and configuration
   - Configure SSL certificate generation
   - Set up virtual hosts
   - Implement security hardening (fail2ban, firewall, headers)

3. **fastapi-tutorial cookbook** (High complexity, depends on PostgreSQL)
   - Set up PostgreSQL database
   - Deploy FastAPI application from Git
   - Configure Python environment and dependencies
   - Create and manage systemd service

### Assumptions

1. The target environment will continue to support either Ubuntu (>= 18.04) or CentOS (>= 7.0) as specified in the cookbook metadata.
2. Self-signed certificates are acceptable for the migrated solution, or a clear path to integrate with Let's Encrypt will be provided.
3. The hardcoded credentials in the Chef recipes will be replaced with more secure credential management in Ansible.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain accessible.
5. The Nginx configuration assumes specific document roots (/opt/server/test, /opt/server/ci, /opt/server/status) that may need to be created or verified.
6. The current implementation assumes the www-data user exists for Nginx file ownership, which may need adjustment based on the target OS.
7. The migration will maintain the same level of security hardening present in the original Chef implementation.
8. The Vagrant development environment may need separate migration if local development testing is required.