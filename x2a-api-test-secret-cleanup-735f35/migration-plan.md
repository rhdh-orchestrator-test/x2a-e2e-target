# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- No custom resources or complex Chef-specific patterns
- Standard infrastructure components (Nginx, Redis, Memcached, PostgreSQL)
- Security configurations need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), sysctl security settings

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints. Will be replaced by Ansible Galaxy requirements.yml.
- `solo.json`: Chef node configuration with run list and attribute overrides. Will be replaced by Ansible inventory variables.
- `solo.rb`: Chef configuration file. Will be replaced by Ansible configuration.
- `Vagrantfile`: Defines the development VM using Fedora 42. Can be adapted for Ansible testing.
- `vagrant-provision.sh`: Shell script to install Chef and run the cookbooks. Will be replaced by Ansible provisioning.

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with development environment using Fedora 42
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible community.general.nginx or builtin package module
- **memcached (~> 6.0)**: Replace with Ansible community.general.memcached or custom role
- **redisio (~> 7.2.4)**: Replace with Ansible community.general.redis or custom role
- **Python 3 and pip**: Use Ansible builtin package module
- **PostgreSQL**: Use Ansible community.postgresql collection

### Security Considerations

- **SSL/TLS Management**: 
  - Self-signed certificates are generated for each site
  - Migration approach: Use Ansible crypto modules (openssl_certificate, openssl_privatekey)

- **Firewall Configuration**: 
  - UFW is configured with specific rules
  - Migration approach: Use Ansible community.general.ufw module

- **Fail2ban Configuration**: 
  - Custom jail configuration
  - Migration approach: Use Ansible community.general.fail2ban module

- **SSH Hardening**: 
  - Root login disabled
  - Password authentication disabled
  - Migration approach: Use Ansible community.general.ssh module or lineinfile

- **Vault/secrets management**:
  - Redis password hardcoded in recipe: "redis_secure_password_123"
  - PostgreSQL password hardcoded in recipe: "fastapi_password"
  - Migration approach: Use Ansible Vault for all credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The Chef cookbook dynamically creates multiple Nginx sites with SSL
  - Mitigation: Create Ansible templates with Jinja2 loops to generate site configurations

- **Redis Configuration Hack**: 
  - Description: The Chef cookbook includes a ruby_block to modify Redis configuration
  - Mitigation: Create proper Redis configuration template in Ansible

- **Service Orchestration**: 
  - Description: Proper ordering of service installation, configuration, and startup
  - Mitigation: Use Ansible handlers and proper task dependencies

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component
   - Other services depend on it
   - Contains security configurations

2. **cache** (Priority 2)
   - Standalone service
   - Moderate complexity
   - Depends on external modules

3. **fastapi-tutorial** (Priority 3)
   - Application layer
   - Depends on PostgreSQL
   - Contains database initialization

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL systems
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt)
3. The Vagrant development environment will be maintained
4. No custom Chef handlers or complex search functionality is in use
5. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
6. The current security settings (fail2ban, ufw, SSH hardening) are appropriate for the target environment
7. The Redis and PostgreSQL passwords in the code are development passwords that will be replaced with secure values in production