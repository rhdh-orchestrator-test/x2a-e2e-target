# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application with PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, configuration templates, and security settings. Based on the complexity and scope, this migration is estimated to require 3-4 weeks of effort with a team of 2 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and custom configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl), custom resource for line-in-file operations

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file listing cookbook dependencies and versions. Will be replaced by Ansible Galaxy requirements.yml.
- `Vagrantfile`: Defines the development VM environment using Fedora 42. Can be adapted for Ansible testing with minimal changes.
- `solo.json`: Contains Chef run list and node attributes. Will be converted to Ansible group_vars or host_vars.
- `solo.rb`: Chef configuration file. Not needed in Ansible.
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef. Will be replaced by Ansible playbook calls.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or create custom role
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role from Galaxy
- **Python 3 + venv**: Use Ansible pip module for Python package management
- **PostgreSQL**: Use Ansible PostgreSQL modules for database management

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated in the nginx-multisite cookbook
  - Migration approach: Use Ansible crypto modules for certificate generation or integrate with Let's Encrypt

- **Firewall Configuration**: 
  - UFW is configured in the security.rb recipe
  - Migration approach: Use Ansible UFW module for firewall management

- **Fail2ban Configuration**: 
  - Fail2ban is configured in the security.rb recipe
  - Migration approach: Use Ansible to deploy fail2ban configuration templates

- **SSH Hardening**: 
  - SSH configuration is hardened in the security.rb recipe
  - Migration approach: Use Ansible to configure SSH settings or use ssh-hardening role from Galaxy

- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook
  - PostgreSQL password is hardcoded in the fastapi-tutorial cookbook
  - Migration approach: Use Ansible Vault for secret management

### Technical Challenges

- **Custom Resource Migration**: 
  - The nginx-multisite cookbook includes a custom lineinfile resource
  - Migration approach: Replace with Ansible's lineinfile module

- **Multi-site Configuration**: 
  - The nginx-multisite cookbook dynamically creates site configurations
  - Migration approach: Use Ansible templates with loops to generate site configurations

- **Service Orchestration**: 
  - The current setup manages service dependencies (e.g., FastAPI depends on PostgreSQL)
  - Migration approach: Use Ansible handlers and meta dependencies to ensure proper service ordering

- **Configuration File Modifications**: 
  - The cache cookbook includes a ruby_block to modify Redis configuration
  - Migration approach: Use Ansible's lineinfile or template modules with regexp capabilities

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security configurations that should be established first

2. **cache** (Priority 2)
   - Depends on external cookbooks (memcached, redisio)
   - Moderate complexity with Redis configuration modifications

3. **fastapi-tutorial** (Priority 3)
   - Application-specific configuration that depends on PostgreSQL
   - Involves git repository management, Python environment setup, and service configuration

### Assumptions

1. The target environment will continue to use Fedora 42 or a compatible Linux distribution.
2. Self-signed SSL certificates are acceptable for the migrated environment, or certificates will be provided externally.
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
4. The current security settings (fail2ban, ufw, SSH hardening) are appropriate for the target environment.
5. The Redis and PostgreSQL passwords used in the current configuration are development passwords and will be replaced with secure passwords in the Ansible Vault.
6. The current directory structure for web content (/opt/server/test, /opt/server/ci, /opt/server/status) will be maintained.
7. The FastAPI application will continue to run on port 8000 and be proxied through Nginx.
8. The current Nginx configuration templates contain standard configurations that can be directly translated to Ansible templates.