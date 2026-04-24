# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, configuration templates, and security settings.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- **Total**: 5-6 weeks

**Complexity**: Medium
- The codebase is well-structured with clear separation of concerns
- Security configurations are comprehensive and will need careful migration
- External dependencies on community cookbooks will need Ansible equivalents

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and fail2ban/ufw configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, firewall configuration

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file listing both local cookbooks and external dependencies from Chef Supermarket
  - Migration consideration: Replace with Ansible Galaxy requirements.yml
  
- `solo.json`: Chef run list and node attributes configuration
  - Migration consideration: Convert to Ansible inventory variables or group_vars
  
- `solo.rb`: Chef configuration file
  - Migration consideration: Replace with ansible.cfg
  
- `Vagrantfile`: Defines the development VM using Fedora 42
  - Migration consideration: Update to use Ansible provisioner instead of Chef
  
- `vagrant-provision.sh`: Shell script to install Chef and run the cookbooks
  - Migration consideration: Replace with Ansible provisioning commands

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or create a custom role
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy
- **redisio (~> 7.2.4)**: Replace with Ansible redis role from Galaxy
- **Python 3 and venv**: Use Ansible's pip and package modules
- **PostgreSQL**: Use Ansible's postgresql_* modules or community.postgresql collection

### Security Considerations

- **SSL/TLS Configuration**: 
  - Migrate the self-signed certificate generation logic
  - Maintain the secure TLS protocols and cipher configurations
  - Consider using Ansible's openssl_* modules for certificate management

- **Firewall Configuration**:
  - Replace ufw configuration with Ansible's ufw module
  - Maintain the same allowed ports (SSH, HTTP, HTTPS)

- **Fail2ban Configuration**:
  - Use Ansible to deploy and configure fail2ban
  - Migrate the jail.local template

- **SSH Hardening**:
  - Maintain the same security settings (disable root login, disable password authentication)
  - Use Ansible's lineinfile or template modules

- **Vault/secrets management**:
  - Identified credentials:
    - Redis password: "redis_secure_password_123" in cache/recipes/default.rb
    - PostgreSQL user/password: "fastapi"/"fastapi_password" in fastapi-tutorial/recipes/default.rb
    - Database connection string in .env file
  - Recommendation: Use Ansible Vault to secure these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**:
  - Challenge: Maintaining the dynamic generation of multiple virtual hosts with SSL
  - Mitigation: Create Ansible templates with similar logic to the Chef templates, using with_items to iterate over site configurations

- **Redis Configuration Hack**:
  - Challenge: The Chef cookbook includes a hack to fix Redis configuration
  - Mitigation: Create proper Redis configuration templates in Ansible without needing the hack

- **Service Dependencies**:
  - Challenge: Ensuring proper service startup order (PostgreSQL before FastAPI)
  - Mitigation: Use Ansible handlers and proper service dependencies in systemd unit files

- **SSL Certificate Management**:
  - Challenge: Generating and managing self-signed certificates
  - Mitigation: Use Ansible's openssl_* modules with proper idempotency checks

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add SSL and security features
   - Finally, add multi-site configuration

2. **cache** (Priority 2)
   - Relatively independent service
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (Priority 3)
   - Depends on PostgreSQL being configured
   - Implement database setup
   - Implement application deployment
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions
2. Self-signed certificates are acceptable for the migrated environment (not production)
3. The same security requirements will apply in the new environment
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current directory structure in /opt/ and /var/ can be maintained
6. The Vagrant development workflow will be preserved
7. No additional monitoring or logging requirements beyond what's in the current code
8. No high availability or clustering requirements for Redis or Memcached
9. The nginx sites configuration (test.cluster.local, ci.cluster.local, status.cluster.local) will remain the same