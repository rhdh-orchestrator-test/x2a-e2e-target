# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
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
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and fail2ban/ufw configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, firewall configuration

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis authentication, Memcached configuration, service management

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks, lists both local and external dependencies
  - Migration consideration: Replace with Ansible Galaxy requirements.yml
- `solo.json`: Chef node attributes and run list configuration
  - Migration consideration: Convert to Ansible group_vars or host_vars
- `solo.rb`: Chef configuration file
  - Migration consideration: Replace with ansible.cfg
- `Vagrantfile`: Defines development VM for testing
  - Migration consideration: Update to use Ansible provisioner instead of Chef
- `vagrant-provision.sh`: Shell script for provisioning Vagrant VM with Chef
  - Migration consideration: Replace with Ansible provisioning in Vagrantfile

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Libvirt (from Vagrantfile)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package installation

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each virtual host
  - Migration approach: Use Ansible's openssl_* modules for certificate generation

- **Firewall Configuration**: 
  - UFW is configured with specific rules
  - Migration approach: Use Ansible's ufw module or firewalld module depending on target OS

- **Fail2ban Integration**: 
  - Fail2ban is configured for intrusion prevention
  - Migration approach: Use Ansible's template module for fail2ban configuration

- **SSH Hardening**: 
  - Root login disabled, password authentication disabled
  - Migration approach: Use Ansible's lineinfile or template module for SSH configuration

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (redis_secure_password_123)
  - PostgreSQL password is hardcoded in the recipe (fastapi_password)
  - Migration approach: Use Ansible Vault for storing sensitive credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current setup dynamically generates Nginx site configurations based on node attributes
  - Mitigation strategy: Use Ansible's template module with loops to generate site configurations

- **Service Dependencies**: 
  - Description: The FastAPI application depends on PostgreSQL being configured first
  - Mitigation strategy: Use Ansible handlers and proper task ordering to ensure dependencies are met

- **SSL Certificate Generation**: 
  - Description: Self-signed certificates are generated for each virtual host
  - Mitigation strategy: Use Ansible's openssl_* modules with proper idempotency checks

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Relatively self-contained with clear configuration patterns

2. **cache** (Priority 2)
   - Depends on external cookbooks (memcached, redisio)
   - Moderate complexity with Redis authentication configuration

3. **fastapi-tutorial** (Priority 3)
   - Depends on PostgreSQL and web server configuration
   - Most complex with application deployment, database setup, and service configuration

### Assumptions

1. The target environment will continue to be Fedora 42 or a compatible Linux distribution
2. Self-signed certificates are acceptable for the migrated solution (not using Let's Encrypt or other CA)
3. The same security hardening measures should be applied in the Ansible solution
4. The FastAPI application source will continue to be available at the specified Git repository
5. The current Redis and PostgreSQL passwords are not production values and can be replaced
6. No custom Chef handlers or complex Chef-specific patterns are in use that would require special handling
7. The Vagrant development environment should be preserved with equivalent functionality
8. No external monitoring or logging systems integration is required beyond what's in the current code