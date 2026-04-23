# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application with PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- Total: 5-6 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- Multiple external dependencies need to be addressed
- Security configurations require careful migration
- Secrets management needs improvement in the Ansible implementation

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

- `Berksfile`: Dependency management for Chef cookbooks, lists both local and external cookbook dependencies
  - Migration consideration: Replace with Ansible Galaxy requirements.yml
  
- `Vagrantfile`: Defines development VM using Fedora 42, configures networking and provisioning
  - Migration consideration: Update to use Ansible provisioner instead of Chef

- `solo.json`: Chef node attributes and run list configuration
  - Migration consideration: Convert to Ansible group_vars or host_vars

- `solo.rb`: Chef configuration file
  - Migration consideration: Replace with ansible.cfg

- `vagrant-provision.sh`: Shell script for installing Chef and running cookbooks
  - Migration consideration: Replace with Ansible provisioning commands

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or custom role
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy or custom role
- **redisio (~> 7.2.4)**: Replace with Ansible redis role from Galaxy or custom role

### Security Considerations

- **SSL Certificate Management**: 
  - Current implementation generates self-signed certificates
  - Migration approach: Use Ansible's openssl_* modules for certificate generation or integrate with Let's Encrypt via certbot

- **Firewall Configuration**: 
  - Current implementation uses UFW
  - Migration approach: Use Ansible's ufw module to maintain the same configuration

- **Fail2ban Integration**: 
  - Current implementation configures fail2ban for intrusion prevention
  - Migration approach: Create an Ansible role for fail2ban configuration

- **SSH Hardening**: 
  - Current implementation disables root login and password authentication
  - Migration approach: Use Ansible's lineinfile module or dedicated ssh hardening role

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe
  - PostgreSQL credentials are hardcoded in the recipe
  - Migration approach: Use Ansible Vault for storing sensitive information

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation dynamically generates Nginx site configurations based on node attributes
  - Mitigation strategy: Use Ansible templates with similar logic, leveraging host_vars or group_vars for site definitions

- **SSL Certificate Generation**: 
  - Description: Self-signed certificates are generated for each site
  - Mitigation strategy: Use Ansible's openssl_* modules with similar logic or integrate with Let's Encrypt

- **Database User and Schema Creation**: 
  - Description: PostgreSQL database and user are created using shell commands
  - Mitigation strategy: Use Ansible's postgresql_* modules for more idempotent database management

- **Python Application Deployment**: 
  - Description: FastAPI application is deployed from Git with virtual environment setup
  - Mitigation strategy: Create an Ansible role that handles Python application deployment with similar steps

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security configurations that should be established first

2. **cache** (Priority 2)
   - Supporting services that the application may depend on
   - Moderate complexity with external dependencies

3. **fastapi-tutorial** (Priority 3)
   - Application layer that depends on both web server and database
   - Contains database setup that should come after infrastructure components

### Assumptions

1. The target environment will continue to be Fedora 42 or a compatible Linux distribution
2. The same network configuration will be maintained in the migrated environment
3. Self-signed certificates are acceptable for the migrated solution (production would likely require proper certificates)
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current security configurations (fail2ban, UFW, SSH hardening) are appropriate for the target environment
6. Redis and PostgreSQL passwords in the current implementation are development/example passwords and will be replaced with proper secrets management
7. The current directory structure in the target environment (/opt/fastapi-tutorial, /var/www/sites) will be maintained