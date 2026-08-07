# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-service environment consisting of:
- Nginx web server with multiple SSL-enabled sites
- FastAPI Python application with PostgreSQL database
- Caching services (Memcached and Redis)

The migration scope involves converting 3 Chef cookbooks with approximately 10 recipes to Ansible roles and playbooks. Based on the complexity and interdependencies, this migration is estimated to require 2-3 weeks of effort with 1-2 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificates
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup, security hardening (fail2ban, UFW firewall)

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment, PostgreSQL database setup, systemd service configuration

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks. Lists both local and external cookbook dependencies.
- `solo.json`: Chef node configuration with run list and attribute overrides.
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings.
- `Vagrantfile`: Vagrant configuration for local development/testing.
- `vagrant-provision.sh`: Provisioning script for Vagrant VM setup with Chef.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04 or newer / CentOS 7 or newer (both supported in cookbooks)
- **Virtual Machine Technology**: VirtualBox (inferred from Vagrant usage)
- **Cloud Platform**: Not specified, appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible `nginx` role or `ansible.builtin.package` module
- **memcached (~> 6.0)**: Replace with Ansible `memcached` role or custom role using `ansible.builtin.package` and templates
- **redisio (~> 7.2.4)**: Replace with Ansible `redis` role or custom role using `ansible.builtin.package` and templates

### Security Considerations

- **SSL/TLS Management**: 
  - Migration approach: Use Ansible `community.crypto.openssl_*` modules for certificate generation
  - Consider integration with Let's Encrypt using `community.crypto.acme_*` modules

- **Firewall Configuration**: 
  - Migration approach: Use Ansible `ansible.builtin.ufw` module for Ubuntu or `ansible.posix.firewalld` for CentOS/RHEL

- **SSH Hardening**: 
  - Migration approach: Use Ansible `ansible.builtin.lineinfile` or `ansible.builtin.template` to configure SSH settings
  - Consider using `devsec.hardening.ssh_hardening` role

- **Fail2ban Configuration**: 
  - Migration approach: Use Ansible `ansible.builtin.package` and `ansible.builtin.template` modules

- **Vault/secrets management**:
  - Redis password in `cookbooks/cache/recipes/default.rb` (hardcoded)
  - PostgreSQL credentials in `cookbooks/fastapi-tutorial/recipes/default.rb` (hardcoded)
  - Migration approach: Use Ansible Vault for storing sensitive information

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation uses Chef templates and attributes to configure multiple virtual hosts
  - Mitigation: Create Ansible templates with similar structure, use Ansible variables for site configuration

- **SSL Certificate Generation**: 
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's `community.crypto.openssl_*` modules to generate certificates

- **Service Orchestration**: 
  - Description: The current setup has interdependent services (Nginx, FastAPI, PostgreSQL, Redis)
  - Mitigation: Use Ansible handlers and proper task ordering to ensure services are configured and started in the correct order

- **Configuration Templating**: 
  - Description: Multiple configuration templates are used for Nginx, security settings, etc.
  - Mitigation: Convert ERB templates to Jinja2 format for Ansible

### Migration Order

1. **cache** (Priority 1 - low complexity)
   - Simple configuration of Memcached and Redis services
   - Few dependencies on other modules

2. **fastapi-tutorial** (Priority 2 - moderate complexity)
   - Python application deployment with PostgreSQL
   - Moderate complexity with database setup and service configuration

3. **nginx-multisite** (Priority 3 - high complexity)
   - Most complex module with multiple recipes and security configurations
   - Depends on the applications it will serve

### Assumptions

1. The target environment will continue to support Ubuntu 18.04+ or CentOS 7+ as operating systems
2. Self-signed certificates are acceptable for development/testing (production would likely use proper certificates)
3. The same security hardening approach (fail2ban, UFW, SSH hardening) is desired in the migrated configuration
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current directory structure with multiple sites under `/var/www/` will be maintained
6. The PostgreSQL and Redis passwords currently hardcoded will be moved to Ansible Vault
7. The Vagrant development environment will be replaced with an Ansible-compatible alternative