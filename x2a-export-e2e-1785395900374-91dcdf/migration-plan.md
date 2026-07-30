# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server setup with FastAPI application deployment and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- Well-structured Chef cookbooks with clear separation of concerns
- Standard web server, application, and caching configurations
- Some security considerations that need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and SSL certificate management
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW, sysctl security settings

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database setup
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef configuration file with run list and node attributes
- `solo.rb`: Chef configuration file with file paths and logging settings
- `Vagrantfile`: Defines development VM for testing with Fedora 42
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible `nginx` role or use the `ansible.builtin.package` module to install Nginx directly
- **memcached (~> 6.0)**: Replace with Ansible `geerlingguy.memcached` role or create a custom Memcached role
- **redisio (~> 7.2.4)**: Replace with Ansible `geerlingguy.redis` role or create a custom Redis role

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated in the Chef cookbook
  - Migration approach: Use Ansible's `openssl_*` modules or `community.crypto` collection for certificate generation
  - Consider integrating with Let's Encrypt for production environments

- **Firewall Configuration**: 
  - UFW is configured in the Chef cookbook
  - Migration approach: Use Ansible's `ufw` module or `ansible.posix.firewalld` for Fedora

- **Fail2ban Setup**:
  - Configured in the Chef cookbook for intrusion prevention
  - Migration approach: Create an Ansible role for fail2ban configuration

- **SSH Hardening**:
  - Root login disabled and password authentication disabled
  - Migration approach: Use Ansible's `lineinfile` module or `ansible-hardening` role

- **Vault/secrets management**:
  - Redis password is hardcoded in the Chef recipe
  - PostgreSQL credentials are hardcoded in the FastAPI recipe
  - Migration approach: Use Ansible Vault for storing sensitive credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Preserving the dynamic nature of the multi-site setup
  - Mitigation: Use Ansible templates with loops to generate site configurations

- **SSL Certificate Generation**: 
  - Challenge: Ensuring certificates are only generated when needed
  - Mitigation: Use Ansible's `stat` module to check for existing certificates before generation

- **Database Initialization**: 
  - Challenge: Ensuring idempotent database creation and user setup
  - Mitigation: Use Ansible's PostgreSQL modules with appropriate `when` conditions

- **Service Dependencies**: 
  - Challenge: Maintaining proper service startup order
  - Mitigation: Use Ansible handlers and meta dependencies between roles

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add SSL certificate management
   - Add security hardening features

2. **cache** (Priority 2)
   - Standalone services that other components may depend on
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on database and potentially caching
   - Implement PostgreSQL setup
   - Implement Python environment and application deployment
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora-based systems, with potential support for Ubuntu and CentOS as indicated in the cookbook metadata.
2. The self-signed SSL certificates approach is acceptable for the migrated solution, though production environments might benefit from Let's Encrypt integration.
3. The current security settings (fail2ban, UFW, SSH hardening) are appropriate and should be maintained in the Ansible implementation.
4. The Redis and PostgreSQL passwords in the current implementation are for development purposes and will be replaced with more secure values stored in Ansible Vault.
5. The FastAPI application repository URL will remain accessible during and after migration.
6. The Vagrant development environment will be maintained but converted to use Ansible provisioning instead of Chef.
7. No changes to the application architecture or deployment strategy are required as part of this migration.