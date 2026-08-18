# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- Limited external dependencies (nginx, memcached, redisio)
- Security configurations that need careful migration
- SSL certificate management that requires special attention

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
    - Key Features: Python virtual environment setup, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Contains node attributes and run list - will be replaced by Ansible inventory variables
- `solo.rb`: Chef configuration file - not needed in Ansible
- `vagrant-provision.sh`: Provisioning script for Vagrant - will be replaced by Ansible provisioner in Vagrantfile
- `Vagrantfile`: VM configuration - will be updated to use Ansible provisioner instead of Chef

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) based on cookbook metadata, with Fedora 42 used in Vagrant
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration should preserve the same certificate generation logic
  - Consider using Ansible's community.crypto.openssl_* modules

- **Firewall Configuration**: 
  - UFW is configured with default deny and specific allow rules
  - Migrate to Ansible's community.general.ufw module

- **SSH Hardening**:
  - Root login disabled
  - Password authentication disabled
  - Use Ansible's openssh_config module for equivalent configuration

- **Fail2Ban Configuration**:
  - Custom jail configuration
  - Use Ansible's community.general.fail2ban module or template tasks

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe
  - PostgreSQL credentials are hardcoded in the FastAPI recipe
  - Recommend using Ansible Vault for storing these secrets

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - The Chef cookbook dynamically creates site configurations based on node attributes
  - Ansible implementation will need similar templating logic with loops
  - Solution: Use Ansible with_items/loop constructs with templates

- **SSL Certificate Generation**:
  - Self-signed certificates are generated with specific attributes
  - Solution: Use community.crypto.openssl_* modules with similar parameters

- **Service Dependencies**:
  - FastAPI service depends on PostgreSQL
  - Solution: Use Ansible handlers and meta dependencies between roles

- **Configuration File Modifications**:
  - The cache cookbook uses a ruby_block to modify Redis configuration
  - Solution: Use Ansible's lineinfile or template modules with proper validation

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Then add SSL and security features
   - Finally implement the multi-site configuration

2. **cache** (Priority 2)
   - Standalone services with external dependencies
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on properly configured infrastructure
   - Implement PostgreSQL database setup
   - Implement Python application deployment
   - Configure systemd service

### Assumptions

1. The target environment will continue to use the same operating systems (Ubuntu/CentOS/Fedora)
2. Self-signed certificates are acceptable for the migrated solution (vs. Let's Encrypt or other CA)
3. The same security policies should be applied in the Ansible version
4. The directory structure for web content will remain the same
5. PostgreSQL and Python versions are not explicitly specified and will use system defaults
6. The FastAPI application repository URL will remain accessible
7. The Vagrant development environment should be preserved with equivalent functionality
8. No CI/CD pipeline integration is required as part of the migration