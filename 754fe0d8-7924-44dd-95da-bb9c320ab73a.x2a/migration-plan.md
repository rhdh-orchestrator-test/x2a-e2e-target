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
- The codebase is well-structured with clear separation of concerns
- No custom resources or complex Chef-specific patterns
- Standard infrastructure components (Nginx, Redis, Memcached, PostgreSQL)
- Security configurations that need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
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
    - Key Features: Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks. Lists both local and external cookbook dependencies.
- `solo.json`: Chef configuration data including the run list and node attributes for Nginx sites and security settings.
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings.
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef.
- `Vagrantfile`: Vagrant configuration for development environment using Fedora 42.

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) based on cookbook metadata, but the Vagrantfile uses Fedora 42.
- **Virtual Machine Technology**: Vagrant with libvirt provider (based on Vagrantfile configuration).
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.nginx collection
- **memcached (~> 6.0)**: Replace with Ansible memcached role or community.general.memcached module
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role or community.redis collection

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration approach: Use Ansible's openssl_* modules or community.crypto collection

- **Firewall Configuration**: 
  - UFW firewall is configured with specific rules
  - Migration approach: Use Ansible's ufw module or community.general.ufw module

- **Fail2ban Integration**: 
  - Fail2ban is configured for intrusion prevention
  - Migration approach: Use Ansible's template module with fail2ban configuration templates

- **SSH Hardening**: 
  - Root login and password authentication can be disabled
  - Migration approach: Use Ansible's lineinfile or template module for sshd_config

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe ('redis_secure_password_123')
  - PostgreSQL credentials are hardcoded in the FastAPI recipe
  - Migration approach: Use Ansible Vault for storing sensitive credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation dynamically creates Nginx site configurations based on node attributes
  - Mitigation: Use Ansible loops with templates to achieve the same dynamic configuration

- **SSL Certificate Generation**: 
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's openssl_* modules to generate certificates or integrate with Let's Encrypt

- **Service Orchestration**: 
  - Description: Services have dependencies (e.g., FastAPI depends on PostgreSQL)
  - Mitigation: Use Ansible handlers and proper task ordering to ensure dependencies are met

- **Idempotency**: 
  - Description: Some Chef resources use not_if guards to ensure idempotency
  - Mitigation: Ensure Ansible tasks are idempotent using appropriate state parameters and conditionals

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security configurations that should be established first

2. **cache** (Priority 2)
   - Supporting services (Redis, Memcached) that may be required by applications
   - Moderate complexity with external dependencies

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on the infrastructure being in place
   - Involves database setup, application code deployment, and service configuration

### Assumptions

1. The target environment will continue to be Vagrant-based for development/testing
2. Self-signed certificates are acceptable (no requirement for Let's Encrypt or commercial certificates)
3. The same security hardening measures will be maintained in the Ansible implementation
4. The FastAPI application source will continue to be pulled from the same Git repository
5. PostgreSQL and Python versions will remain compatible with the application requirements
6. The Ansible implementation will target the same supported operating systems (Ubuntu 18.04+ and CentOS 7+)
7. No changes to the application architecture or deployment model are required
8. Redis and Memcached configurations will maintain the same performance characteristics
9. No high availability or clustering requirements exist for the services
10. The migration will be a direct translation of functionality rather than a redesign