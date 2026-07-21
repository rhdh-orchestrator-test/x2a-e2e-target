# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure with three cookbooks that manage a multi-site Nginx web server, caching services (Redis and Memcached), and a FastAPI Python application with PostgreSQL database. The migration to Ansible is estimated to be of moderate complexity and should take approximately 2-3 weeks with 1-2 dedicated engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Multi-site Nginx configuration with SSL support and security hardening
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multiple virtual hosts, SSL configuration, security hardening (fail2ban, UFW)

- **cache**:
    - Description: Caching services configuration including Redis and Memcached
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with authentication, Memcached configuration, Redis log directory management

- **fastapi-tutorial**:
    - Description: FastAPI Python application deployment with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment, Git repository deployment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Manages cookbook dependencies (nginx, memcached, redisio). Will be replaced by Ansible Galaxy requirements.yml.
- `solo.json`: Contains node configuration and run list. Will be replaced by Ansible inventory and group_vars.
- `solo.rb`: Chef configuration file. Will be replaced by ansible.cfg.
- `Vagrantfile`: Defines development environment using Fedora 42. Can be adapted for Ansible testing.
- `vagrant-provision.sh`: Provisions the Vagrant VM with Chef. Will be replaced with Ansible provisioning.

### Target Details

Based on the source repository analysis:

- **Operating System**: Fedora 42 (as specified in the Vagrantfile)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be on-premises or local development

## Migration Approach

### Key Dependencies to Address

- **nginx (~12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~7.2.4)**: Replace with Ansible Redis role (e.g., geerlingguy.redis)

### Security Considerations

- **SSL Configuration**: Migrate SSL certificate paths and configuration from nginx-multisite cookbook
- **fail2ban and UFW**: Implement using Ansible security roles
- **SSH Hardening**: Migrate SSH security settings (disable root login, password authentication)
- **Vault/secrets management**:
  - Redis password hardcoded in cache/recipes/default.rb
  - PostgreSQL credentials hardcoded in fastapi-tutorial/recipes/default.rb
  - Consider using Ansible Vault for these secrets

### Technical Challenges

- **Multi-site Nginx Configuration**: The nginx-multisite cookbook manages multiple virtual hosts with SSL. This will require careful migration to ensure all sites remain properly configured.
- **Redis Configuration Hack**: The cache cookbook contains a Ruby block that modifies Redis configuration files after they're created. This will need special attention in Ansible.
- **FastAPI Application Deployment**: The fastapi-tutorial cookbook handles cloning a Git repository, setting up a Python virtual environment, and configuring a systemd service. This workflow will need to be carefully replicated in Ansible.

### Migration Order

1. **cache cookbook** (Low complexity, foundational service)
   - Implement Memcached and Redis configuration
   - Address Redis configuration hack

2. **nginx-multisite cookbook** (Medium complexity, depends on SSL certificates)
   - Implement basic Nginx configuration
   - Set up SSL certificates
   - Configure virtual hosts
   - Implement security features

3. **fastapi-tutorial cookbook** (High complexity, application deployment)
   - Set up PostgreSQL database
   - Deploy FastAPI application
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora-based systems
2. The multi-site configuration will remain the same (test.cluster.local, ci.cluster.local, status.cluster.local)
3. SSL certificates will be managed in the same way (self-signed for development)
4. The FastAPI application source will remain available at the same Git repository
5. The PostgreSQL database schema and user requirements will remain unchanged
6. The Redis and Memcached configuration requirements will remain the same
7. The security requirements (fail2ban, UFW, SSH hardening) will remain unchanged