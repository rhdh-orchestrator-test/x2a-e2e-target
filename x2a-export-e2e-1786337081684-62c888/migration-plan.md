# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- No custom resources or complex Chef-specific patterns
- Standard package installation and configuration patterns that map well to Ansible

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
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (nginx, memcached, redisio) - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Contains node attributes and run list - will be replaced by Ansible inventory variables
- `solo.rb`: Chef configuration file - no direct Ansible equivalent needed
- `Vagrantfile`: VM configuration for testing - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisioning script for Vagrant - will be replaced by Ansible playbook

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible community.nginx collection or direct package installation
- **memcached (~> 6.0)**: Replace with Ansible community.general.memcached module
- **redisio (~> 7.2.4)**: Replace with Ansible community.redis collection or direct package installation

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated in the nginx-multisite cookbook
  - Migration approach: Use Ansible community.crypto collection for certificate generation

- **Firewall Configuration**: 
  - UFW is configured in the security.rb recipe
  - Migration approach: Use Ansible's ansible.posix.ufw module

- **Fail2ban Configuration**: 
  - Configured in security.rb recipe
  - Migration approach: Use Ansible's community.general.fail2ban module

- **SSH Hardening**: 
  - Root login and password authentication disabled in security.rb
  - Migration approach: Use Ansible's ansible.posix.sshd module

- **Vault/secrets management**:
  - Redis password is hardcoded in cache/default.rb recipe
  - PostgreSQL credentials hardcoded in fastapi-tutorial/default.rb
  - Count: 2 hardcoded credentials detected
  - Migration approach: Use Ansible Vault for sensitive data

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Chef iterates through node attributes to create multiple virtual hosts
  - Mitigation: Use Ansible with_items/loop to iterate through host definitions

- **Service Dependencies**: 
  - FastAPI application depends on PostgreSQL
  - Mitigation: Use Ansible handlers and meta dependencies to ensure proper ordering

- **Template Conversion**: 
  - Multiple ERB templates need conversion to Jinja2
  - Mitigation: Carefully map ERB syntax to equivalent Jinja2 constructs

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add SSL and security features
   - Finally add site configuration

2. **cache** (Priority 2)
   - Independent service with moderate complexity
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (Priority 3)
   - Application deployment with database dependencies
   - Implement PostgreSQL configuration
   - Implement Python application deployment
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions
2. Self-signed certificates are acceptable for development/testing (production would likely use Let's Encrypt or other CA)
3. The same security hardening measures will be maintained in the Ansible implementation
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current Redis and PostgreSQL passwords are for development only and will be replaced with secure passwords in production
6. No custom Chef handlers or complex Chef-specific patterns are in use that would require special handling
7. The Vagrant testing environment will be maintained for the Ansible implementation