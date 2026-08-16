# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backend. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- No custom resources or complex Chef-specific patterns are used
- Security configurations are present and need careful migration
- Hardcoded credentials will need to be moved to Ansible Vault

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall), sysctl security settings

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (nginx, memcached, redisio) - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Contains node attributes and run list - will be replaced by Ansible inventory variables
- `solo.rb`: Chef configuration file - not needed in Ansible
- `Vagrantfile`: Defines the development VM - can be adapted for Ansible with minimal changes
- `vagrant-provision.sh`: Provisioning script for Vagrant - will be replaced by Ansible playbook calls

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrant provider configuration)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or local development

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible community.general.nginx_* modules or geerlingguy.nginx role
- **memcached (~> 6.0)**: Replace with geerlingguy.memcached role
- **redisio (~> 7.2.4)**: Replace with geerlingguy.redis role

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW - migrate to Ansible's `ufw` module
- **fail2ban**: The Chef cookbook configures fail2ban - migrate to Ansible's `community.general.fail2ban` module
- **SSH Hardening**: The Chef cookbook disables root login and password authentication - migrate to Ansible's `lineinfile` module or the `ansible-hardening` role
- **Sysctl Security Settings**: The Chef cookbook applies sysctl security settings - migrate to Ansible's `sysctl` module
- **Vault/secrets management**:
  - Redis password in cache cookbook: Move to Ansible Vault
  - PostgreSQL credentials in fastapi-tutorial cookbook: Move to Ansible Vault
  - SSL certificates and private keys: Use Ansible's `community.crypto` modules for generation and management

### Technical Challenges

- **SSL Certificate Generation**: The Chef cookbook generates self-signed certificates - migrate to Ansible's `community.crypto.openssl_*` modules
- **Multi-site Configuration**: The Chef cookbook dynamically creates Nginx site configurations - use Ansible's templating and with_items to achieve similar functionality
- **Service Dependencies**: The FastAPI application depends on PostgreSQL - ensure proper ordering in Ansible playbooks using handlers and notify

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx configuration and site setup
   - Add SSL and security features

2. **cache** (Priority 2)
   - Relatively simple configuration with external dependencies
   - Ensure Redis password is properly secured in Ansible Vault

3. **fastapi-tutorial** (Priority 3)
   - Most complex with database, application code, and service management
   - Depends on proper functioning of the web server

### Assumptions

1. The target environment will continue to use Fedora 42 as specified in the Vagrantfile
2. The same directory structure for web content will be maintained (/var/www/*)
3. Self-signed certificates are acceptable for development (production would likely use Let's Encrypt)
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current security settings (firewall, fail2ban, SSH hardening) are appropriate for the target environment
6. The Redis password and PostgreSQL credentials will need to be secured in Ansible Vault
7. The Vagrant development environment will be maintained for testing