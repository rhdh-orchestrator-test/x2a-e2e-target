# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services (Redis and Memcached) and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- No custom resources or complex Chef-specific patterns
- Standard infrastructure components (Nginx, Redis, Memcached, PostgreSQL)
- Self-contained development environment using Vagrant

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), custom site templates

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

- `Berksfile`: Defines cookbook dependencies (nginx, memcached, redisio) - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Contains node attributes and run list - will be replaced by Ansible inventory variables
- `solo.rb`: Chef Solo configuration - not needed in Ansible
- `Vagrantfile`: Defines the development VM - can be adapted for Ansible provisioning
- `vagrant-provision.sh`: Installs Chef and runs cookbooks - will be replaced with Ansible provisioning

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or direct package installation
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible redis role from Galaxy or direct package installation

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration should maintain proper permissions (root:ssl-cert with 640 permissions)
  - Consider integrating with Ansible's crypto modules for certificate generation

- **Firewall Configuration**: 
  - UFW configuration should be migrated to equivalent Ansible ufw module
  - Maintain the same allowed services (SSH, HTTP, HTTPS)

- **SSH Hardening**:
  - Disable root login
  - Disable password authentication
  - Maintain these security settings in Ansible

- **Fail2Ban Configuration**:
  - Maintain fail2ban configuration for brute force protection

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe as 'redis_secure_password_123'
  - PostgreSQL password is hardcoded in the recipe as 'fastapi_password'
  - These should be moved to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - The Chef cookbook dynamically generates site configurations based on node attributes
  - Ansible will need to use templates and loops to achieve the same functionality
  - Solution: Use Ansible with_items/loop constructs with templates

- **SSL Certificate Generation**:
  - Chef uses inline shell commands for certificate generation
  - Solution: Use Ansible's openssl_* modules for more idiomatic certificate management

- **Service Dependencies**:
  - FastAPI service depends on PostgreSQL
  - Solution: Use Ansible handlers and meta dependencies to ensure proper ordering

- **Redis Configuration Patching**:
  - The Chef recipe uses a ruby_block to modify Redis configuration
  - Solution: Create a proper Ansible template for Redis configuration instead of patching

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Then add SSL and security features
   - Finally implement the multi-site configuration

2. **cache** (Priority 2)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper service management

3. **fastapi-tutorial** (Priority 3)
   - Set up PostgreSQL database
   - Deploy the FastAPI application
   - Configure the systemd service

### Assumptions

1. The target environment will continue to use Vagrant for development/testing
2. The same operating systems (Fedora/Ubuntu/CentOS) will be supported
3. Self-signed certificates are acceptable (no Let's Encrypt integration required)
4. The FastAPI application source code will remain at the same GitHub repository
5. No CI/CD pipeline integration is required for the migration
6. The current security settings (fail2ban, ufw, SSH hardening) should be maintained
7. The Redis and PostgreSQL passwords will be managed securely in the new implementation
8. The directory structure for web content (/var/www/[site]) will remain the same
9. The SSL certificate paths (/etc/ssl/certs and /etc/ssl/private) will remain the same