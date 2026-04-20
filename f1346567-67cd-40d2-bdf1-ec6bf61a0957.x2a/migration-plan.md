# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three primary cookbooks (nginx-multisite, cache, and fastapi-tutorial) along with their dependencies. The environment appears to be designed for a Fedora-based system with multiple web services, security hardening, and caching layers.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium to High
- Multiple interconnected services
- Security configurations that require careful migration
- External dependencies on Chef Supermarket cookbooks

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and proper SSL configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, fail2ban integration, UFW firewall configuration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4)
- `solo.json`: Defines the run list and configuration parameters for Chef Solo
- `solo.rb`: Configures Chef Solo paths and logging
- `Vagrantfile`: Defines a Fedora 42 VM for development/testing with port forwarding and networking
- `vagrant-provision.sh`: Bash script to provision the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora (based on Vagrantfile specifying "generic/fedora42")
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or local development

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or DavidWittman.redis

### Security Considerations

- **SSL Certificate Management**: 
  - Chef cookbook generates self-signed certificates
  - Migration approach: Use Ansible's `openssl_*` modules or community.crypto collection

- **Firewall Configuration**: 
  - Chef cookbook configures UFW with specific rules
  - Migration approach: Use Ansible's `ufw` module to replicate rules

- **fail2ban Integration**: 
  - Chef cookbook configures fail2ban for intrusion prevention
  - Migration approach: Use Ansible Galaxy role `geerlingguy.security` or create custom fail2ban tasks

- **Vault/secrets management**:
  - Redis password hardcoded in recipe: "redis_secure_password_123"
  - PostgreSQL credentials hardcoded in recipe: "fastapi:fastapi_password"
  - Migration approach: Use Ansible Vault for all credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The Chef cookbook dynamically creates multiple virtual hosts with SSL
  - Mitigation: Create Ansible templates with Jinja2 loops to replicate the dynamic site creation

- **Service Orchestration**: 
  - Description: Interdependent services (Nginx, PostgreSQL, Redis, FastAPI app)
  - Mitigation: Use Ansible handlers and proper dependency ordering

- **SSL Certificate Generation**: 
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's crypto modules to generate certificates or integrate with Let's Encrypt

- **Redis Configuration Hack**: 
  - Description: The Chef cookbook includes a ruby_block to modify Redis config
  - Mitigation: Create proper Redis configuration template in Ansible

### Migration Order

1. **cache cookbook** (low risk, foundational services)
   - Implement Memcached configuration
   - Implement Redis configuration with authentication

2. **nginx-multisite cookbook** (moderate complexity)
   - Implement base Nginx configuration
   - Implement SSL certificate generation
   - Implement security configurations (fail2ban, UFW)
   - Implement virtual host configuration

3. **fastapi-tutorial cookbook** (high complexity, dependencies)
   - Implement PostgreSQL configuration
   - Implement Python environment setup
   - Implement application deployment
   - Implement systemd service configuration

### Assumptions

1. The target environment will continue to be Fedora-based systems
2. Self-signed certificates are acceptable for the migrated solution
3. The same security hardening requirements will apply
4. The FastAPI application repository will remain available at the specified URL
5. The directory structure for web content will remain the same
6. No changes to the application architecture are required
7. The Redis and PostgreSQL passwords can be replaced with Ansible Vault secured values
8. The Vagrant development environment will be replaced with an equivalent Ansible-based setup