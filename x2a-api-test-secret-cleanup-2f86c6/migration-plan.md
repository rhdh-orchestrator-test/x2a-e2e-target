# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, security configurations, and service deployments.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- Well-structured Chef cookbooks with clear separation of concerns
- Standard web server, caching, and application deployment patterns
- Security configurations that need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and fail2ban/ufw configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, fail2ban integration, UFW firewall rules

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

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef configuration file with run list and node attributes
- `solo.rb`: Chef configuration file for Chef Solo
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration file for local development environment

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in Vagrant
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks
- **Python 3 and pip**: Use Ansible's package module for installation
- **PostgreSQL**: Use Ansible's postgresql_* modules for database and user management

### Security Considerations

- **SSL/TLS Configuration**: 
  - Migration approach: Use Ansible's openssl_* modules to generate self-signed certificates
  - Ensure proper file permissions are maintained for private keys

- **Firewall Configuration (UFW)**:
  - Migration approach: Use Ansible's ufw module to configure firewall rules
  - Ensure default deny policy and specific allow rules are preserved

- **fail2ban Integration**:
  - Migration approach: Use Ansible's template module to create fail2ban configuration
  - Ensure service is enabled and started

- **SSH Hardening**:
  - Migration approach: Use Ansible's lineinfile or template module to configure sshd_config
  - Maintain settings for root login and password authentication

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (redis_secure_password_123)
  - PostgreSQL password is hardcoded in the recipe (fastapi_password)
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current setup dynamically generates Nginx site configurations based on node attributes
  - Mitigation strategy: Use Ansible templates with loops to generate site configurations from variables

- **SSL Certificate Generation**:
  - Description: Self-signed certificates are generated for each site
  - Mitigation strategy: Use Ansible's openssl_* modules with proper idempotency checks

- **Service Dependencies**:
  - Description: Services have specific ordering requirements (e.g., PostgreSQL before FastAPI)
  - Mitigation strategy: Use Ansible handlers and meta dependencies to ensure proper ordering

- **Redis Configuration Patching**:
  - Description: The current setup uses a ruby_block to modify Redis configuration
  - Mitigation strategy: Use Ansible templates with proper configuration options instead of post-installation patching

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Base Nginx installation
   - SSL certificate generation
   - Security configurations (fail2ban, ufw)
   - Site configurations

2. **cache** (low complexity, independent service)
   - Memcached installation and configuration
   - Redis installation and configuration

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - PostgreSQL installation and configuration
   - Python environment setup
   - Application deployment
   - Service configuration

### Assumptions

1. The target environment will continue to be Fedora/CentOS/Ubuntu based systems
2. Self-signed certificates are acceptable for the migrated solution
3. The same security policies should be applied in the Ansible version
4. The FastAPI application source code will remain at the same GitHub repository
5. The directory structure for web content and application code will remain the same
6. The PostgreSQL database schema is managed by the application, not by the infrastructure code
7. Redis and Memcached configurations don't require clustering or replication
8. The Nginx sites will continue to use the same domain names and SSL configuration
9. The current hardcoded passwords will be replaced with Ansible Vault secured variables