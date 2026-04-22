# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, security configurations, and service deployments.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- Well-structured Chef cookbooks with clear separation of concerns
- Standard web infrastructure components (Nginx, Redis, Memcached, PostgreSQL)
- Security configurations that need careful migration
- Hardcoded credentials that need to be moved to Ansible Vault

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and SSL certificate management
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup, security headers, fail2ban integration, UFW firewall configuration

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

- `Berksfile`: Dependency management file listing both local cookbooks and external dependencies from Chef Supermarket
  - Migration consideration: Replace with Ansible Galaxy requirements.yml
  
- `solo.json`: Chef configuration file containing the run list and node attributes
  - Migration consideration: Convert to Ansible inventory variables or group_vars
  
- `solo.rb`: Chef configuration file specifying cookbook paths and log settings
  - Migration consideration: Replace with ansible.cfg configuration
  
- `Vagrantfile`: Defines the development VM configuration using Vagrant
  - Migration consideration: Update to use Ansible provisioner instead of Chef
  
- `vagrant-provision.sh`: Shell script to install Chef and run the cookbooks
  - Migration consideration: Replace with Ansible playbook execution

### Target Details

Based on the source repository analysis:

- **Operating System**: Fedora 42 (from Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Libvirt (from Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package installation
- **Python 3 and pip**: Use Ansible's package module for installation
- **PostgreSQL**: Use Ansible's postgresql_* modules for database and user management

### Security Considerations

- **SSL/TLS Configuration**: 
  - Migrate SSL certificate generation for multiple sites
  - Ensure proper file permissions for private keys
  - Maintain strong cipher configurations

- **Firewall (UFW)**: 
  - Use Ansible's ufw module to configure firewall rules
  - Maintain default deny policy with specific allow rules

- **fail2ban**: 
  - Configure fail2ban with Ansible to protect against brute force attacks
  - Migrate jail.local configuration

- **SSH Hardening**:
  - Disable root login
  - Disable password authentication
  - Migrate to Ansible's openssh_* modules

- **Vault/secrets management**:
  - Redis password: Found in cache/recipes/default.rb ("redis_secure_password_123")
  - PostgreSQL credentials: Found in fastapi-tutorial/recipes/default.rb (user: "fastapi", password: "fastapi_password")
  - Move all hardcoded credentials to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Maintaining the dynamic generation of multiple virtual hosts with SSL
  - Mitigation: Use Ansible templates with loops to generate site configurations

- **SSL Certificate Management**: 
  - Challenge: Self-signed certificate generation for development environments
  - Mitigation: Use Ansible's openssl_* modules to generate certificates with proper permissions

- **Security Hardening**: 
  - Challenge: Ensuring all security configurations are properly migrated
  - Mitigation: Create a dedicated security role with tasks for each security aspect

- **Service Dependencies**: 
  - Challenge: Ensuring proper service startup order (PostgreSQL before FastAPI)
  - Mitigation: Use Ansible handlers and meta dependencies between roles

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Base infrastructure component that other services depend on
   - Contains security configurations that should be applied early

2. **cache** (Priority 2)
   - Standalone services with minimal dependencies
   - Required by the application but not as fundamental as Nginx

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on both Nginx and PostgreSQL
   - More complex with database setup, Python environment, and service configuration

### Assumptions

1. The target environment will continue to be Fedora or a similar Linux distribution
2. Self-signed certificates are acceptable for development (production would likely use Let's Encrypt or similar)
3. The same network ports and configurations will be maintained
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current security configurations are appropriate for the target environment
6. No changes to the application logic or configuration are required during migration
7. The Vagrant development environment will be maintained for testing