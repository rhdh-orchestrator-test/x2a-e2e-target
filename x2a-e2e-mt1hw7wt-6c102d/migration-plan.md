# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services (Redis and Memcached) and a FastAPI application with PostgreSQL. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and files to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- No complex custom resources or libraries
- Standard infrastructure components (web server, caching, application deployment)
- Security configurations that need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificates
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup, security headers, fail2ban integration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4). Will need to be replaced with Ansible Galaxy requirements.
- `solo.json`: Contains node attributes and run list. Will be converted to Ansible group_vars or host_vars.
- `solo.rb`: Chef configuration file. Not needed in Ansible.
- `Vagrantfile`: VM configuration for development/testing. Can be adapted for Ansible with minimal changes.
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef. Will need to be replaced with an Ansible provisioner.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or local development

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` module or community.general collection
- **memcached (~> 6.0)**: Replace with Ansible's `memcached` module or community.general collection
- **redisio (~> 7.2.4)**: Replace with Ansible's `redis` module or community.general collection

### Security Considerations

- **SSL/TLS Configuration**: The nginx-multisite cookbook generates self-signed certificates. Migrate to Ansible's `openssl_*` modules.
- **Security Headers**: Nginx security headers need to be preserved in the Ansible templates.
- **Fail2ban Configuration**: Migrate fail2ban jail configuration to Ansible.
- **UFW Firewall Rules**: Convert UFW rules to Ansible's `ufw` module.
- **SSH Hardening**: Preserve SSH security settings (disable root login, password authentication).
- **Sysctl Security Settings**: Migrate sysctl security configurations.
- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123" (hardcoded)
  - PostgreSQL credentials in fastapi-tutorial cookbook: username "fastapi" with password "fastapi_password" (hardcoded)
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of Nginx site configurations based on node attributes will need to be replicated in Ansible using templates and variables.
- **SSL Certificate Generation**: Self-signed certificate generation logic needs to be migrated to Ansible's `openssl_*` modules.
- **Service Dependencies**: Ensuring proper ordering of service installations and configurations, especially for the FastAPI application which depends on PostgreSQL.
- **Idempotence**: Ensuring all operations remain idempotent, particularly the database user and database creation in the FastAPI cookbook.

### Migration Order

1. **nginx-multisite** (Priority 1): Core infrastructure component that other services depend on
2. **cache** (Priority 2): Supporting services with moderate complexity
3. **fastapi-tutorial** (Priority 3): Application deployment with database dependencies

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions.
2. The Vagrant development environment will be maintained for testing.
3. Self-signed certificates are acceptable for development/testing purposes.
4. No external configuration management system (like Chef Server) is in use - this appears to be a Chef Solo setup.
5. No complex custom resources or libraries are in use that would require special handling.
6. The current security configurations are appropriate and should be maintained in the Ansible implementation.
7. The FastAPI application source will continue to be pulled from the same Git repository.
8. The current directory structure for web content will be maintained.