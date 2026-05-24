# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup with three primary cookbooks: nginx-multisite, cache, and fastapi-tutorial. The infrastructure appears to be designed for a development/testing environment using Vagrant with Fedora 42. The migration to Ansible is estimated to be of moderate complexity, with an estimated timeline of 3-4 weeks for a small team (2-3 engineers).

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificates
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database provisioning, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks, lists both local and external dependencies
- `Vagrantfile`: Defines the development VM using Fedora 42 with libvirt provider
- `solo.json`: Chef run list and node attributes configuration
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ mentioned in cookbook metadata
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development/testing

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or community.general.memcached module
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or community.general.redis module

### Security Considerations

- **SSL Certificate Management**: Self-signed certificates are generated for development; in Ansible, use the community.crypto collection
- **Firewall Configuration**: UFW rules need to be migrated to appropriate firewall modules (ufw or firewalld depending on target OS)
- **Fail2ban Configuration**: Migrate fail2ban configuration to Ansible fail2ban role
- **SSH Hardening**: SSH configuration hardening needs to be migrated to Ansible ssh role or openssh_config module
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook
  - These should be migrated to Ansible Vault or an external secrets management solution

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple Nginx sites will require careful templating in Ansible
- **Service Orchestration**: The order of operations for the FastAPI application deployment needs to be preserved
- **Platform Compatibility**: The current setup supports multiple platforms (Ubuntu, CentOS); Ansible playbooks should maintain this compatibility
- **Redis Configuration**: The current setup includes a hack to fix Redis configuration which may need special handling in Ansible

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - First migrate the basic Nginx installation and configuration
   - Then add SSL certificate generation
   - Finally add security hardening features

2. **cache** (low complexity, standalone service)
   - Migrate Memcached configuration
   - Migrate Redis configuration with authentication

3. **fastapi-tutorial** (high complexity, application deployment)
   - Migrate PostgreSQL database setup
   - Migrate Python environment and application deployment
   - Migrate systemd service configuration

### Assumptions

1. The target environment will continue to be Fedora-based, though the cookbooks support Ubuntu and CentOS as well
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or other CA)
3. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate for the target environment
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The Redis configuration hack is necessary due to compatibility issues that may persist in the Ansible migration
6. The Vagrant development environment will be maintained, just converted to use Ansible provisioner instead of Chef