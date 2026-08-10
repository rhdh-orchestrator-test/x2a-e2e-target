# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- Well-structured Chef cookbooks with clear separation of concerns
- Standard infrastructure components (Nginx, Redis, Memcached, PostgreSQL)
- Security configurations that need careful migration
- Self-signed SSL certificates that need to be managed

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including external cookbooks from Chef Supermarket (nginx, memcached, redisio)
- `solo.json`: Contains node configuration including the run list and attribute overrides for Nginx sites and security settings
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `Vagrantfile`: Defines the development VM using Fedora 42 with port forwarding and resource allocation
- `vagrant-provision.sh`: Shell script that installs Chef and runs the cookbooks in the Vagrant environment

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile) with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks
- **Python 3 and pip**: Use Ansible's package module to install Python dependencies
- **PostgreSQL**: Use Ansible's postgresql_* modules for database management

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration approach: Use Ansible's openssl_* modules to generate certificates
  - Consider integrating with Let's Encrypt for production environments

- **Firewall Configuration**:
  - UFW is configured to allow only SSH, HTTP, and HTTPS
  - Migration approach: Use Ansible's ufw module to configure firewall rules

- **Fail2ban Integration**:
  - Fail2ban is configured to protect against brute force attacks
  - Migration approach: Use Ansible's template module to configure fail2ban

- **SSH Hardening**:
  - Root login is disabled
  - Password authentication is disabled
  - Migration approach: Use Ansible's lineinfile or template module to configure SSH

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (redis_secure_password_123)
  - PostgreSQL credentials are hardcoded in the FastAPI recipe
  - Migration approach: Use Ansible Vault to securely store and manage these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Maintaining the dynamic generation of site configurations
  - Mitigation: Use Ansible's with_items/loop to iterate through site configurations

- **SSL Certificate Management**: 
  - Challenge: Ensuring proper permissions and ownership of SSL certificates
  - Mitigation: Use Ansible's file module with appropriate mode and owner settings

- **Service Dependencies**: 
  - Challenge: Ensuring proper ordering of service installation and configuration
  - Mitigation: Use Ansible's handlers and notify mechanism to manage service restarts

- **Database Initialization**: 
  - Challenge: Creating PostgreSQL users and databases idempotently
  - Mitigation: Use Ansible's postgresql_* modules which handle idempotence properly

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add SSL certificate management
   - Add security configurations (fail2ban, ufw)
   - Add site-specific configurations

2. **cache** (Priority 2)
   - Relatively simple configuration for Memcached and Redis
   - Ensure Redis password is stored securely in Ansible Vault

3. **fastapi-tutorial** (Priority 3)
   - More complex with database setup, Python environment, and application deployment
   - Depends on PostgreSQL being properly configured
   - Requires systemd service configuration

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions.
2. The self-signed SSL certificates approach is acceptable for the migrated solution, or a clear alternative (like Let's Encrypt) will be specified.
3. The current directory structure in the target environment (`/opt/server/test`, etc.) should be maintained.
4. The FastAPI application source will continue to be pulled from the same Git repository.
5. The Redis and PostgreSQL passwords currently hardcoded in recipes will be migrated to Ansible Vault.
6. The current security configurations (fail2ban, ufw, SSH hardening) are to be maintained in the Ansible solution.
7. The Vagrant development environment should be preserved but updated to use Ansible provisioning instead of Chef.