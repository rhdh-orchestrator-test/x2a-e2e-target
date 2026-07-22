# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI Python application with PostgreSQL database. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- Security configurations are comprehensive but straightforward
- Self-signed SSL certificates will need careful handling
- Hardcoded credentials will need to be migrated to Ansible Vault

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled sites, security hardening, fail2ban, and firewall rules
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening, UFW firewall configuration

- **cache**:
    - Description: Configures Memcached and Redis caching services with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password protection, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database, virtual environment, and systemd service
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (nginx, memcached, redisio) - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Contains node configuration and run list - will be replaced by Ansible inventory variables
- `solo.rb`: Chef Solo configuration - not needed in Ansible
- `Vagrantfile`: Development environment configuration - will need updating for Ansible provisioner
- `vagrant-provision.sh`: Provisioning script for Vagrant - will need updating for Ansible

### Target Details

- **Operating System**: Based on the Vagrantfile, the target OS is Fedora 42. The cookbooks also support Ubuntu 18.04+ and CentOS 7+.
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks

### Security Considerations

- **Self-signed SSL certificates**: The current implementation generates self-signed certificates for each site. Ansible can use the `community.crypto.openssl_*` modules to generate certificates.
- **Fail2ban configuration**: Currently configured via templates. Ansible has modules for managing fail2ban.
- **UFW firewall rules**: Currently managed via execute resources. Ansible has the `community.general.ufw` module.
- **SSH hardening**: Currently configured via execute resources. Ansible has modules for managing SSH configuration.
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook
  - These should be migrated to Ansible Vault

### Technical Challenges

- **Multi-site Nginx configuration**: The current implementation uses templates to generate site configurations. Ansible will need to use templates or the `community.general.nginx_*` modules.
- **Self-signed certificate generation**: The current implementation uses execute resources to generate certificates. Ansible has modules for this, but the logic will need to be preserved.
- **PostgreSQL database setup**: The current implementation uses execute resources to create databases and users. Ansible has modules for PostgreSQL management.
- **Service management**: The current implementation uses service resources. Ansible has modules for service management.

### Migration Order

1. **nginx-multisite** (Priority 1): This is the foundation for the web infrastructure and should be migrated first.
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Add site configuration
   - Add security hardening

2. **cache** (Priority 2): This provides caching services for the application.
   - Migrate Memcached configuration
   - Migrate Redis configuration with authentication

3. **fastapi-tutorial** (Priority 3): This deploys the application and depends on the database.
   - Migrate PostgreSQL installation and configuration
   - Migrate application deployment
   - Migrate service configuration

### Assumptions

1. The target environment will continue to be Fedora 42 or similar Linux distributions.
2. Self-signed certificates are acceptable for the migrated solution (not production-ready).
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
4. The current security configurations (fail2ban, UFW, SSH hardening) are sufficient and should be preserved.
5. The current Redis password and PostgreSQL credentials will be migrated to Ansible Vault without changing them.
6. The Vagrant development environment will be preserved but updated to use Ansible provisioning.
7. No changes to the application code or database schema are required.
8. The current directory structure for web content (/var/www/site.cluster.local) will be preserved.
9. The current systemd service configuration for FastAPI will be preserved.
10. The current Nginx configuration templates will be migrated as-is to Ansible templates.