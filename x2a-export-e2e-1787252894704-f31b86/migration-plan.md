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
- Well-structured Chef cookbooks with clear separation of concerns
- Standard infrastructure components (Nginx, Redis, Memcached, PostgreSQL)
- Security configurations that need careful migration
- Hardcoded credentials that should be moved to Ansible Vault

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
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
    - Key Features: Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (nginx, memcached, redisio) - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Contains node attributes and run list - will be converted to Ansible group_vars and inventory
- `solo.rb`: Chef configuration file - not needed in Ansible
- `Vagrantfile`: Defines the development VM - can be adapted for Ansible testing
- `vagrant-provision.sh`: Installs Chef and runs provisioning - will be replaced by Ansible provisioning

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Libvirt (from Vagrantfile)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible community.nginx collection or geerlingguy.nginx role
- **memcached (~> 6.0)**: Replace with geerlingguy.memcached role
- **redisio (~> 7.2.4)**: Replace with geerlingguy.redis role or community.redis collection

### Security Considerations

- **SSL Certificate Management**: 
  - Chef cookbook generates self-signed certificates
  - Migration approach: Use Ansible crypto modules (openssl_certificate, openssl_privatekey) or community.crypto collection

- **Firewall Configuration**: 
  - Chef cookbook configures UFW
  - Migration approach: Use Ansible ufw module or firewalld module depending on target OS

- **System Hardening**:
  - Chef cookbook applies sysctl security settings
  - Migration approach: Use ansible.posix.sysctl module

- **Fail2ban Configuration**:
  - Chef cookbook configures fail2ban
  - Migration approach: Create Ansible tasks using template module for fail2ban configuration

- **Vault/secrets management**:
  - Hardcoded Redis password in cache cookbook: `redis_secure_password_123`
  - Hardcoded PostgreSQL password in fastapi-tutorial cookbook: `fastapi_password`
  - Migration approach: Move all credentials to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Dynamically creating multiple virtual hosts with SSL
  - Mitigation: Create Ansible templates with loops similar to the Chef templates

- **Service Dependencies**: 
  - Challenge: Ensuring proper service startup order (PostgreSQL before FastAPI, etc.)
  - Mitigation: Use Ansible handlers and meta dependencies between roles

- **SSL Certificate Generation**: 
  - Challenge: Generating self-signed certificates for development
  - Mitigation: Use Ansible's openssl_* modules with proper idempotency checks

- **Redis Configuration Hack**: 
  - Challenge: The Chef cookbook includes a hack to fix Redis configuration
  - Mitigation: Create a proper Redis configuration template in Ansible without needing post-processing

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security configurations that should be established first

2. **cache** (Priority 2)
   - Moderate complexity with external dependencies
   - Required for application performance but not for basic functionality

3. **fastapi-tutorial** (Priority 3)
   - Depends on both Nginx (for serving) and potentially cache services
   - Most complex with database setup and application deployment

### Assumptions

1. The target environment will continue to be Fedora/RHEL-based systems, though the cookbooks support Ubuntu as well
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or other CA)
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
4. The current security settings (fail2ban, ufw, sysctl) are appropriate for the target environment
5. The hardcoded credentials in the Chef recipes are for development only and will be replaced with secure values in Ansible Vault
6. The Nginx sites configuration (test.cluster.local, ci.cluster.local, status.cluster.local) will remain the same
7. The current VM resources (2GB RAM, 2 CPUs) are sufficient for the application stack