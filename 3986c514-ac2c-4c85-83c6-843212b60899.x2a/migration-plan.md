# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-service environment consisting of web servers (nginx), caching services (Redis and Memcached), and a FastAPI application with PostgreSQL database. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- No custom resources or complex Chef-specific patterns
- Standard infrastructure components with well-established Ansible modules

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures nginx with multiple SSL-enabled subdomains, security hardening, and site configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall), sysctl security settings

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

- `Berksfile`: Dependency management for Chef cookbooks. Lists both local and external dependencies including nginx, memcached, and redisio.
- `solo.json`: Chef solo configuration file defining the run list and node attributes.
- `solo.rb`: Chef solo configuration settings.
- `Vagrantfile`: Vagrant configuration for local development/testing.
- `vagrant-provision.sh`: Shell script for provisioning Vagrant environments.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04 or later / CentOS 7 or later (both supported in cookbooks)
- **Virtual Machine Technology**: Vagrant (based on Vagrantfile presence)
- **Cloud Platform**: Not specified, appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` module and templates
- **memcached (~> 6.0)**: Replace with Ansible's `memcached` module
- **redisio (~> 7.2.4)**: Replace with Ansible's `community.general.redis` module and templates

### Security Considerations

- **SSL/TLS Management**: 
  - Self-signed certificates are generated for development
  - Migration should maintain or improve certificate management
  - Consider integrating with Ansible Vault for key storage

- **Firewall Configuration**: 
  - UFW firewall rules need to be migrated to Ansible's `ufw` module
  - Maintain existing security posture (SSH, HTTP, HTTPS ports)

- **SSH Hardening**:
  - Disable root login
  - Disable password authentication
  - Maintain these security settings in Ansible

- **Fail2ban Configuration**:
  - Migrate fail2ban configuration to Ansible

- **Vault/secrets management**:
  - Redis password in cache cookbook (`redis_secure_password_123`)
  - PostgreSQL database credentials in fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - The dynamic generation of multiple site configurations will need careful translation to Ansible templates
  - Solution: Use Ansible's template module with similar variable structure

- **SSL Certificate Management**: 
  - Self-signed certificate generation logic needs to be replicated
  - Solution: Use Ansible's `openssl_*` modules

- **PostgreSQL User/Database Creation**: 
  - The current implementation uses direct psql commands
  - Solution: Use Ansible's `postgresql_*` modules for more idiomatic management

- **Redis Configuration Patching**: 
  - The Chef cookbook includes a hack to fix Redis configuration
  - Solution: Create proper Redis configuration template in Ansible

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic nginx installation and configuration
   - Then add SSL and security features
   - Finally, implement multi-site configuration

2. **cache** (Priority 2)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper service management

3. **fastapi-tutorial** (Priority 3)
   - Set up PostgreSQL database
   - Deploy Python application
   - Configure systemd service

### Assumptions

1. The target environment will continue to support Ubuntu 18.04+ or CentOS 7+
2. The self-signed SSL certificates are for development only; production would use proper certificates
3. The current security settings (firewall, SSH hardening) are appropriate for the target environment
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current Redis and Memcached configurations are sufficient for application needs
6. No custom Chef handlers or complex Chef-specific patterns are in use
7. The migration will maintain the same level of idempotence as the current Chef implementation
8. The Vagrant setup is primarily for development/testing and may not need to be migrated if alternative testing approaches are used