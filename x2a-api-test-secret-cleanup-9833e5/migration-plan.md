# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup with three main cookbooks: nginx-multisite, cache, and fastapi-tutorial. The migration to Ansible will involve converting Chef recipes, templates, and attributes to Ansible roles, tasks, templates, and variables. The estimated timeline for this migration is 3-4 weeks, with moderate complexity due to the interdependencies between components and security configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and proper SSL configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, fail2ban integration, UFW firewall configuration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (both local and external from Chef Supermarket). Will be replaced by Ansible Galaxy requirements.yml.
- `Vagrantfile`: Defines the development VM using Fedora 42. Can be adapted for Ansible-based provisioning.
- `solo.json`: Contains Chef node attributes and run list. Will be converted to Ansible inventory variables.
- `solo.rb`: Chef Solo configuration. Will be replaced by Ansible configuration.
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef. Will be replaced by Ansible provisioning.

### Target Details

Based on the source configuration files:

- **Operating System**: The repository supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) as stated in the metadata.rb files. The Vagrantfile uses Fedora 42 for development.
- **Virtual Machine Technology**: Vagrant with libvirt provider as specified in the Vagrantfile.
- **Cloud Platform**: Not specified in the repository. The configuration appears to be designed for on-premises or generic VM deployment.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation tasks
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package installation tasks

### Security Considerations

- **SSL Certificate Management**: 
  - The nginx-multisite cookbook generates self-signed certificates for development
  - Migration approach: Use Ansible's openssl_* modules for certificate generation or community.crypto collection

- **Firewall Configuration**: 
  - UFW firewall rules are configured in the security.rb recipe
  - Migration approach: Use Ansible's ufw module or firewalld module depending on target OS

- **Fail2ban Integration**: 
  - Fail2ban is configured for intrusion prevention
  - Migration approach: Use Ansible's template module to configure fail2ban similar to the Chef approach

- **SSH Hardening**: 
  - SSH configuration includes disabling root login and password authentication
  - Migration approach: Use Ansible's lineinfile or template module to configure SSH

- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (redis_secure_password_123)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (fastapi/fastapi_password)
  - Migration approach: Use Ansible Vault to secure these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - The nginx-multisite cookbook dynamically creates site configurations based on attributes
  - Migration approach: Use Ansible loops with templates to achieve the same dynamic configuration

- **Service Dependencies**: 
  - The FastAPI application depends on PostgreSQL being configured first
  - Migration approach: Use Ansible handlers and proper task ordering to ensure dependencies are met

- **SSL Certificate Generation**: 
  - Self-signed certificates are generated for each site
  - Migration approach: Use Ansible's openssl_* modules with proper idempotency checks

- **System Hardening**: 
  - Multiple security configurations are applied (sysctl, SSH, firewall, fail2ban)
  - Migration approach: Create a dedicated security role with separate tasks for each component

### Migration Order

1. **cache** (Priority 1 - low risk, standalone services)
   - Simple configuration of Memcached and Redis services
   - Few dependencies on other components

2. **nginx-multisite** (Priority 2 - moderate complexity)
   - Core web server configuration
   - Security hardening components
   - SSL certificate generation

3. **fastapi-tutorial** (Priority 3 - higher complexity)
   - Depends on PostgreSQL configuration
   - Involves application deployment and service management
   - Environment configuration

### Assumptions

1. The target environment will continue to use the same operating systems (Ubuntu/CentOS) as specified in the metadata.rb files.
2. Self-signed certificates are acceptable for the migrated solution (as used in the current Chef implementation).
3. The same security hardening measures will be required in the Ansible implementation.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The Vagrant development environment will be maintained, but with Ansible provisioning instead of Chef.
6. The current Redis and PostgreSQL passwords are development passwords and will be replaced with proper secrets management in production.
7. The nginx sites configuration (test.cluster.local, ci.cluster.local, status.cluster.local) will remain the same in the migrated solution.