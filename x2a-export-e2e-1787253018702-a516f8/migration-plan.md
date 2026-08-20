# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated complexity is moderate, with an estimated timeline of 2-3 weeks for a complete migration, including testing and documentation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall), custom Nginx configuration

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, service management

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef configuration file containing the run list and node attributes
- `solo.rb`: Chef Solo configuration file specifying paths and logging settings
- `Vagrantfile`: Vagrant configuration for local development/testing using Fedora 42
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used for development in Vagrant
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation and configuration tasks

### Security Considerations

- **SSL/TLS Management**: 
  - Self-signed certificates are generated for development
  - Migration should maintain the same certificate generation or integrate with Ansible's crypto modules
  - Consider implementing Let's Encrypt support via Ansible community.crypto collection

- **Firewall Configuration**: 
  - UFW firewall is configured in security.rb
  - Migrate to Ansible's ufw module or firewalld for RHEL-based systems

- **Fail2ban Integration**:
  - Configured in security.rb
  - Migrate to Ansible's fail2ban_jail module

- **SSH Hardening**:
  - Root login disabled
  - Password authentication disabled
  - Migrate to Ansible's template module for sshd_config or use community.general.ssh_config module

- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook
  - Migrate to Ansible Vault for secure credential storage

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - The current implementation uses Chef templates and attributes
  - Ansible equivalent will need to use templates and variables with similar structure
  - Challenge: Maintaining the dynamic site generation based on configuration

- **SSL Certificate Generation**:
  - Current implementation uses inline shell commands
  - Ansible has built-in modules for certificate management
  - Challenge: Ensuring proper permissions and security for private keys

- **Service Dependencies**:
  - FastAPI application depends on PostgreSQL
  - Nginx sites depend on the FastAPI application
  - Challenge: Maintaining proper ordering and dependencies in Ansible

- **Configuration Templating**:
  - Multiple configuration templates need to be converted
  - Challenge: Ensuring all variables are properly mapped from Chef to Ansible

### Migration Order

1. **cache** (Priority 1 - Low complexity)
   - Simple service installation and configuration
   - Few dependencies
   - Good starting point for the migration

2. **nginx-multisite** (Priority 2 - Moderate complexity)
   - Core infrastructure component
   - Multiple configuration files and templates
   - Security configurations

3. **fastapi-tutorial** (Priority 3 - Moderate complexity)
   - Application deployment
   - Database integration
   - Depends on proper functioning of other components

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based systems
2. The same security requirements will apply in the new Ansible implementation
3. Self-signed certificates are acceptable for development, but production may require proper certificates
4. The FastAPI application source will remain available at the same Git repository
5. The multi-site configuration pattern will be maintained
6. Redis and Memcached will continue to be used as caching solutions
7. PostgreSQL will continue to be the database for the FastAPI application