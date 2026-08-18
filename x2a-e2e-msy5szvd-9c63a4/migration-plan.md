# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- External dependencies are explicitly defined in the Berksfile
- Security configurations are present and need careful migration
- Secrets management needs improvement during migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificates
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies for Chef, including local and external cookbooks. Will be replaced by Ansible Galaxy requirements.yml.
- `solo.json`: Contains Chef node attributes and run list. Will be replaced by Ansible inventory variables.
- `solo.rb`: Chef Solo configuration file. Will be replaced by Ansible configuration.
- `Vagrantfile`: Defines the development VM configuration. Can be adapted for Ansible testing.
- `vagrant-provision.sh`: Shell script to install Chef and run the cookbooks. Will be replaced by Ansible provisioning.

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package installation

### Security Considerations

- **SSL Certificate Management**: 
  - Current approach uses self-signed certificates generated with OpenSSL
  - Migration approach: Use Ansible's openssl_* modules or community.crypto collection

- **Firewall Configuration**: 
  - Current approach uses UFW with specific rules for SSH, HTTP, and HTTPS
  - Migration approach: Use Ansible's ufw module or firewalld module depending on target OS

- **SSH Hardening**: 
  - Current approach modifies sshd_config to disable root login and password authentication
  - Migration approach: Use Ansible's lineinfile module or dedicated ssh hardening role

- **Fail2ban Configuration**: 
  - Current approach installs and configures fail2ban with a custom jail.local file
  - Migration approach: Use Ansible's template module or dedicated fail2ban role

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe: "redis_secure_password_123"
  - PostgreSQL credentials are hardcoded in the recipe: "fastapi" / "fastapi_password"
  - Migration approach: Use Ansible Vault for storing sensitive information

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Replicating the dynamic generation of multiple virtual hosts with SSL
  - Mitigation: Use Ansible's with_items/loop constructs with templates to generate site configurations

- **Service Orchestration**: 
  - Challenge: Ensuring proper service start order (PostgreSQL before FastAPI application)
  - Mitigation: Use Ansible's handlers and meta dependencies to enforce ordering

- **SSL Certificate Generation**: 
  - Challenge: Replicating the conditional SSL certificate generation logic
  - Mitigation: Use Ansible's stat module to check for existing certificates before generation

- **System Tuning**: 
  - Challenge: Replicating the sysctl security configurations
  - Mitigation: Use Ansible's sysctl module with appropriate settings

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security configurations that should be established first

2. **cache** (Priority 2)
   - Supporting services that the application may depend on
   - Relatively self-contained with clear dependencies

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on the infrastructure being in place
   - Requires database setup and configuration

### Assumptions

1. The target environment will continue to be Fedora-based, though the cookbooks support Ubuntu and CentOS as well.
2. The self-signed SSL certificates approach is acceptable for the migrated solution.
3. The current security configurations (fail2ban, UFW, SSH hardening) are appropriate for the target environment.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The current Redis and PostgreSQL passwords are development/testing passwords and will be replaced with more secure values in production.
6. The Vagrant development environment will continue to be used for testing the Ansible playbooks.
7. No CI/CD pipeline integration is required as part of the migration.
8. The current approach of cloning the FastAPI repository directly is acceptable (as opposed to using application artifacts).