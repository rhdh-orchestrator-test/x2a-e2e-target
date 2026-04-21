# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The complexity is moderate, with security configurations, SSL certificate management, and database integration requiring careful attention.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and fail2ban/ufw firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, firewall configuration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef configuration file containing the run list and node attributes
- `solo.rb`: Chef configuration file specifying cookbook paths and log settings
- `Vagrantfile`: Defines the development VM configuration using Fedora 42
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or local development

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or collection (e.g., `ansible.posix.nginx`)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., `geerlingguy.memcached`)
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role (e.g., `geerlingguy.redis`)

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Ansible migration should:
  - Maintain the same certificate generation logic
  - Consider integration with Let's Encrypt for production environments
  - Ensure proper permissions on private keys

- **Firewall Configuration**: The current implementation uses ufw. Ansible migration should:
  - Use `ansible.posix.firewalld` for Fedora/RHEL systems
  - Maintain the same port allowances (SSH, HTTP, HTTPS)

- **Fail2ban Integration**: Implement using Ansible modules or community roles

- **Security Headers**: Ensure Nginx security headers are preserved in the Ansible templates

- **Vault/secrets management**: 
  - Redis password in plaintext in the cache cookbook
  - PostgreSQL credentials in plaintext in the fastapi-tutorial cookbook
  - Consider using Ansible Vault for these secrets

### Technical Challenges

- **Multi-site Configuration**: The dynamic generation of multiple Nginx sites will require careful templating in Ansible
  - Solution: Use Ansible's with_items/loop constructs with templates

- **SSL Certificate Generation**: Self-signed certificate generation logic needs to be replicated
  - Solution: Use the `openssl_certificate` module in Ansible

- **Database Configuration**: PostgreSQL setup with user and database creation
  - Solution: Use the `postgresql_*` modules in Ansible

- **Service Dependencies**: Ensuring proper ordering of service installation and configuration
  - Solution: Use Ansible's handlers and meta dependencies between roles

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security configurations that should be established first

2. **cache** (Priority 2)
   - Moderate complexity with Redis and Memcached configuration
   - Depends on proper network configuration from nginx-multisite

3. **fastapi-tutorial** (Priority 3)
   - Most complex with database, application deployment, and service configuration
   - Depends on both web server and potentially cache services

### Assumptions

1. The target environment will continue to be Fedora-based systems
2. Self-signed certificates are acceptable for the migrated environment
3. The same security policies should be maintained in the Ansible implementation
4. The directory structure for web content will remain the same
5. No changes to the application code or database schema are required
6. The Redis and PostgreSQL passwords in the current implementation are placeholders and will be replaced with proper secrets management
7. The Vagrant development environment will be maintained but provisioned with Ansible instead of Chef