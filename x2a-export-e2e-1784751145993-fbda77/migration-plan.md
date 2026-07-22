# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- No custom resources or complex Chef-specific patterns
- Standard infrastructure components (Nginx, Redis, Memcached, PostgreSQL)

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, SSH hardening)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (nginx, memcached, redisio) - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Defines the run list and configuration attributes - will be replaced by Ansible inventory variables
- `solo.rb`: Chef Solo configuration - not needed in Ansible
- `vagrant-provision.sh`: Provisioning script for Vagrant - will be replaced by Ansible provisioner in Vagrantfile
- `Vagrantfile`: VM configuration for testing - will be updated to use Ansible provisioner instead of Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or native package installation tasks
- **memcached (~> 6.0)**: Replace with Ansible memcached role or native package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or native package installation tasks

### Security Considerations

- **SSL Certificate Management**: Self-signed certificates are generated for each site. In Ansible, use the `openssl_*` modules to generate certificates.
- **Firewall Configuration**: UFW is configured to allow only specific ports. Use Ansible's `ufw` module or `firewalld` module depending on the target OS.
- **SSH Hardening**: Root login and password authentication are disabled. Use Ansible's `lineinfile` or template module to configure SSH.
- **Fail2ban Configuration**: Fail2ban is installed and configured. Use Ansible to install and configure fail2ban.
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - These should be moved to Ansible Vault or an external secrets management system

### Technical Challenges

- **Multi-site Nginx Configuration**: The current implementation uses Chef templates and attributes to configure multiple Nginx sites. Ansible will need to replicate this dynamic site configuration using templates and variables.
- **SSL Certificate Generation**: Self-signed certificates are generated for each site. Ansible will need to handle certificate generation and management.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL, and the Nginx configuration depends on the FastAPI application. Ansible will need to handle these dependencies correctly.
- **Redis Configuration Hack**: There's a Ruby block that modifies the Redis configuration file after it's created. This will need to be handled differently in Ansible, possibly with templates or the `lineinfile` module.

### Migration Order

1. **cache** (low complexity): Simple configuration of Memcached and Redis services
2. **fastapi-tutorial** (medium complexity): Python application deployment with PostgreSQL
3. **nginx-multisite** (high complexity): Complex multi-site configuration with SSL and security hardening

### Assumptions

1. The target environment will continue to be Fedora 42 or similar Linux distributions.
2. The application architecture will remain the same (Nginx + FastAPI + PostgreSQL + Redis/Memcached).
3. Self-signed certificates are acceptable for development/testing, but production may require proper certificates.
4. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate for the target environment.
5. The Vagrant setup will be maintained for development and testing.
6. No custom Chef resources or complex Chef-specific patterns are used that would require special handling in Ansible.
7. The current hardcoded credentials will be replaced with more secure credential management in Ansible.