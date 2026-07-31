# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site web application environment with FastAPI backend, Nginx web server, and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured and modular
- No custom resources or complex Chef-specific patterns
- Clear separation of concerns between cookbooks
- Standard configuration patterns for common services

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
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

- `Berksfile`: Defines cookbook dependencies - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Contains node attributes and run list - will be replaced by Ansible inventory variables
- `solo.rb`: Chef Solo configuration - not needed in Ansible
- `vagrant-provision.sh`: Provisioning script for Vagrant - will need to be updated for Ansible
- `Vagrantfile`: Vagrant configuration - will need updates for Ansible provisioner

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata support declarations)
- **Virtual Machine Technology**: VirtualBox (inferred from Vagrant usage)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (v12.0+)**: Replace with Ansible community.general.nginx_* modules or geerlingguy.nginx role
- **memcached (v6.0+)**: Replace with geerlingguy.memcached role
- **redisio (v7.2.4+)**: Replace with geerlingguy.redis role or community.general.redis_* modules

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration should use ansible.builtin.openssl_* modules for certificate generation
  - Consider integrating with Ansible Vault for private key storage

- **Firewall Configuration**: 
  - UFW configuration should be migrated to ansible.posix.ufw module
  - Ensure all required ports are properly allowed (22, 80, 443)

- **SSH Hardening**:
  - Root login disabled
  - Password authentication disabled
  - Use ansible.posix.sshd_config module for SSH configuration

- **Fail2ban Integration**:
  - Migrate fail2ban configuration to use community.general.fail2ban module

- **Vault/secrets management**:
  - Redis password in cache cookbook should be stored in Ansible Vault
  - PostgreSQL credentials in fastapi-tutorial cookbook should be stored in Ansible Vault
  - Total credentials detected: 2 (Redis password, PostgreSQL user/password)

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Dynamically creating multiple virtual hosts with SSL
  - Solution: Use Ansible with_items/loop to iterate through site configurations

- **Service Orchestration**: 
  - Challenge: Ensuring proper service restart only when needed
  - Solution: Use Ansible handlers and notify mechanism to replace Chef notifications

- **Template Migration**: 
  - Challenge: Converting ERB templates to Jinja2
  - Solution: Systematic conversion of template syntax while preserving logic

- **PostgreSQL Configuration**: 
  - Challenge: Ensuring idempotent database and user creation
  - Solution: Use community.postgresql modules with proper when conditions

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Then add SSL and security features
   - Finally implement multi-site configuration

2. **cache** (Priority 2)
   - Relatively simple configuration with external dependencies
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (Priority 3)
   - Application-specific configuration that depends on other services
   - Implement PostgreSQL database setup
   - Configure Python environment and application deployment
   - Set up systemd service

### Assumptions

1. The target environment will continue to be Ubuntu 18.04+ or CentOS 7+ systems
2. Self-signed certificates are acceptable for development/testing (production would likely use Let's Encrypt or other CA)
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain accessible
4. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate for the target environment
5. The Vagrant development workflow will be maintained after migration
6. No custom Chef resources or libraries are being used that would require special handling
7. The current directory structure in /opt and /var will be maintained in the Ansible implementation