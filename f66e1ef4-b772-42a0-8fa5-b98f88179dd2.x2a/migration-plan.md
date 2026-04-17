# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three primary Chef cookbooks to Ansible roles and playbooks, addressing security configurations, and ensuring proper handling of secrets.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- Well-structured Chef cookbooks with clear separation of concerns
- Standard infrastructure components (Nginx, Redis, Memcached, PostgreSQL)
- Some security configurations that need careful migration
- Hardcoded secrets that need to be moved to Ansible Vault

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
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
    - Key Features: Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including nginx, ssl_certificate, memcached, and redisio. Will be replaced by Ansible Galaxy requirements.
- `Policyfile.rb`: Defines the run list and cookbook dependencies. Will be replaced by Ansible playbook structure.
- `solo.rb`: Chef Solo configuration file. Will be replaced by Ansible configuration.
- `solo.json`: Defines node attributes and run list. Will be replaced by Ansible inventory and variable files.
- `Vagrantfile`: Defines the development VM. Can be adapted to use Ansible provisioner instead of Chef.
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM. Will need to be updated for Ansible.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or create a custom role
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role from Galaxy
- **ssl_certificate (~> 2.1)**: Replace with Ansible certificate management tasks or community roles

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW. Migrate to Ansible's `ufw` module.
- **fail2ban Setup**: Migrate fail2ban configuration to Ansible tasks using the `template` module.
- **SSH Hardening**: Migrate SSH security configurations (disable root login, password authentication) to Ansible tasks.
- **SSL Certificate Management**: Migrate self-signed certificate generation to Ansible using the `openssl_*` modules.
- **Vault/secrets management**:
  - Redis password hardcoded in `cache/recipes/default.rb` ("redis_secure_password_123")
  - PostgreSQL credentials hardcoded in `fastapi-tutorial/recipes/default.rb` (user: "fastapi", password: "fastapi_password")
  - Environment variables in `.env` file for FastAPI application
  - All credentials should be migrated to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple site configurations needs to be carefully migrated to Ansible's templating system.
- **SSL Certificate Management**: Self-signed certificate generation and management needs to be properly implemented in Ansible.
- **Service Dependencies**: Ensuring proper ordering of service installation and configuration, particularly for the FastAPI application which depends on PostgreSQL.
- **Idempotency**: Ensuring all Ansible tasks are idempotent, particularly the database creation tasks in the FastAPI role.

### Migration Order

1. **cache role** (low complexity): Simple configuration of Memcached and Redis services
2. **nginx-multisite role** (medium complexity): Nginx configuration with SSL and security hardening
3. **fastapi-tutorial role** (high complexity): Application deployment with database dependencies

### Assumptions

1. The target environment will continue to be Fedora/CentOS/Ubuntu based on the current cookbook support.
2. The self-signed certificates approach will be maintained rather than implementing Let's Encrypt or other certificate authorities.
3. The current network configuration and port mappings will remain the same.
4. The repository structure will be reorganized to follow Ansible best practices (roles, playbooks, inventory).
5. Hardcoded credentials will be replaced with Ansible Vault variables.
6. The Vagrant development environment will be maintained but updated to use Ansible provisioning.
7. No changes to the actual application code or deployment architecture are required.
8. The current security configurations (fail2ban, UFW, SSH hardening) will be maintained in the Ansible implementation.