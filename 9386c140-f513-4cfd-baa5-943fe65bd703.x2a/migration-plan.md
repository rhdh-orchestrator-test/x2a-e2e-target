# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with FastAPI application backend and caching services (Redis and Memcached). The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- No custom resources or complex Chef-specific patterns
- Standard infrastructure components (web server, application server, caching)
- Security configurations that need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall)

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database setup
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment, Git repository deployment, PostgreSQL database configuration, systemd service

- **cache**:
    - Description: Caching services configuration (Redis and Memcached)
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks. Lists both local and external cookbook dependencies.
- `solo.json`: Chef configuration data including run list and node attributes.
- `solo.rb`: Chef Solo configuration file defining paths and log settings.
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef.
- `Vagrantfile`: Vagrant configuration for development environment using Fedora 42.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be a local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW firewall. Migration should use Ansible's `ufw` module or `firewalld` module for Fedora.
- **Fail2ban Setup**: The Chef cookbook configures fail2ban. Migration should use Ansible's `template` module for fail2ban configuration.
- **SSH Hardening**: The Chef cookbook disables root login and password authentication. Migration should use Ansible's `lineinfile` or `template` module for SSH configuration.
- **SSL Certificate Management**: The Chef cookbook generates self-signed certificates. Migration should use Ansible's `openssl_*` modules.
- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL password in fastapi-tutorial cookbook: "fastapi_password"
  - These should be moved to Ansible Vault or another secrets management solution

### Technical Challenges

- **Multi-site Configuration**: The nginx-multisite cookbook dynamically creates site configurations based on node attributes. This pattern needs to be replicated in Ansible using loops and templates.
- **SSL Certificate Generation**: The Chef cookbook generates self-signed certificates. This needs to be replicated in Ansible using the `openssl_*` modules.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL. This dependency needs to be managed in Ansible using handlers or the `meta` directive.
- **Redis Configuration Hack**: The cache cookbook includes a Ruby block to modify Redis configuration. This needs to be replicated in Ansible using the `lineinfile` module or templates.

### Migration Order

1. **cache** (Priority 1): Simplest cookbook with standard package installations and minimal configuration.
2. **nginx-multisite** (Priority 2): Core infrastructure component with security configurations.
3. **fastapi-tutorial** (Priority 3): Application deployment with database dependencies.

### Assumptions

1. The target environment will continue to be Fedora-based (the Vagrantfile specifies Fedora 42).
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or another CA).
3. The same directory structure for web content and SSL certificates will be maintained.
4. The FastAPI application source will continue to be pulled from the same Git repository.
5. The PostgreSQL database structure and user permissions will remain the same.
6. The Redis and Memcached configurations will maintain the same settings.
7. The security hardening measures (fail2ban, ufw, SSH configuration) will be maintained.