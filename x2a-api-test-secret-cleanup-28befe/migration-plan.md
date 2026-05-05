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
- The codebase is well-structured with clear separation of concerns
- External dependencies on community cookbooks will need Ansible equivalents
- Security configurations are present and will need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and custom configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, dependency on community cookbooks

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
  - Migration consideration: Replace with Ansible Galaxy requirements.yml
  
- `solo.json`: Chef node attributes and run list configuration
  - Migration consideration: Convert to Ansible group_vars or host_vars

- `solo.rb`: Chef configuration file
  - Migration consideration: Replace with ansible.cfg

- `Vagrantfile`: Defines the development VM for testing
  - Migration consideration: Update to use Ansible provisioner instead of Chef

- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
  - Migration consideration: Replace with Ansible playbook

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` module or community.general collection
- **memcached (~> 6.0)**: Replace with Ansible's `memcached` module or community.general collection
- **redisio (~> 7.2.4)**: Replace with Ansible's `redis` module or community.general collection
- **Python dependencies**: Use Ansible's `pip` module to manage Python packages and virtual environments

### Security Considerations

- **SSL Certificate Management**: 
  - Current implementation generates self-signed certificates
  - Migration approach: Use Ansible's `openssl_*` modules for certificate generation or community.crypto collection

- **Firewall Configuration**: 
  - Current implementation uses UFW
  - Migration approach: Use Ansible's `ufw` module or `firewalld` module depending on target OS

- **Fail2ban Configuration**: 
  - Current implementation installs and configures fail2ban
  - Migration approach: Use Ansible's `template` module to configure fail2ban

- **SSH Hardening**: 
  - Current implementation disables root login and password authentication
  - Migration approach: Use Ansible's `lineinfile` module or community.general.ini_file module

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL password is hardcoded in the recipe (`fastapi_password`)
  - Migration approach: Use Ansible Vault to secure these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Maintaining the dynamic generation of multiple virtual hosts
  - Mitigation: Use Ansible's with_items/loop constructs with templates

- **SSL Certificate Generation**: 
  - Challenge: Ensuring proper permissions and security for SSL certificates
  - Mitigation: Use Ansible's file module with appropriate permissions and owner/group settings

- **Database Initialization**: 
  - Challenge: Ensuring idempotent database creation and user setup
  - Mitigation: Use Ansible's postgresql_* modules with appropriate when conditions

- **Service Dependencies**: 
  - Challenge: Maintaining proper service startup order
  - Mitigation: Use Ansible's handlers and meta dependencies between roles

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security configurations that should be established first

2. **cache** (Priority 2)
   - Supporting service with external dependencies
   - Moderate complexity due to Redis configuration requirements

3. **fastapi-tutorial** (Priority 3)
   - Application layer that depends on both web server and database
   - Most complex due to application deployment, database setup, and service configuration

### Assumptions

1. The target environment will continue to be Fedora-based systems (specifically Fedora 42 as indicated in the Vagrantfile)
2. The self-signed SSL certificates approach is acceptable for the migrated solution
3. The current security configurations (fail2ban, ufw, SSH hardening) are still required
4. The FastAPI application repository URL and structure will remain the same
5. The PostgreSQL database name, user, and schema requirements will remain unchanged
6. The Redis password and configuration requirements will remain the same
7. The Vagrant development environment will continue to be used for testing
8. No additional monitoring or logging requirements beyond what's currently implemented