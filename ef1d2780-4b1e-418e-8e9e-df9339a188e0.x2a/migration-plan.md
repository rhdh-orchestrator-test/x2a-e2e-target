# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site web application environment with FastAPI backend, Nginx web server, and caching services. The migration scope includes 3 Chef cookbooks with moderate complexity. Based on the repository analysis, we estimate a 2-3 week timeline for complete migration, with the most complex components being the Nginx multi-site configuration and SSL certificate management.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site virtual hosts, SSL configuration, security hardening (fail2ban, UFW)

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

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef node configuration with run list and attribute overrides
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Defines development environment using Vagrant with Fedora 42
- `vagrant-provision.sh`: Bash script to provision the Vagrant VM with Chef

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with development environment using Fedora 42
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible `nginx` role from Galaxy or custom role
- **memcached (~> 6.0)**: Replace with Ansible `geerlingguy.memcached` role
- **redisio (~> 7.2.4)**: Replace with Ansible `geerlingguy.redis` role or custom Redis role

### Security Considerations

- **SSL Certificate Management**: Migration must handle self-signed certificates for multiple domains
  - Current implementation: Certificates stored in `/etc/ssl/certs` and `/etc/ssl/private`
  - Ansible approach: Use `community.crypto.x509_certificate` module or `geerlingguy.certbot` for Let's Encrypt

- **Security Hardening**: Several security measures need to be preserved:
  - fail2ban configuration: Migrate to Ansible `geerlingguy.security` role
  - UFW firewall rules: Use Ansible `community.general.ufw` module
  - SSH hardening (root login disabled, password auth disabled): Use Ansible `geerlingguy.security` role

- **Vault/secrets management**:
  - Redis password in cache cookbook: Detected hardcoded password `redis_secure_password_123`
  - PostgreSQL credentials in fastapi-tutorial cookbook: Detected hardcoded username/password `fastapi`/`fastapi_password`
  - Recommendation: Migrate to Ansible Vault for secure credential storage

### Technical Challenges

- **Multi-site Nginx Configuration**: The current Chef implementation manages multiple virtual hosts with SSL. This requires careful migration to ensure all sites remain properly configured.
  - Mitigation: Create a flexible Ansible role with templates that can handle multiple site configurations from variables

- **SSL Certificate Management**: The current implementation likely uses self-signed certificates that need to be generated and managed.
  - Mitigation: Use Ansible's crypto modules to generate and manage certificates, or integrate with Let's Encrypt

- **Service Orchestration**: The current setup manages multiple interdependent services (Nginx, FastAPI, PostgreSQL, Redis, Memcached).
  - Mitigation: Use Ansible's handlers and dependencies to ensure proper service restart ordering

- **Configuration Templating**: Several configuration files are generated from templates with complex variable substitution.
  - Mitigation: Carefully migrate ERB templates to Jinja2 format, preserving all variable references

### Migration Order

1. **cache cookbook** (low complexity, minimal dependencies)
   - Implement Redis and Memcached configuration
   - Migrate password management to Ansible Vault

2. **fastapi-tutorial cookbook** (moderate complexity)
   - Implement Python application deployment
   - Configure PostgreSQL database
   - Set up systemd service

3. **nginx-multisite cookbook** (high complexity, depends on other services)
   - Implement base Nginx configuration
   - Configure SSL certificates
   - Set up virtual hosts for multiple sites
   - Implement security hardening

### Assumptions

1. The current Chef setup is functional and represents the desired end state
2. Self-signed certificates are acceptable for the migrated solution (or Let's Encrypt will be implemented)
3. The same operating systems (Ubuntu 18.04+/CentOS 7+) will be targeted
4. The Vagrant development environment will be preserved or migrated to a similar setup
5. No CI/CD pipeline integration is required beyond what's currently implemented
6. The FastAPI application source will continue to be pulled from the same Git repository
7. The current security configurations (fail2ban, UFW, SSH hardening) are sufficient and should be preserved
8. Redis and Memcached configurations don't require significant changes beyond what's currently implemented