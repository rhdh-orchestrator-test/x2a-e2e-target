# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services (Redis and Memcached) and a FastAPI application. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- No complex custom resources or libraries
- Standard infrastructure components (Nginx, Redis, Memcached, PostgreSQL)
- Security configurations need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment, Git repository deployment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (nginx, memcached, redisio) - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Contains node attributes and run list - will be replaced by Ansible inventory variables
- `solo.rb`: Chef configuration file - not needed in Ansible
- `Vagrantfile`: Defines development VM - can be adapted for Ansible testing
- `vagrant-provision.sh`: Installs Chef and runs cookbooks - will be replaced by Ansible provisioning

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ mentioned in cookbook metadata
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` role or direct package installation and configuration

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW with specific rules for SSH, HTTP, and HTTPS. Ansible will need to use the `ufw` module to replicate this functionality.
- **Fail2ban Setup**: The Chef cookbook installs and configures fail2ban. Ansible will need to use the `package` and `template` modules to replicate this.
- **SSH Hardening**: The Chef cookbook disables root login and password authentication. Ansible will need to use the `lineinfile` or `template` module to configure SSH.
- **SSL Certificate Management**: The Chef cookbook generates self-signed certificates. Ansible will need to use the `openssl_certificate` module.
- **Vault/secrets management**: 
  - Redis password is hardcoded in the cache cookbook
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook
  - These should be moved to Ansible Vault or another secrets management solution

### Technical Challenges

- **Multi-site Nginx Configuration**: The Chef cookbook dynamically creates Nginx site configurations based on node attributes. Ansible will need to use templates with loops to achieve the same functionality.
- **SSL Certificate Generation**: The Chef cookbook generates self-signed certificates for each site. Ansible will need to use the `openssl_certificate` module with loops.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL. Ansible will need to use handlers and wait_for to ensure services are started in the correct order.
- **Python Environment Management**: The Chef cookbook creates a Python virtual environment and installs dependencies. Ansible will need to use the `pip` module with a virtualenv parameter.

### Migration Order

1. **nginx-multisite** (Priority 1): This is the foundation for the web infrastructure and should be migrated first.
   - Start with basic Nginx installation
   - Add security configurations (fail2ban, ufw)
   - Add SSL certificate generation
   - Add site configuration templates

2. **cache** (Priority 2): This provides caching services that may be used by the web applications.
   - Implement Memcached configuration
   - Implement Redis configuration with authentication

3. **fastapi-tutorial** (Priority 3): This depends on the web and database infrastructure.
   - Implement PostgreSQL installation and configuration
   - Implement Python environment setup
   - Implement application deployment
   - Implement systemd service configuration

### Assumptions

1. The target environment will continue to use Fedora 42 or a compatible Linux distribution.
2. The self-signed certificates are for development only and may be replaced with proper certificates in production.
3. The Redis password and PostgreSQL credentials are development values and will be replaced with secure values in production.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The Vagrant development environment will be maintained for testing the Ansible playbooks.
6. No custom Chef resources or libraries are used that would require special handling in Ansible.
7. The current security configurations (fail2ban, ufw, SSH hardening) are sufficient and should be maintained in the Ansible playbooks.
8. The current multi-site Nginx configuration pattern should be preserved in the Ansible roles.