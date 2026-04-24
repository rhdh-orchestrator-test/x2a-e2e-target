# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- Total: 5-6 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- External dependencies are explicitly defined in Berksfile
- Security configurations are present and need careful migration
- Secrets management needs improvement in the Ansible implementation

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, fail2ban integration, UFW firewall configuration

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (both local and from Chef Supermarket)
  - Migration consideration: Dependencies need to be mapped to Ansible Galaxy roles or custom roles
  
- `solo.json`: Defines the Chef run list and configuration attributes
  - Migration consideration: Convert to Ansible group_vars or host_vars

- `solo.rb`: Chef Solo configuration
  - Migration consideration: Replace with Ansible configuration

- `Vagrantfile`: Defines the development VM configuration
  - Migration consideration: Update to use Ansible provisioner instead of Chef

- `vagrant-provision.sh`: Shell script to install Chef and run the cookbooks
  - Migration consideration: Replace with Ansible provisioning script

### Target Details

- **Operating System**: Based on the cookbooks, the target systems are Ubuntu (>= 18.04) and CentOS (>= 7.0). The Vagrantfile specifies Fedora 42 as the development environment.
- **Virtual Machine Technology**: Vagrant with libvirt provider is used for development.
- **Cloud Platform**: No specific cloud platform configurations were found. The setup appears to be cloud-agnostic.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible community.nginx role or create a custom nginx role
- **memcached (~> 6.0)**: Replace with geerlingguy.memcached or create a custom memcached role
- **redisio (~> 7.2.4)**: Replace with geerlingguy.redis or create a custom redis role
- **PostgreSQL**: Replace with geerlingguy.postgresql or community.postgresql collection

### Security Considerations

- **SSL Certificate Management**: 
  - Current implementation generates self-signed certificates
  - Migration approach: Use Ansible's openssl_* modules or community.crypto collection

- **Firewall Configuration (UFW)**:
  - Current implementation configures UFW with specific rules
  - Migration approach: Use Ansible's ufw module

- **fail2ban Configuration**:
  - Current implementation installs and configures fail2ban
  - Migration approach: Use community.general.fail2ban module or create a custom role

- **SSH Hardening**:
  - Current implementation disables root login and password authentication
  - Migration approach: Use Ansible's lineinfile module or dedicated ssh hardening role

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe
  - PostgreSQL credentials are hardcoded in the recipe
  - Migration approach: Use Ansible Vault for storing sensitive information

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation dynamically creates multiple virtual hosts based on node attributes
  - Mitigation strategy: Use Ansible loops with templates to achieve the same functionality

- **SSL Certificate Generation**:
  - Description: Self-signed certificates are generated with specific parameters
  - Mitigation strategy: Use Ansible's openssl_certificate module with similar parameters

- **Redis Configuration Patching**:
  - Description: The current implementation uses a ruby_block to modify Redis configuration
  - Mitigation strategy: Create a proper Redis configuration template in Ansible

- **PostgreSQL User and Database Creation**:
  - Description: The current implementation uses shell commands to create database and user
  - Mitigation strategy: Use Ansible's postgresql_user and postgresql_db modules

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Create base Nginx role
   - Implement SSL certificate generation
   - Implement virtual host configuration
   - Implement security hardening

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis configuration with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Implement PostgreSQL installation and configuration
   - Implement Python environment setup
   - Implement application deployment
   - Implement systemd service configuration

### Assumptions

1. The target environment will continue to support the same operating systems (Ubuntu 18.04+ and CentOS 7+)
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or other CA)
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
4. The current security configurations (fail2ban, UFW, SSH hardening) are appropriate for the target environment
5. The Redis and PostgreSQL passwords in the current implementation are for development only and will be replaced with secure passwords in the Ansible Vault
6. The Nginx sites configuration in solo.json overrides the default attributes in the cookbook
7. The Vagrant development environment will continue to be used for testing the Ansible playbooks