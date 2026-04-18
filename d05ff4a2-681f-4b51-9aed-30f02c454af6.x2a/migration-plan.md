# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application with PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- **Total**: 5-6 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- External dependencies on community cookbooks need to be replaced with Ansible Galaxy roles
- Security configurations need careful migration to maintain hardening standards

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site-specific configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef configuration file containing the run list and node attributes
- `solo.rb`: Chef configuration file specifying cookbook paths and log settings
- `Vagrantfile`: Defines a Fedora 42 VM with Nginx for local development and testing
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (specified in Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible Galaxy memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy redis role (e.g., geerlingguy.redis)

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW; migrate to Ansible's `ufw` module
- **Fail2ban Setup**: Migrate fail2ban configuration to Ansible using the `template` module
- **SSH Hardening**: Preserve SSH security settings (disable root login, password authentication)
- **SSL Certificate Management**: Migrate self-signed certificate generation to Ansible's `openssl_*` modules
- **Vault/secrets management**:
  - Redis password in cache cookbook (hardcoded as 'redis_secure_password_123')
  - PostgreSQL credentials in fastapi-tutorial cookbook (hardcoded as 'fastapi_password')
  - Total credentials detected: 2 hardcoded passwords

### Technical Challenges

- **Multi-site Nginx Configuration**: Ensure the dynamic generation of site configurations is preserved in Ansible
- **SSL Certificate Management**: Properly handle certificate generation and permissions
- **Service Dependencies**: Maintain proper ordering of service deployments (e.g., PostgreSQL before FastAPI app)
- **Idempotency**: Ensure database creation tasks are idempotent like the original Chef recipes

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security hardening that should be applied first

2. **cache** (Priority 2)
   - Standalone services with minimal dependencies
   - Required by the application layer

3. **fastapi-tutorial** (Priority 3)
   - Application layer that depends on both web server and cache services
   - Requires database setup and configuration

### Assumptions

1. The target environment will continue to be Fedora-based systems (specifically Fedora 42 as specified in the Vagrantfile)
2. The same network configuration will be maintained (ports 80/443 exposed)
3. Self-signed certificates are acceptable for development (production would likely use Let's Encrypt or other CA)
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current security hardening measures are sufficient and should be maintained
6. The current directory structure for web content (/var/www/[site]) will be preserved
7. Redis and Memcached configurations don't require advanced tuning beyond what's currently implemented