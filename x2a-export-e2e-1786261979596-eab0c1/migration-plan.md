# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 2-3 weeks, with moderate complexity due to the SSL configuration, security hardening, and application deployment requirements.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: SSL certificate generation, fail2ban integration, UFW firewall configuration, multiple virtual hosts

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database setup
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment, PostgreSQL database creation, systemd service configuration

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef node configuration with run list and attribute overrides
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Vagrant configuration for local development using Fedora 42
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible `nginx` role or use the `ansible.builtin.package` module directly
- **memcached (~> 6.0)**: Replace with Ansible `memcached` role or use the `ansible.builtin.package` module with templates
- **redisio (~> 7.2.4)**: Replace with Ansible `redis` role or use the `ansible.builtin.package` module with templates

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for development
  - Migration should maintain the same certificate paths and permissions
  - Consider integrating with Ansible's `community.crypto.openssl_*` modules

- **Firewall Configuration**: 
  - UFW firewall rules need to be migrated to Ansible's `community.general.ufw` module
  - Maintain the same allowed ports (SSH, HTTP, HTTPS)

- **Fail2ban Integration**: 
  - Convert fail2ban configuration to use Ansible's `community.general.fail2ban` module
  - Maintain the same jail configurations

- **SSH Hardening**: 
  - Disable root login and password authentication
  - Use Ansible's `ansible.posix.sshd_config` module

- **Vault/secrets management**:
  - Redis password in cache cookbook: 1 hardcoded password
  - PostgreSQL database credentials in fastapi-tutorial cookbook: 2 hardcoded passwords
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - The current setup uses Chef templates and attributes to configure multiple virtual hosts
  - Ansible will need to use templates with similar variable structures
  - Challenge: Maintaining the same flexibility for site configuration

- **SSL Certificate Generation**: 
  - Self-signed certificates are generated with specific attributes
  - Challenge: Ensuring proper permissions and ownership in Ansible

- **Application Deployment**: 
  - The FastAPI application is deployed from Git with specific environment configuration
  - Challenge: Ensuring idempotent deployment with proper service management

- **Redis Configuration Hack**: 
  - The current setup includes a Ruby block to modify Redis configuration
  - Challenge: Implementing an equivalent solution in Ansible

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation
   - Add SSL certificate generation
   - Configure virtual hosts
   - Implement security hardening

2. **cache** (moderate complexity, standalone service)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper service management

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Implement PostgreSQL installation and configuration
   - Set up Python environment and dependencies
   - Deploy application from Git
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora 42 or a compatible Linux distribution
2. The same directory structure for web content will be maintained
3. Self-signed certificates are acceptable for the migrated solution
4. The same security hardening measures are required in the Ansible version
5. The FastAPI application source repository will remain available at the same URL
6. The PostgreSQL database structure and user permissions will remain the same
7. The Redis and Memcached configurations will maintain the same settings
8. The Vagrant development environment will be replaced with an Ansible-compatible alternative