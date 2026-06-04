# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site web server with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 3-4 weeks, with moderate complexity due to the security configurations and multi-site setup.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and fail2ban integration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, firewall configuration

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment, Git repository deployment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints. Will be replaced by Ansible Galaxy requirements.yml.
- `solo.json`: Chef node attributes and run list configuration. Will be replaced by Ansible inventory variables.
- `solo.rb`: Chef configuration file for Chef Solo. Will be replaced by Ansible configuration.
- `Vagrantfile`: Defines the development VM using Fedora 42. Can be adapted for Ansible testing with minimal changes.
- `vagrant-provision.sh`: Shell script to install Chef and run the cookbooks. Will be replaced with Ansible provisioning.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or create a custom role
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role from Galaxy

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should maintain this capability or integrate with Let's Encrypt.
  - Migration approach: Use Ansible's openssl_* modules for certificate generation or community.crypto collection

- **Firewall Configuration (UFW)**: The current implementation configures UFW with specific rules.
  - Migration approach: Use Ansible's ufw module to configure the same rules

- **Fail2ban Integration**: The current implementation installs and configures fail2ban.
  - Migration approach: Use Ansible's template module to create fail2ban configuration files

- **SSH Hardening**: The current implementation disables root login and password authentication.
  - Migration approach: Use Ansible's lineinfile module or template module to configure SSH

- **Vault/secrets management**:
  - Redis password in cache cookbook: Found in default.rb (redis_secure_password_123)
  - PostgreSQL credentials in fastapi-tutorial cookbook: Found in default.rb (fastapi/fastapi_password)
  - Database URL in .env file: Found in fastapi-tutorial/default.rb
  - Total credentials detected: 3 (should be migrated to Ansible Vault)

### Technical Challenges

- **Multi-site Nginx Configuration**: The current implementation uses Chef templates and attributes to configure multiple Nginx sites. 
  - Mitigation: Create Ansible templates that can handle the same level of customization, using host_vars or group_vars for site-specific configuration.

- **Dynamic SSL Certificate Generation**: The current implementation dynamically generates SSL certificates for each site.
  - Mitigation: Use Ansible's openssl_* modules with loops to achieve the same functionality.

- **Redis Configuration Patching**: The current implementation includes a hack to fix Redis configuration.
  - Mitigation: Create a proper Redis configuration template in Ansible rather than patching the file after creation.

- **PostgreSQL User and Database Creation**: The current implementation uses shell commands to create PostgreSQL users and databases.
  - Mitigation: Use Ansible's postgresql_* modules for more idempotent database management.

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation
   - Add SSL certificate generation
   - Add security configurations (fail2ban, ufw)
   - Add multi-site configuration

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis configuration with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Implement PostgreSQL installation and configuration
   - Implement Python environment setup
   - Implement application deployment
   - Implement systemd service configuration

### Assumptions

1. The target environment will continue to be Fedora 42 as specified in the Vagrantfile.
2. Self-signed certificates are acceptable for the migrated solution (production environments might require proper certificates).
3. The security requirements (fail2ban, ufw, SSH hardening) will remain the same.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The current passwords used in the Chef recipes are for development only and will be replaced with more secure passwords stored in Ansible Vault.
6. The Nginx sites configuration (test.cluster.local, ci.cluster.local, status.cluster.local) will remain the same.
7. The current Chef-based development workflow using Vagrant will be replaced with an Ansible-based workflow.