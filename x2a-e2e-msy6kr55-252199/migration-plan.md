# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services and a FastAPI application. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- No complex custom resources or libraries
- Standard infrastructure components (Nginx, Redis, Memcached, PostgreSQL)
- Security configurations that need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, SSH hardening)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (nginx, memcached, redisio) - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Contains node attributes and run list - will be replaced by Ansible inventory variables
- `solo.rb`: Chef configuration file - no direct Ansible equivalent needed
- `Vagrantfile`: Defines development VM - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisions the VM with Chef - will be replaced with Ansible provisioning

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or local development

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible community.nginx collection or direct package installation
- **memcached (~> 6.0)**: Replace with Ansible community.general.memcached module
- **redisio (~> 7.2.4)**: Replace with Ansible community.redis collection

### Security Considerations

- **SSL Certificate Management**: Self-signed certificates are generated for development. In Ansible, use community.crypto collection for certificate generation
- **Firewall Configuration**: UFW rules need to be migrated to Ansible's community.general.ufw module
- **Fail2ban Configuration**: Migrate fail2ban configuration using Ansible's community.general.fail2ban module
- **SSH Hardening**: SSH configuration hardening needs to be migrated using Ansible's openssh_config module
- **Vault/secrets management**:
  - Redis password in cache/recipes/default.rb: "redis_secure_password_123"
  - PostgreSQL credentials in fastapi-tutorial/recipes/default.rb: User "fastapi" with password "fastapi_password"
  - These should be moved to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple Nginx sites will need careful translation to Ansible templates and loops
- **Service Dependencies**: Ensuring proper ordering of service installations and configurations (e.g., PostgreSQL before FastAPI application)
- **Template Migration**: Converting ERB templates to Jinja2 format for Ansible
- **Idempotency**: Ensuring all operations remain idempotent, especially the conditional commands that use not_if guards in Chef

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security configurations that should be established first

2. **cache** (Priority 2)
   - Supporting services with external dependencies
   - Relatively simple configuration

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on other infrastructure components
   - More complex with database setup and application configuration

### Assumptions

1. The target environment will continue to be Fedora-based systems
2. Self-signed certificates are acceptable for development (production would likely use Let's Encrypt or other CA)
3. The same security policies should be maintained in the Ansible implementation
4. The Vagrant development workflow should be preserved
5. No changes to the application code or deployment architecture are required
6. The current Redis and Memcached configurations meet performance requirements
7. The PostgreSQL database setup is for development purposes and may need enhancement for production
8. The current directory structure in the target system (/opt/fastapi-tutorial, /var/www/sites) should be maintained