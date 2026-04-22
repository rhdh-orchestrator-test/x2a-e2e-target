# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity:** Medium
- The codebase is well-structured with clear separation of concerns
- External dependencies on community cookbooks will need Ansible equivalents
- Security configurations are present and need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), custom Nginx configuration

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, dependency on community cookbooks

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef node configuration with run list and attribute overrides
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration for development environment using Fedora 42

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be a local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for development
  - Migration should maintain the same level of security or improve it
  - Consider using Ansible's openssl_* modules for certificate management

- **Firewall Configuration**: 
  - UFW is configured in the security.rb recipe
  - Migrate to Ansible's ufw module or firewalld for Fedora

- **Fail2ban Configuration**: 
  - Fail2ban is configured for intrusion prevention
  - Use Ansible's template module to create fail2ban configuration

- **SSH Hardening**: 
  - Root login disabled
  - Password authentication disabled
  - Migrate using Ansible's lineinfile or template modules

- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook
  - Recommend using Ansible Vault for storing sensitive information

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - The current implementation uses templates to generate site configurations
  - Ansible will need to replicate this dynamic site generation
  - Solution: Use Ansible's template module with similar logic

- **SSL Certificate Generation**: 
  - Self-signed certificates are generated for each site
  - Solution: Use Ansible's openssl_* modules to generate certificates

- **Service Dependencies**: 
  - FastAPI application depends on PostgreSQL
  - Solution: Use Ansible's meta dependencies and handlers to ensure proper ordering

- **Redis Configuration Hack**: 
  - The cache cookbook includes a ruby_block to modify Redis configuration
  - Solution: Create a custom template for Redis configuration in Ansible

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component
   - Other services depend on it
   - Start with basic Nginx installation and configuration
   - Add security features
   - Add SSL configuration
   - Add multi-site configuration

2. **cache** (Priority 2)
   - Independent service but used by applications
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (Priority 3)
   - Application layer that depends on infrastructure
   - Implement PostgreSQL database setup
   - Implement Python environment and application deployment
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora-based systems (Fedora 42 as specified in the Vagrantfile)
2. The same network configuration and port mappings will be maintained
3. Self-signed certificates are acceptable for development purposes
4. The FastAPI application repository will remain available at the specified URL
5. The current security configurations are appropriate for the target environment
6. No additional monitoring or logging requirements beyond what's currently implemented
7. The Redis configuration hack is necessary due to compatibility issues with the current version
8. The PostgreSQL database schema is managed by the FastAPI application itself
9. No backup or disaster recovery procedures are currently implemented
10. No high availability or clustering requirements are present