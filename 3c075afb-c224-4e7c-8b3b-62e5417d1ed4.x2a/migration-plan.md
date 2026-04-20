# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure for deploying a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application with PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 3 weeks
- Testing and Validation: 2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 7 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- External dependencies are clearly defined in the Berksfile
- Security configurations are comprehensive and will require careful migration
- Secrets management needs improvement in the Ansible implementation

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and configuration management
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl), custom Nginx configurations

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, service management

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (nginx, memcached, redisio) - will be replaced by Ansible Galaxy requirements.yml
- `Vagrantfile`: Defines development VM configuration - can be adapted for Ansible testing with minimal changes
- `solo.json`: Contains Chef node attributes and run list - will be converted to Ansible group_vars or host_vars
- `solo.rb`: Chef configuration file - not needed in Ansible
- `vagrant-provision.sh`: Shell script for provisioning Vagrant VM with Chef - will be replaced by Ansible provisioner in Vagrantfile

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible community.general.nginx_vhost or direct template management
- **memcached (~> 6.0)**: Replace with Ansible community.general.memcached module
- **redisio (~> 7.2.4)**: Replace with Ansible community.redis collection or direct package/service/config management
- **Python 3 and venv**: Use Ansible pip module for Python dependency management
- **PostgreSQL**: Use Ansible community.postgresql collection for database management

### Security Considerations

- **SSL Certificate Management**: 
  - Current implementation generates self-signed certificates
  - Migration approach: Use Ansible community.crypto.openssl_* modules for certificate generation
  - Consider integrating with Ansible Vault for certificate storage

- **Firewall Configuration (UFW)**:
  - Migration approach: Use Ansible community.general.ufw module to manage firewall rules

- **Fail2ban Configuration**:
  - Migration approach: Use Ansible to template fail2ban configuration files and manage the service

- **System Hardening (sysctl)**:
  - Migration approach: Use Ansible posix.sysctl module to manage kernel parameters

- **SSH Hardening**:
  - Migration approach: Use Ansible openssh_config module to manage SSH configuration

- **Vault/secrets management**:
  - Current implementation has hardcoded Redis password in recipe
  - Migration approach: Use Ansible Vault to store sensitive information
  - Credentials detected:
    - Redis password: "redis_secure_password_123" in cache/recipes/default.rb
    - PostgreSQL user/password: "fastapi"/"fastapi_password" in fastapi-tutorial/recipes/default.rb
    - Database connection string in .env file

### Technical Challenges

- **Multi-site Nginx Configuration**:
  - Challenge: Maintaining the dynamic generation of site configurations
  - Mitigation: Use Ansible with_items/loop to iterate through site definitions in variables

- **SSL Certificate Generation**:
  - Challenge: Ensuring certificates are only generated when needed
  - Mitigation: Use Ansible's changed_when and check_mode features to control execution

- **Service Dependencies**:
  - Challenge: Maintaining proper service startup order (PostgreSQL before FastAPI)
  - Mitigation: Use Ansible handlers and meta tasks to enforce dependencies

- **Idempotent Database Creation**:
  - Challenge: Ensuring database operations are idempotent
  - Mitigation: Use Ansible community.postgresql modules with proper when conditions

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Moderate complexity with clear separation of concerns

2. **cache** (Priority 2)
   - Independent service with external dependencies
   - Relatively simple configuration with some security considerations

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on database
   - Most complex due to application deployment, database setup, and service configuration

### Assumptions

1. The target environment will continue to be Fedora-based systems
2. Self-signed certificates are acceptable for the migrated solution
3. The same security hardening requirements will apply to the Ansible implementation
4. The FastAPI application repository will remain available at the specified URL
5. The current Redis and PostgreSQL password policies are acceptable
6. No additional monitoring or logging requirements beyond what's in the current implementation
7. The Vagrant development workflow will be maintained
8. No CI/CD integration is required for the initial migration