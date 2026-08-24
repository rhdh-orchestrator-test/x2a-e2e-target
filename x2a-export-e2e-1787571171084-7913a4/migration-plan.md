# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- External dependencies are clearly specified in the Berksfile
- The configuration is relatively standard with common services (Nginx, Redis, Memcached, PostgreSQL)
- Security configurations are present and need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, including security hardening
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL setup, security hardening (fail2ban, UFW)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (both local and external from Chef Supermarket)
- `solo.json`: Contains Chef node attributes and run list for the Chef Solo run
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef
- `Vagrantfile`: Defines the Vagrant VM configuration (Fedora 42 with libvirt provider)

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in Vagrant
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or community.general collection
- **memcached (~> 6.0)**: Replace with Ansible's `memcached` role or community.general collection
- **redisio (~> 7.2.4)**: Replace with Ansible's `redis` role or community.general collection
- **Python 3 and venv**: Use Ansible's `pip` and `package` modules
- **PostgreSQL**: Use Ansible's `postgresql_*` modules or community.postgresql collection

### Security Considerations

- **SSL/TLS Configuration**: 
  - Migration approach: Use Ansible's `openssl_*` modules to generate self-signed certificates or integrate with Let's Encrypt using `community.crypto` collection
  - Ensure proper file permissions for certificate files

- **Redis Authentication**: 
  - Migration approach: Use Ansible Vault to store the Redis password securely
  - Update Redis configuration template to include authentication

- **Fail2ban Configuration**: 
  - Migration approach: Use Ansible to deploy fail2ban configuration files
  - Ensure proper service management

- **UFW Firewall Rules**: 
  - Migration approach: Use Ansible's `ufw` module to configure firewall rules
  - Ensure idempotent rule application

- **SSH Hardening**: 
  - Migration approach: Use Ansible to configure SSH daemon with secure settings
  - Disable root login and password authentication as specified in solo.json

- **Vault/secrets management**:
  - PostgreSQL credentials in fastapi-tutorial recipe (plaintext)
  - Redis password in cache recipe (plaintext)
  - Both should be migrated to Ansible Vault variables

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current setup uses Chef templates to generate site configurations for multiple domains
  - Mitigation strategy: Create Ansible templates with similar structure, use Ansible's template module with proper variable substitution

- **Service Dependencies**: 
  - Description: The FastAPI application depends on PostgreSQL being configured first
  - Mitigation strategy: Use Ansible's handlers and notify system to ensure proper service ordering

- **Custom Ruby Block for Redis Configuration**: 
  - Description: The cache cookbook uses a Ruby block to modify Redis configuration
  - Mitigation strategy: Use Ansible's lineinfile or replace module to achieve the same configuration changes

- **Environment File Creation**: 
  - Description: The FastAPI application requires an environment file with database connection details
  - Mitigation strategy: Use Ansible templates with variables from Ansible Vault for sensitive information

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Create base Nginx role
   - Implement SSL configuration
   - Implement security hardening
   - Configure multi-site setup

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on database)
   - Implement PostgreSQL database setup
   - Configure Python environment
   - Deploy application from Git
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora/CentOS/Ubuntu based systems
2. Self-signed certificates are acceptable for development/testing (as used in the current setup)
3. The same directory structure for web content will be maintained (/var/www/*)
4. The FastAPI application will continue to be deployed from the same Git repository
5. The PostgreSQL database schema does not require special migration steps
6. The Redis configuration hack in the cache cookbook is still necessary in the target environment
7. The security requirements (fail2ban, UFW, SSH hardening) remain the same
8. The Vagrant development environment will be maintained but converted to use Ansible provisioner