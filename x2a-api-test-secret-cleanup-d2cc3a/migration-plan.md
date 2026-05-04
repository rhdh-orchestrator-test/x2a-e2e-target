# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has well-structured Chef cookbooks with clear dependencies
- Security configurations are present and need careful migration
- External cookbook dependencies need to be replaced with Ansible Galaxy roles or custom implementations

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, fail2ban integration, UFW firewall configuration

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4)
- `solo.json`: Defines the Chef run list and configuration attributes for nginx sites and security settings
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Defines the Vagrant VM configuration using Fedora 42 with port forwarding and networking

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be a local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role from Galaxy or create a custom role
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role or create a custom role
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` role or create a custom role
- **PostgreSQL**: Replace with Ansible's `geerlingguy.postgresql` role or create a custom role

### Security Considerations

- **SSL Certificate Management**: 
  - The current implementation generates self-signed certificates
  - Migration approach: Use Ansible's `openssl_*` modules or `community.crypto` collection

- **Firewall Configuration (UFW)**:
  - Current implementation uses UFW with specific rules for SSH, HTTP, and HTTPS
  - Migration approach: Use Ansible's `ufw` module to configure the same rules

- **fail2ban Integration**:
  - Current implementation installs and configures fail2ban
  - Migration approach: Use Ansible's `template` module to create fail2ban configuration files

- **SSH Hardening**:
  - Current implementation disables root login and password authentication
  - Migration approach: Use Ansible's `lineinfile` module or `template` module to configure SSH

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL password is hardcoded in the recipe (`fastapi_password`)
  - Migration approach: Use Ansible Vault to store sensitive information

### Technical Challenges

- **Multi-site Nginx Configuration**:
  - Challenge: Replicating the dynamic site configuration from Chef to Ansible
  - Mitigation: Create Ansible templates that iterate through site configurations defined in variables

- **SSL Certificate Generation**:
  - Challenge: Ensuring proper permissions and ownership for SSL certificates and keys
  - Mitigation: Use Ansible's file module with appropriate permissions and the `community.crypto` collection

- **Service Dependencies**:
  - Challenge: Ensuring proper service startup order (PostgreSQL before FastAPI application)
  - Mitigation: Use Ansible's `meta: flush_handlers` and proper `notify` directives

- **Idempotent Database Creation**:
  - Challenge: Ensuring PostgreSQL database creation is idempotent
  - Mitigation: Use Ansible's `postgresql_*` modules with proper `when` conditions

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Includes security configurations that should be established first

2. **cache** (Priority 2)
   - Supporting services that can be configured independently
   - Moderate complexity with Redis authentication

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on both web server and database
   - Higher complexity with Python environment setup and PostgreSQL integration

### Assumptions

1. The target environment will continue to be Fedora-based systems (Fedora 42 as specified in the Vagrantfile)
2. Self-signed SSL certificates are acceptable for the migrated solution
3. The same security hardening measures are required in the Ansible implementation
4. The FastAPI application source will continue to be pulled from the same Git repository
5. The current directory structure for deployed applications will be maintained
6. The Redis and PostgreSQL passwords will be managed securely in the new implementation
7. The Vagrant development environment will be maintained for testing
8. No additional monitoring or logging solutions need to be integrated beyond what's in the current implementation
9. The current nginx site configurations (test.cluster.local, ci.cluster.local, status.cluster.local) will remain the same