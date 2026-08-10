# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- No custom resources or complex Chef-specific patterns
- Standard infrastructure components (web server, caching, application deployment)

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
    - Key Features: Python virtual environment, Git repository deployment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef node configuration with run list and attribute overrides
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration for development/testing environment using Fedora 42

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development/testing

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)

### Security Considerations

- **SSL Certificate Management**: 
  - Current implementation generates self-signed certificates
  - Migration approach: Use Ansible's openssl_* modules or community.crypto collection

- **Firewall Configuration**: 
  - Current implementation uses UFW
  - Migration approach: Use Ansible's ufw module or firewalld for Fedora

- **SSH Hardening**:
  - Current implementation disables root login and password authentication
  - Migration approach: Use Ansible's lineinfile module or dedicated ssh hardening role

- **Fail2ban Configuration**:
  - Current implementation installs and configures fail2ban
  - Migration approach: Use Ansible's template module or dedicated fail2ban role

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe
  - PostgreSQL credentials are hardcoded in the recipe
  - Migration approach: Use Ansible Vault for storing sensitive information

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation dynamically creates multiple virtual hosts based on node attributes
  - Mitigation: Use Ansible loops with templates to achieve similar functionality

- **SSL Certificate Generation**:
  - Description: Self-signed certificates are generated with OpenSSL commands
  - Mitigation: Use Ansible's openssl_* modules from community.crypto collection

- **PostgreSQL User/Database Creation**:
  - Description: Uses shell commands with sudo for database operations
  - Mitigation: Use Ansible's postgresql_* modules for idempotent database management

- **Service Dependencies**:
  - Description: Ensuring proper service startup order (e.g., PostgreSQL before FastAPI)
  - Mitigation: Use Ansible handlers and meta dependencies between roles

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Relatively self-contained with clear boundaries

2. **cache** (Priority 2)
   - Independent service that can be migrated separately
   - Depends on external cookbooks that need Ansible equivalents

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on PostgreSQL
   - More complex with database setup, git operations, and service configuration

### Assumptions

1. The target environment will continue to be Fedora-based systems
2. Self-signed certificates are acceptable for development/testing
3. The same network configuration (ports, IPs) will be maintained
4. No changes to the application code or database schema are required
5. The Vagrant development environment will be maintained
6. No CI/CD pipeline integration is currently implemented
7. No monitoring or logging solutions are currently implemented
8. No backup/restore procedures are currently implemented
9. The current security measures (fail2ban, ufw, SSH hardening) are sufficient
10. No high availability or clustering is required