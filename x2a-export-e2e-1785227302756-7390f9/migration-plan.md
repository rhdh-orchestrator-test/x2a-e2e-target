# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-component application stack consisting of Nginx web servers with multiple sites, caching services (Redis and Memcached), and a FastAPI Python application with PostgreSQL database. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- No custom resources or complex Chef-specific patterns
- Standard infrastructure components (web server, database, caching)
- Security configurations that need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate management, security hardening with fail2ban and UFW firewall

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints.
- `solo.json`: Chef configuration file containing the run list and node attributes. Defines the Nginx sites, SSL paths, and security settings.
- `solo.rb`: Chef configuration file for Chef Solo execution.
- `Vagrantfile`: Defines the development environment using Vagrant.
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04 or newer / CentOS 7 or newer (both supported in cookbooks)
- **Virtual Machine Technology**: VirtualBox (inferred from Vagrant usage)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` module and templates
- **memcached (~> 6.0)**: Replace with Ansible's `apt`/`yum` modules and templates for configuration
- **redisio (~> 7.2.4)**: Replace with Ansible's `apt`/`yum` modules and templates for Redis configuration

### Security Considerations

- **SSL Certificate Management**: 
  - Current approach uses self-signed certificates generated with OpenSSL
  - Migration approach: Use Ansible's `openssl_*` modules for certificate generation
  - Consider integrating with Ansible Vault for secure key storage

- **Firewall Configuration**: 
  - Current approach uses UFW with specific rules
  - Migration approach: Use Ansible's `ufw` module with equivalent rules

- **Fail2ban Configuration**: 
  - Current approach configures fail2ban with custom jail settings
  - Migration approach: Use Ansible templates to configure fail2ban

- **SSH Hardening**: 
  - Current approach disables root login and password authentication
  - Migration approach: Use Ansible's `lineinfile` or templates to configure SSH

- **Vault/secrets management**:
  - Redis password in cache cookbook: Use Ansible Vault to store this secret
  - PostgreSQL credentials in fastapi-tutorial cookbook: Use Ansible Vault to store database credentials
  - Count: 2 hardcoded credentials detected (Redis password, PostgreSQL password)

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Preserving the dynamic site generation based on node attributes
  - Mitigation: Use Ansible's template module with loops to generate site configurations

- **Service Dependencies**: 
  - Challenge: Ensuring proper service startup order (PostgreSQL before FastAPI, etc.)
  - Mitigation: Use Ansible's handlers and meta dependencies to manage service ordering

- **SSL Certificate Management**: 
  - Challenge: Securely managing SSL certificates and private keys
  - Mitigation: Use Ansible Vault for sensitive data and proper file permissions

- **Idempotent Database Setup**: 
  - Challenge: Ensuring PostgreSQL user and database creation is idempotent
  - Mitigation: Use Ansible's PostgreSQL modules with proper conditionals

### Migration Order

1. **cache** (Priority 1 - Low complexity)
   - Simple configuration of Memcached and Redis services
   - Few dependencies on other components

2. **nginx-multisite** (Priority 2 - Medium complexity)
   - Core web server configuration with multiple sites
   - Security hardening components

3. **fastapi-tutorial** (Priority 3 - Higher complexity)
   - Application deployment with database dependencies
   - Requires proper service orchestration

### Assumptions

1. The target environment will continue to be Ubuntu/CentOS based systems
2. Self-signed certificates are acceptable for development (production may require proper CA-signed certificates)
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
4. The current security settings (disabled root SSH, password authentication, etc.) should be preserved
5. The current multi-site configuration pattern should be maintained
6. Redis and Memcached will continue to be used as caching solutions
7. PostgreSQL will continue to be the database for the FastAPI application
8. The Vagrant development environment will be replaced with an equivalent Ansible-based setup