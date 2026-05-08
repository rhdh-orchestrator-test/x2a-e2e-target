# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their recipes, templates, attributes, and resources to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The Chef cookbooks are well-structured and focused on specific concerns
- No complex custom resources or libraries
- Standard infrastructure components (web server, caching, application deployment)
- Security configurations need careful attention during migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
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
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4)
- `Vagrantfile`: Defines a Fedora 42 VM with port forwarding for development and testing
- `solo.json`: Contains the Chef run list and node attributes for Nginx sites and security configurations
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified (appears to be designed for local development/testing)

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (community.general.nginx_config or custom role)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role (geerlingguy.redis)

### Security Considerations

- **SSL Certificate Management**: 
  - Chef cookbook generates self-signed certificates
  - Ansible migration should use ansible.builtin.openssl_* modules or community.crypto collection

- **Firewall Configuration**: 
  - Current implementation uses UFW
  - Migrate to ansible.posix.firewalld for RHEL-based systems or community.general.ufw for Debian-based systems

- **Fail2ban Integration**:
  - Migrate fail2ban configuration to use ansible.builtin.template for configuration files

- **SSH Hardening**:
  - Current implementation disables root login and password authentication
  - Use ansible.builtin.lineinfile or ansible.posix.sshd_config module

- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook
  - Migrate to Ansible Vault for secure credential storage
  - Count of credentials detected: 2 (Redis password, PostgreSQL user/password)

### Technical Challenges

- **Custom Resource Migration**: 
  - The nginx-multisite cookbook includes a custom `lineinfile` resource
  - Replace with ansible.builtin.lineinfile module

- **Template Conversion**:
  - Chef ERB templates need conversion to Jinja2 format for Ansible
  - Pay special attention to conditional logic in site.conf.erb

- **Idempotency**:
  - Ensure all Ansible tasks are idempotent, especially for the database creation tasks in fastapi-tutorial

- **Service Management**:
  - Chef uses service resources with notifications
  - Convert to Ansible handlers for service restarts/reloads

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component
   - Other components depend on web server configuration
   - Contains security configurations that should be established first

2. **cache** (Priority 2)
   - Moderate complexity
   - Depends on external cookbooks (memcached, redisio)
   - Contains hardcoded credentials that need to be migrated to Ansible Vault

3. **fastapi-tutorial** (Priority 3)
   - Application deployment can follow infrastructure setup
   - Contains database setup that depends on PostgreSQL being installed

### Assumptions

1. The target environment will continue to be Fedora 42 as specified in the Vagrantfile
2. Self-signed certificates are acceptable for the migrated solution (production would likely require Let's Encrypt or other CA)
3. The current security configurations (fail2ban, UFW, SSH hardening) are required in the migrated solution
4. The FastAPI application source will continue to be pulled from the same Git repository
5. The directory structure for document roots (/opt/server/test, etc.) should be maintained
6. Redis and Memcached configurations (ports, memory allocation) should match current settings
7. The PostgreSQL database name, user, and credentials should remain the same
8. The systemd service configuration for the FastAPI application should be preserved