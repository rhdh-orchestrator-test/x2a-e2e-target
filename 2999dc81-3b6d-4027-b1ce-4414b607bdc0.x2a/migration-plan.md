# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This migration plan outlines the process of converting a Chef-based infrastructure to Ansible. The repository contains three Chef cookbooks managing a multi-site Nginx setup, caching services (Redis and Memcached), and a FastAPI Python application with PostgreSQL. The estimated complexity is medium, with an approximate timeline of 3-4 weeks for complete migration, including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificates
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup, security hardening (fail2ban, UFW firewall), sysctl security settings

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Manages cookbook dependencies (nginx, memcached, redisio) - will be replaced by Ansible Galaxy requirements.yml
- `Vagrantfile`: Defines development VM using Fedora 42 - can be adapted for Ansible testing with minimal changes
- `solo.json`: Contains Chef run list and node attributes - will be converted to Ansible group_vars or host_vars
- `solo.rb`: Chef configuration file - not needed in Ansible
- `vagrant-provision.sh`: Bash script for Chef provisioning in Vagrant - will be replaced by Ansible provisioner in Vagrantfile

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or custom role
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy or custom role
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role from Galaxy or custom role

### Security Considerations

- **SSL/TLS Configuration**: Migrate self-signed certificate generation logic to Ansible
  - Current approach: OpenSSL commands in Chef recipe
  - Ansible approach: Use `openssl_*` modules or community.crypto collection

- **Firewall Configuration**: Convert UFW rules to Ansible
  - Current approach: Chef execute resources for UFW commands
  - Ansible approach: Use `ufw` module

- **fail2ban Setup**: Migrate fail2ban configuration
  - Current approach: Chef template for jail.local
  - Ansible approach: Use `template` module or dedicated fail2ban role

- **SSH Hardening**: Migrate SSH security settings
  - Current approach: Chef execute resources modifying sshd_config
  - Ansible approach: Use `lineinfile` module or dedicated SSH hardening role

- **Vault/secrets management**:
  - Redis password in plain text in cache cookbook (redis_secure_password_123)
  - PostgreSQL password in plain text in fastapi-tutorial cookbook (fastapi_password)
  - Recommend using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple virtual hosts with SSL
  - Mitigation: Create Ansible templates with Jinja2 loops similar to the ERB templates

- **Service Orchestration**: Ensuring proper service restart/reload notifications
  - Mitigation: Use Ansible handlers for service management

- **PostgreSQL User/Database Management**: Converting PostgreSQL commands to Ansible modules
  - Mitigation: Use Ansible's postgresql_* modules instead of shell commands

- **Python Environment Setup**: Managing Python virtual environments and dependencies
  - Mitigation: Use Ansible's pip module with virtualenv parameter

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Implement virtual hosts configuration
   - Add security hardening features

2. **cache** (low complexity, standalone services)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, application deployment)
   - Set up PostgreSQL database and user
   - Configure Python environment and dependencies
   - Deploy application code
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions
2. Self-signed certificates are acceptable for the migrated environment (production would likely use Let's Encrypt or other CA)
3. The current security settings (fail2ban, UFW, SSH hardening) are appropriate for the target environment
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current Redis and PostgreSQL passwords are development passwords that will be replaced with secure passwords in production
6. The Nginx sites configuration in solo.json (test.cluster.local, ci.cluster.local, status.cluster.local) will remain the same
7. No custom Nginx modules or configurations beyond what's in the templates are required
8. The current directory structure in the target system (/opt/server/*, /var/www/*) will be maintained