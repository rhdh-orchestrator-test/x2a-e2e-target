# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure for deploying a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, configuration templates, and security settings.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- **Total: 5-6 weeks**

**Complexity Assessment:** Medium
- Well-structured Chef cookbooks with clear separation of concerns
- Standard infrastructure components (Nginx, Redis, Memcached, PostgreSQL)
- Security configurations that need careful migration
- External cookbook dependencies that need Ansible equivalents

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and fail2ban/ufw firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, firewall rules

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment, Git repository deployment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4)
- `solo.json`: Defines the run list and configuration attributes for Nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Defines a Fedora 42 VM with port forwarding for development/testing
- `vagrant-provision.sh`: Bash script to provision the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or local development

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` module and custom templates
- **memcached (~> 6.0)**: Replace with Ansible's `community.general.memcached` module
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role (e.g., `geerlingguy.redis`)

### Security Considerations

- **SSL Certificate Management**: 
  - Chef cookbook generates self-signed certificates
  - Migration should use Ansible's `openssl_*` modules for certificate generation
  - Consider integrating with Ansible Vault for private key storage

- **Firewall Configuration**:
  - Current implementation uses ufw
  - Migrate to Ansible's `ufw` module or `firewalld` module depending on target OS

- **fail2ban Integration**:
  - Migrate fail2ban configuration templates to Ansible templates
  - Use Ansible's `template` module for configuration files

- **SSH Hardening**:
  - Current implementation disables root login and password authentication
  - Use Ansible's `lineinfile` or templates for SSH configuration

- **Vault/secrets management**:
  - Redis password in plaintext in the cache cookbook
  - PostgreSQL credentials in plaintext in the fastapi-tutorial cookbook
  - Migrate to Ansible Vault for secure credential storage

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Preserving the dynamic site configuration capability
  - Mitigation: Use Ansible's template module with Jinja2 loops to generate site configurations

- **SSL Certificate Generation**:
  - Challenge: Ensuring secure certificate generation and storage
  - Mitigation: Use Ansible's `openssl_*` modules and Ansible Vault for key storage

- **Database Initialization**:
  - Challenge: Ensuring idempotent database and user creation
  - Mitigation: Use Ansible's PostgreSQL modules with appropriate `when` conditions

- **Service Dependencies**:
  - Challenge: Maintaining proper service startup order
  - Mitigation: Use Ansible's `meta: flush_handlers` and proper handler notification

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security configurations that should be established first

2. **cache** (Priority 2)
   - Moderate complexity with external dependencies
   - Required by the application layer

3. **fastapi-tutorial** (Priority 3)
   - Application layer that depends on infrastructure components
   - Involves database setup and application deployment

### Assumptions

1. The target environment will continue to be Fedora-based systems (the current Vagrantfile specifies Fedora 42)
2. Self-signed certificates are acceptable for the migrated solution (production environments might require integration with Let's Encrypt or other certificate authorities)
3. The security requirements will remain the same (fail2ban, ufw, SSH hardening)
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current Redis and PostgreSQL passwords are development passwords and will be replaced with production-grade passwords in the Ansible implementation
6. The Nginx site configurations (test.cluster.local, ci.cluster.local, status.cluster.local) will remain the same
7. The current implementation does not use Chef Vault or encrypted data bags for secrets management