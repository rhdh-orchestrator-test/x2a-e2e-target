# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 3-4 weeks, with moderate complexity due to the interdependencies between services and security configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificates
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall)

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

- `Berksfile`: Dependency management file listing cookbook dependencies (nginx, memcached, redisio). Will be replaced by Ansible Galaxy requirements.yml.
- `solo.json`: Chef run list and node attributes configuration. Will be replaced by Ansible inventory variables.
- `solo.rb`: Chef configuration file. No direct Ansible equivalent needed.
- `Vagrantfile`: VM configuration for development/testing. Can be adapted for Ansible testing with minimal changes.
- `vagrant-provision.sh`: Provisioning script for Vagrant. Will be replaced by Ansible playbook calls.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or direct package installation
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible redis role from Galaxy or direct package installation

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each virtual host
  - Migration approach: Use Ansible's openssl_* modules to generate certificates

- **Firewall Configuration**: 
  - UFW is configured to allow only SSH, HTTP, and HTTPS
  - Migration approach: Use Ansible's ufw module for Ubuntu targets or firewalld module for RHEL/Fedora

- **Fail2ban Integration**: 
  - Configured to protect against brute force attacks
  - Migration approach: Use Ansible to deploy fail2ban configuration templates

- **SSH Hardening**: 
  - Root login disabled and password authentication disabled
  - Migration approach: Use Ansible's lineinfile or template module to configure SSH

- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (redis_secure_password_123)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (fastapi/fastapi_password)
  - Migration approach: Use Ansible Vault to secure these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current setup dynamically creates Nginx site configurations based on node attributes
  - Mitigation: Use Ansible's template module with Jinja2 templates to achieve similar functionality

- **Service Interdependencies**: 
  - Description: The FastAPI application depends on PostgreSQL, and the web server depends on the application being available
  - Mitigation: Use Ansible handlers and the 'notify' mechanism to ensure proper service restart order

- **SSL Certificate Generation**: 
  - Description: Self-signed certificates are generated for each virtual host
  - Mitigation: Use Ansible's openssl_* modules to generate certificates with proper permissions

- **Redis Configuration Patching**: 
  - Description: The current setup uses a ruby_block to modify Redis configuration after installation
  - Mitigation: Use Ansible's lineinfile module or template the entire configuration file

### Migration Order

1. **cache** (Priority 1 - low complexity)
   - Simple configuration of Memcached and Redis services
   - Few dependencies on other modules

2. **nginx-multisite** (Priority 2 - moderate complexity)
   - Security configurations
   - SSL certificate generation
   - Virtual host configuration

3. **fastapi-tutorial** (Priority 3 - higher complexity)
   - Requires database setup
   - Python environment configuration
   - Application deployment and service setup

### Assumptions

1. The target environment will continue to be Fedora-based systems (the Vagrantfile specifies Fedora 42)
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or commercial certificates)
3. The security requirements (fail2ban, UFW, SSH hardening) will remain the same
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current Redis and PostgreSQL passwords are development passwords and will be replaced with more secure passwords in production
6. The current directory structure in the target system (/opt/fastapi-tutorial, /var/www/sites) will be maintained
7. The Nginx virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local) will remain the same
8. The port mappings (80/443 for Nginx, 8000 for FastAPI) will remain unchanged