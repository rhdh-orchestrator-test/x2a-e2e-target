# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated complexity is moderate, with an estimated timeline of 2-3 weeks for a complete migration.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificate generation
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup, security hardening (fail2ban, UFW firewall), systemd service management

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication, Memcached configuration, service management

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database setup
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment, Git repository deployment, PostgreSQL database configuration, systemd service creation

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `Vagrantfile`: Defines a Fedora 42 VM for local development and testing
- `solo.json`: Chef configuration file with run list and node attributes
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development/testing

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks

### Security Considerations

- **SSL/TLS Management**: 
  - Self-signed certificate generation for development environments
  - Certificate and private key storage paths need to be maintained
  - Migration approach: Use Ansible's openssl_* modules

- **Firewall Configuration**: 
  - UFW firewall rules for HTTP, HTTPS, and SSH
  - Migration approach: Use Ansible's community.general.ufw module

- **Fail2ban Setup**: 
  - Protection against brute force attacks
  - Migration approach: Use Ansible's community.general.fail2ban module

- **SSH Hardening**: 
  - Root login disabled
  - Password authentication disabled
  - Migration approach: Use Ansible's template module with sshd_config template

- **Vault/secrets management**:
  - Redis password in cache cookbook (plaintext in recipe)
  - PostgreSQL database credentials in fastapi-tutorial cookbook (plaintext in recipe)
  - Count: 2 plaintext credentials detected

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - The current implementation uses Chef templates and attributes to configure multiple virtual hosts
  - Mitigation: Create Ansible templates that replicate the same functionality, using host_vars or group_vars for site-specific configuration

- **Service Dependencies**: 
  - FastAPI application depends on PostgreSQL service
  - Mitigation: Use Ansible handlers and meta dependencies to ensure proper service ordering

- **Self-signed Certificate Generation**: 
  - Current implementation generates certificates on-the-fly
  - Mitigation: Use Ansible's openssl_* modules to generate certificates when needed

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation and configuration
   - Add SSL/TLS certificate generation
   - Implement security hardening (fail2ban, UFW)
   - Configure virtual hosts

2. **cache** (low complexity, standalone service)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure service management

3. **fastapi-tutorial** (high complexity, application deployment)
   - Set up PostgreSQL database
   - Deploy Python application from Git
   - Configure virtual environment and dependencies
   - Create systemd service

### Assumptions

1. The target environment will continue to be Fedora-based systems (the Vagrantfile specifies Fedora 42)
2. Self-signed certificates are acceptable for development environments
3. The same security hardening measures (fail2ban, UFW, SSH hardening) are required in the Ansible implementation
4. The FastAPI application source code will continue to be pulled from the same Git repository
5. The PostgreSQL database structure and user permissions will remain the same
6. Redis will continue to require password authentication
7. The Nginx virtual host configuration will maintain the same domain names and document roots
8. The current plaintext secrets in the Chef recipes will need to be secured using Ansible Vault in the migrated solution