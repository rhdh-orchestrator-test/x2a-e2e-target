# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure for deploying a multi-site Nginx web server with SSL, security hardening, caching services (Redis and Memcached), and a FastAPI Python application with PostgreSQL database. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and resources to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- Total: 5-6 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- No complex custom resources or libraries
- Standard infrastructure components (web server, database, caching)
- Security configurations that need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening (fail2ban, ufw firewall), and SSL certificate management
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and ufw

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

- `Berksfile`: Dependency management for Chef cookbooks. Lists both local cookbooks and external dependencies from Chef Supermarket.
- `solo.json`: Chef run list and configuration data. Contains site configurations, SSL settings, and security options.
- `solo.rb`: Chef Solo configuration file.
- `Vagrantfile`: Defines the development environment using Vagrant with Fedora 42.
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef.

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Libvirt (from Vagrantfile)
- **Cloud Platform**: Not specified, appears to be targeting on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` role or direct package installation and configuration

### Security Considerations

- **SSL Certificate Management**: 
  - Current implementation generates self-signed certificates
  - Migration should maintain or improve certificate management
  - Consider integrating with Ansible's `community.crypto` collection for certificate operations

- **Firewall Configuration**: 
  - Current implementation uses UFW
  - Migration should use Ansible's `ansible.posix.firewalld` module for Fedora/RHEL or maintain UFW for Ubuntu

- **Fail2ban Configuration**: 
  - Current implementation installs and configures fail2ban
  - Migration should use Ansible's fail2ban modules or templates

- **SSH Hardening**:
  - Current implementation disables root login and password authentication
  - Migration should maintain these security practices using Ansible's `ansible.posix.sshd_config` module

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL password is hardcoded in the recipe (`fastapi_password`)
  - Migration should use Ansible Vault for storing these credentials securely

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Maintaining the dynamic generation of multiple virtual hosts with SSL
  - Mitigation: Use Ansible's template module with Jinja2 templates to generate site configurations

- **SSL Certificate Management**: 
  - Challenge: Ensuring proper permissions and ownership for SSL certificates and keys
  - Mitigation: Use Ansible's file module with appropriate mode and owner settings

- **Service Dependencies**: 
  - Challenge: Maintaining proper service start order (e.g., PostgreSQL before FastAPI application)
  - Mitigation: Use Ansible's `meta: flush_handlers` and proper handler notification

- **Idempotency**: 
  - Challenge: Ensuring one-time operations like database creation remain idempotent
  - Mitigation: Use Ansible's `changed_when` and `failed_when` directives to control change reporting

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add SSL and security features
   - Finally, add multi-site configuration

2. **cache** (Priority 2)
   - Independent service with minimal dependencies
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (Priority 3)
   - Depends on PostgreSQL and potentially the web server
   - Implement PostgreSQL installation and configuration
   - Implement Python environment setup and application deployment
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora-based (or compatible RHEL/CentOS)
2. Self-signed certificates are acceptable for the migrated solution
3. The same security hardening measures should be maintained
4. The FastAPI application source code will remain available at the same Git repository
5. The same virtual host names will be maintained
6. Development will continue to use Vagrant for testing
7. No additional monitoring or logging requirements beyond what's in the current implementation