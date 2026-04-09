# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx configuration with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three primary Chef cookbooks to Ansible roles and playbooks, addressing external dependencies, and ensuring security configurations are properly maintained.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity:** Medium
- The repository has well-structured Chef cookbooks with clear dependencies
- Security configurations need careful attention during migration
- Multiple services with interdependencies require coordinated testing

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (both local and from Chef Supermarket) - will be replaced by Ansible Galaxy requirements
- `Policyfile.rb`: Defines the run list and cookbook dependencies - will be replaced by Ansible playbooks
- `Vagrantfile`: VM configuration for development/testing - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisioning script for Vagrant - will be replaced by Ansible provisioning
- `solo.json`: Chef node attributes - will be converted to Ansible variables
- `solo.rb`: Chef configuration - not needed in Ansible

### Target Details

Based on the source configuration files:

- **Operating System**: Supports Ubuntu 18.04+ and CentOS 7+, with Fedora 42 used in Vagrant development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role or direct package management
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` role or direct package management
- **ssl_certificate (~> 2.1)**: Replace with Ansible's `openssl_*` modules for certificate management

### Security Considerations

- **SSL Certificate Management**: Migration must maintain proper certificate generation and permissions
  - Use Ansible's `openssl_certificate`, `openssl_privatekey` modules
  - Ensure proper file permissions (640 for private keys)

- **Firewall Configuration (UFW)**: Maintain security rules
  - Use Ansible's `ufw` module to configure firewall rules
  - Ensure SSH, HTTP, and HTTPS ports remain accessible

- **fail2ban Configuration**: Maintain brute force protection
  - Use Ansible's `template` module to configure fail2ban
  - Ensure service is enabled and running

- **SSH Hardening**: Maintain secure SSH configuration
  - Use Ansible's `lineinfile` or `template` modules to configure SSH
  - Maintain settings for root login and password authentication

- **Redis Authentication**: Maintain password protection
  - Ensure Redis password is securely stored (consider Ansible Vault)
  - Configure Redis with authentication in Ansible

- **PostgreSQL Security**: Maintain database security
  - Use Ansible's `postgresql_*` modules for secure database setup
  - Store database credentials securely (consider Ansible Vault)

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple site configurations needs careful translation to Ansible
  - Solution: Use Ansible loops with templates to generate site configurations

- **SSL Certificate Generation**: Self-signed certificate generation logic needs to be preserved
  - Solution: Use Ansible's `openssl_*` modules with proper conditionals

- **Security Hardening**: Multiple security layers need coordinated configuration
  - Solution: Create dedicated security role with separate tasks for each component

- **Service Dependencies**: Ensure proper ordering of service installation and configuration
  - Solution: Use Ansible's handlers and meta dependencies between roles

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add SSL certificate management
   - Add multi-site configuration
   - Add security hardening

2. **cache** (Priority 2)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper service management

3. **fastapi-tutorial** (Priority 3)
   - Set up PostgreSQL database
   - Configure Python environment and application deployment
   - Set up systemd service

### Assumptions

1. The target environment will continue to support Ubuntu 18.04+ or CentOS 7+ as specified in the cookbook metadata
2. The Vagrant development environment will be maintained for testing
3. Self-signed certificates are acceptable for development/testing (production would likely use proper certificates)
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain accessible
5. The Redis password and PostgreSQL credentials in the Chef recipes are development values and will be replaced with secure values in production
6. The current security configurations (fail2ban, UFW, SSH hardening) are appropriate for the target environment
7. The multi-site Nginx configuration pattern will be maintained in the Ansible version