# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with FastAPI application backend and caching services (Redis and Memcached). The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The Chef cookbooks are well-structured and focused on specific concerns
- External dependencies are clearly defined
- Security configurations are present and need careful migration
- Self-signed SSL certificates are generated for multiple sites

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (both local and external from Chef Supermarket)
- `solo.json`: Contains Chef node attributes and run list for the Chef Solo run
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Defines the development VM using Vagrant with Fedora 42
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct configuration

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW firewall rules that need to be migrated to Ansible's `ufw` module
- **Fail2ban Setup**: Fail2ban configuration needs to be migrated using Ansible's template module
- **SSH Hardening**: SSH configuration (disabling root login, password authentication) should be migrated using Ansible's `lineinfile` or template modules
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - SSL certificates are generated and stored in specified paths
  - Recommend using Ansible Vault for all credentials in the migrated solution

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple Nginx site configurations based on node attributes will need careful translation to Ansible variables and templates
- **SSL Certificate Generation**: Self-signed certificate generation logic needs to be preserved or enhanced with Let's Encrypt support
- **Service Dependencies**: Ensuring proper ordering of service installations and configurations (e.g., PostgreSQL before FastAPI application)
- **Idempotency**: Ensuring all operations remain idempotent, particularly the database user/schema creation and SSL certificate generation

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Add security hardening (fail2ban, firewall)
   - Add virtual host configuration

2. **cache** (Priority 2)
   - Relatively independent service
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on database
   - Implement PostgreSQL installation and configuration
   - Implement Python environment setup
   - Implement application deployment and service configuration

### Assumptions

1. The target environment will continue to be Fedora-based, though the cookbooks support Ubuntu and CentOS as well
2. The self-signed SSL certificates approach will be maintained rather than switching to Let's Encrypt
3. The same directory structure for web content will be maintained
4. The same security policies (firewall rules, SSH hardening) will be applied
5. The Vagrant development environment will be preserved but updated to use Ansible provisioning
6. The current hardcoded credentials will be migrated to Ansible Vault
7. No changes to the application code or database schema are required
8. The same virtual host names will be maintained