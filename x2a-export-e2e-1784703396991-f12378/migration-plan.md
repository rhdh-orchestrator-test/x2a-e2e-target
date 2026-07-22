# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- No custom resources or complex Chef-specific patterns are used
- Standard package installation and configuration patterns are used throughout

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), custom Nginx configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Configures caching services (Memcached and Redis) with security settings
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (nginx, memcached, redisio) - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Defines the run list and configuration attributes - will be replaced by Ansible inventory variables
- `solo.rb`: Chef configuration file - not needed in Ansible
- `Vagrantfile`: Defines the development VM - can be adapted for Ansible with minimal changes
- `vagrant-provision.sh`: Installs Chef and runs cookbooks - will be replaced with Ansible provisioner

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in Vagrant
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role or direct package management
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` role or direct Redis installation and configuration

### Security Considerations

- **SSL Certificate Management**: Self-signed certificates are generated for each site. In Ansible, use the `openssl_*` modules to generate certificates or integrate with `community.crypto` collection.
- **Firewall Configuration**: UFW is configured with specific rules. Use Ansible's `ufw` module or `firewalld` module depending on target OS.
- **SSH Hardening**: SSH configuration disables root login and password authentication. Use Ansible's `lineinfile` or templates to configure SSH.
- **Fail2ban Configuration**: Fail2ban is installed and configured. Use Ansible to install and configure fail2ban with templates.
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - These should be moved to Ansible Vault or an external secrets management system

### Technical Challenges

- **Multi-site Configuration**: The dynamic generation of Nginx site configurations based on node attributes will need to be replicated using Ansible's templating system.
- **SSL Certificate Generation**: The self-signed certificate generation logic will need to be converted to use Ansible's `openssl_*` modules.
- **Service Dependencies**: Ensuring proper ordering of service installation and configuration, particularly for the FastAPI application which depends on PostgreSQL.
- **Idempotency**: Ensuring all operations remain idempotent, especially the database user and schema creation for PostgreSQL.

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Relatively self-contained with clear configuration patterns

2. **cache** (Priority 2)
   - Simple service configuration with external dependencies
   - Moderate complexity due to Redis configuration requirements

3. **fastapi-tutorial** (Priority 3)
   - Application deployment with database dependencies
   - More complex due to Python environment setup and PostgreSQL configuration

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based systems.
2. Self-signed certificates are acceptable for development; production may require integration with Let's Encrypt or other certificate providers.
3. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate for the target environment.
4. The FastAPI application repository at `https://github.com/dibanez/fastapi_tutorial.git` will remain available.
5. The current Redis and PostgreSQL password configurations are for development only and will be replaced with more secure credentials in production.
6. The Vagrant development environment will continue to be used for testing.
7. No custom Chef handlers or other Chef-specific features are in use beyond what is visible in the repository.